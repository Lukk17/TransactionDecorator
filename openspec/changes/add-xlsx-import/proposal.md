## Why

Some banks export transaction histories only as `.xlsx`, with no CSV option on the user-visible export menu. The current importer is CSV-only, so users of those banks have to manually open the `.xlsx` in Excel/LibreOffice and "Save As → CSV UTF-8" before the app will accept it. That's a real-world papercut that filters into [docs/troubleshooting.md](../../../docs/troubleshooting.md) every few months.

Adding `.xlsx` import support is a small change because pandas already provides `pd.read_excel(file, engine='openpyxl')` returning the same DataFrame shape `pd.read_csv` does. The downstream pipeline (header detection, ignore rules, column mapping, `assign_imported_values_to_new_row`, `pd.concat` into the existing ledger) stays identical. The change reduces to a 15-line branch plus one new optional dependency.

This proposal explicitly handles the **simple, single-section xlsx** case — files that look like a CSV with `.xlsx` packaging (one header row at the top, transaction rows underneath). Multi-section workbook exports (multiple per-account or per-currency sub-sheets, summary rows, etc.) are explicitly out of scope; if a user needs such a format supported in the future, a dedicated adapter proposal would handle it.

## What Changes

- Add `openpyxl` to `[project] dependencies` in `pyproject.toml` (pandas needs it as the engine for `read_excel` on `.xlsx`).
- In `src/processor/transactions_importer.py::process_imported_csv`, branch on file extension: `.xlsx`/`.xlsm` → `pd.read_excel(..., engine='openpyxl')`; everything else (CSV) → unchanged path.
- The Qt file picker (`import_csv` GUI wrapper) already accepts arbitrary file types via `QFileDialog.getOpenFileName` — extend its `filter` argument from `"CSV Files (*.csv)"` to include `"Excel Files (*.xlsx *.xlsm)"`.
- The delimiter dialog (`create_input_dialog`) is irrelevant for xlsx (no delimiter to pick); skip it when the picked file is xlsx.
- **BREAKING for any future code**: the importer's input is no longer guaranteed to be a CSV. New code must respect that `process_imported_csv(file_name, ...)` may receive an `.xlsx`.
- Update integration tests under `tests/import/` to add at least one xlsx fixture exercising the new branch.
- Document the new accepted formats in `docs/importing.md` and update the "Recommended export format" table I sketched in earlier discussion.

## Capabilities

### New Capabilities

- `xlsx-import`: Defines the file-extension dispatch contract, the `openpyxl` engine pin, the GUI file-picker filter update, and the constraint that single-section xlsx files must follow the same shape as accepted CSV files (one header row at top, then rows).

### Modified Capabilities

(none — the existing CSV import behavior is preserved unchanged; xlsx is a new branch alongside it)

## Impact

- **Code**: ~15 lines in `process_imported_csv` (extension branch), ~5 lines in `import_csv` (file picker filter + skip delimiter dialog for xlsx). No changes to `transactions_decorator.py`, `utils.py`, or any other module.
- **New dep**: `openpyxl` (pinned). Adds ~3–5 MB to packaged binaries.
- **Tests**: 1 new fixture (e.g. `tests/import/sample-single-section.xlsx`) + 1 parametrized integration test asserting the xlsx path produces the same `allTransactions.csv` as an equivalent CSV would.
- **Docs**: `docs/importing.md` gets a new section. README install table footnote about supported formats.
- **No `Environment` enum changes**, no path-resolution changes, no impact on packaging tracks.
- **Costs**: zero monetary. The added dep is widely available across all our packaging targets (Inno Setup, deb, snap, flatpak future, macOS dmg future).
