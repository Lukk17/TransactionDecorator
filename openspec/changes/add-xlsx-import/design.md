## Context

Today the importer is CSV-only. From `transactions_importer.py::process_imported_csv`:

```python
imported_csv = _read_imported_csv(
    imported_csv_file_name, delimiter, import_encoding, rows_to_skip, header_fix)
```

That helper calls `pd.read_csv` either directly or after splicing a header-fix line via `io.StringIO`. Everything downstream — `_apply_ignore_rules`, `assign_imported_values_to_new_row`, `pd.concat` — operates on a generic DataFrame and doesn't care how it was loaded.

For xlsx, pandas provides `pd.read_excel(file, engine='openpyxl')` which returns the same DataFrame shape. So the change is mechanical: branch at the read step, route xlsx through `read_excel`, leave everything else alone.

The complication is that xlsx files don't have a delimiter or encoding. The current `create_input_dialog` modal asks the user to pick the delimiter (`;` or `,`) and the decimal-separator format. For xlsx:
- No delimiter to pick (Excel cells are pre-parsed)
- Decimal separator question still applies — pandas may load amount columns as floats already, but if the user wants comma-decimal output, the `convert_decimal_separator` downstream step still applies

So we need to keep the decimal-separator question and skip the delimiter question for xlsx files.

## Goals / Non-Goals

**Goals:**

- Users can import `.xlsx` files without converting to CSV first.
- The new branch is small enough to audit in one PR (~15 LOC).
- Single-section xlsx files (one header at top, transactions below) work identically to CSV equivalents.
- The integration test suite gains at least one xlsx fixture proving the new path.

**Non-Goals:**

- Multi-section xlsx (multi-account or multi-currency consolidated workbooks) — out of scope; would need a dedicated adapter proposal if a user demands it later.
- `.xls` (legacy Excel binary format from 2003 and earlier). Pandas can read it via `xlrd` engine, but that's a separately-pinned legacy dep that almost nobody hits in 2026. Skip.
- Writing xlsx output. We only read user input as xlsx; the project's working `allTransactions.csv` stays CSV.
- Auto-detecting xlsx format quirks (multi-section, dual-currency amounts, etc.). The simple-format contract is explicit.

## Decisions

### Decision 1: Branch in `_read_imported_csv`, not at the top of `process_imported_csv`

**Choice:** Add the extension check inside `_read_imported_csv` so the branch is contained.

**Alternatives considered:**

- Branch at the top of `process_imported_csv` — would skip `find_start_row` / `header_fix` logic for xlsx (which is correct since xlsx has no header artifacts), but spreads xlsx awareness across the function.
- Have a separate `_read_imported_xlsx` function called from a separate `process_imported_xlsx`. Doubles the orchestration code.

**Rationale:** Containment. The "how is the bytes turned into a DataFrame" decision lives in one place. Header-fix and skiprows are CSV-specific and naturally short-circuit when the input is xlsx (no header artifacts in well-formed Excel).

### Decision 2: Pin `openpyxl` exactly

**Choice:** `openpyxl==<latest stable>` in `[project] dependencies` (alongside chardet, pandas, PySide6).

**Alternatives considered:**

- Range pin like `openpyxl>=3.1`. Inconsistent with the rest of `pyproject.toml`.
- Optional dep under `[project.optional-dependencies] xlsx`. Means users who don't `pip install transaction-decorator[xlsx]` get a confusing ImportError on first xlsx attempt. Better to bundle.

**Rationale:** Exact pin matches existing convention. xlsx is a core feature once it ships, not an opt-in extra.

### Decision 3: GUI file picker accepts both via single dialog

**Choice:** Update the `QFileDialog` filter to `"Bank Exports (*.csv *.xlsx *.xlsm);;CSV Files (*.csv);;Excel Files (*.xlsx *.xlsm)"`.

**Alternatives considered:** Two separate import buttons (Import CSV / Import Excel). Doubles GUI surface, confuses users.

**Rationale:** One button, one dialog, both formats accepted. Standard UX pattern.

### Decision 4: Skip delimiter dialog for xlsx, keep decimal-separator dialog

**Choice:** In `import_csv`, after the file picker, check the extension. If xlsx, show only the decimal-separator checkbox (no delimiter dropdown).

**Alternatives considered:** Show the delimiter dropdown and ignore the user's choice for xlsx. Confusing — user sees a control that has no effect.

**Rationale:** Clean UX. Decimal separator question still meaningful since the user picks output formatting.

### Decision 5: Test fixture is a hand-authored xlsx mirror of an existing CSV fixture

**Choice:** Create `tests/import/sample-single-section.xlsx` by hand (using openpyxl in a one-shot setup script committed under `tests/import/_fixtures_setup.py` if needed, OR by exporting an existing CSV fixture to xlsx). The xlsx fixture mirrors the structure of `tests/import/importerTestData.csv` but in xlsx packaging. The expected output is identical to the CSV path.

**Alternatives considered:**

- Reuse a complex multi-section xlsx as the fixture. **Rejected** — multi-section formats won't parse with the simple branch this proposal adds; using one as a fixture would force this proposal to grow.

**Rationale:** Test the new branch in isolation. Adapters for non-trivial xlsx layouts are separate concerns.

## Risks / Trade-offs

- **[Risk] openpyxl has had occasional breaking changes between major versions.** → Mitigation: exact pin; version bumps go through the dependency-bump verification recipe in `docs/testing-strategy.md`.
- **[Risk] xlsx files can be enormous (multi-MB) and slow to parse on first import.** → Mitigation: existing user expectations for "Run Processing" already accommodate seconds-long waits; the new `ProcessingWorker` keeps the GUI responsive (already in place from `upgrade-pandas-3`).
- **[Risk] User picks an xlsx with a weird shape (multiple sheets, merged cells, header in row 5).** → Mitigation: explicit single-section contract documented; weird shapes get a "could not find header" error from `find_start_row`-equivalent logic. We can add a dedicated adapter later if a specific bank's format becomes a recurring user need.
- **[Risk] The decimal-separator dialog logic for xlsx vs CSV diverges in subtle ways.** → Mitigation: unit-test `import_csv` for both paths (xlsx skips delimiter; CSV asks for both). Already partially covered by `test_import_csv_*` in `tests/unit/test_widget_assembler.py`; extend.
- **[Trade-off] Bundle size grows by ~3–5 MB.** Acceptable; not a project constraint.
- **[Trade-off] Two distinct read code paths to maintain.** Mitigated by Decision 1 (containment).

## Migration Plan

1. Add `openpyxl` pin to `pyproject.toml`.
2. Modify `_read_imported_csv` to branch on extension.
3. Modify `import_csv` GUI wrapper to expand file picker filter and skip delimiter dialog for xlsx.
4. Add xlsx fixture and parametrized integration test.
5. Update `docs/importing.md` with the new accepted format and the "Recommended export format" table.
6. Run full pytest suite under `-W error`.
7. Manual smoke: import a real xlsx (e.g., one of the simple bank exports if available).
8. After merge, the multi-section xlsx case is unblocked for a future dedicated adapter proposal if/when needed.

**Rollback:** Revert the `pyproject.toml` pin and the source changes. Existing CSV users unaffected. The xlsx fixture and test stay (will then SkipIf-mark or be removed).

## Open Questions

- Should the file picker remember the last-used format and pre-select it next time? Out of scope; track separately.
- Should xlsx files trigger a different default "Force categories update" / "Force labels update" state? No — that's orthogonal to file format.
- `.xls` (binary, pre-2007) support? Skipping. If a user complains, file separately as `add-xls-legacy-import`.
