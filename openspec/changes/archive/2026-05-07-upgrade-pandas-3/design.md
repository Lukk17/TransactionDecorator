## Context

The app uses pandas in two hot paths:

- `src/processor/transactions_decorator.py` — reads `allTransactions.csv`, does row-by-row mutation via `df.loc[i, COL] = value` inside `update_categories` and `update_labels`, applies `replace_multiple_whitespaces`, sorts by date, and writes back.
- `src/processor/transactions_importer.py` — reads bank-export CSVs, applies ignore rules via boolean masking and slicing (`df = df[~condition]`), builds a list of dict rows, and concatenates with the existing ledger via a single `pd.concat([original, pd.DataFrame(new_rows)])`.

Test coverage: 13 integration tests fixture-compare full CSV round-trips via `pd.testing.assert_frame_equal`; 46 unit tests cover helper functions including `replace_multiple_whitespaces`, `sort_dataframe_by_date`, and `normalize_string`.

Current pin: `pandas==2.3.3`. Latest stable: `pandas==3.0.2`.

## Audit methodology

This proposal is grounded in two layers of empirical evidence, not just "the test suite passes":

1. **Source grep** for every known pandas 3 removal/regression pattern (results in the per-pattern table below).
2. **Targeted runtime probes** with pandas 3.0.2 installed, run under `-W error` (every warning category as an error). Each probe exercises one specific risk surface that the existing test suite does not cover (empty-CSV concat, str-vs-object `assert_frame_equal`, chained assignment, CoW slice behavior, etc.).

Both layers ran clean. The full pytest suite (59/59) passed under `pandas==3.0.2 + pytest==9.0.3` with `-W error`.

## Pandas 3 risk audit — per-pattern findings

| # | Pattern | Where it would bite us | Audit outcome |
| --- | --- | --- | --- |
| 1 | `inplace=True` (deprecated more aggressively in 3.x) | `transactions_decorator.py`, `transactions_importer.py` | grep: 0 matches in `src/`. ✅ |
| 2 | `DataFrame.append`, `Series.append` (removed) | importer's row-by-row build, decorator's label accumulation | grep: 0 matches. We use `pd.concat` (importer) and Python list `.append` (decorator). ✅ |
| 3 | Removed `read_csv` args (`mangle_dupe_cols`, `error_bad_lines`, `warn_bad_lines`, `delim_whitespace`, `squeeze`, `prefix`, `date_parser`, `infer_datetime_format`) | importer + decorator both call `pd.read_csv` | grep: 0 matches. We use only `delimiter`, `encoding`, `quotechar`, `skiprows`, `index_col`. ✅ |
| 4 | Chained assignment `df[col][row] = x` (silently no-ops under CoW; warns) | both processors mutate cells | grep `df\[[^\]]+\]\[`: 0 matches. All mutations use `df.loc[i, col] = ...`. ✅ Probe (Test 12): chained assignment emits warning AND silently fails — we are not exposed but future code must avoid this. |
| 5 | CoW changes view→parent mutation semantics | `_apply_ignore_rules` does `df = df[~condition]`, then iterates | We never write back to the filtered slice and expect the parent to update. Probe (Test 5) confirms the new semantics; our flow is unaffected. ✅ |
| 6 | New default `str` dtype for read_csv string columns (NOT `string[pyarrow]` as some tutorials suggest — actual dtype is `StringDtype(storage='python', na_value=nan)`) | every dtype check, every `.astype('object')`, every `assert_frame_equal` | Probe (Tests 0, 6, 17, 18): string columns return `str` dtype. `is_string_dtype()` covers both `str` and `object`, so `replace_multiple_whitespaces` works. Round-trip CSV preserves `str`. ✅ |
| 7 | `df[col].dtype != 'object'` comparison flips meaning | `initialize_labels_column` elif branch | Under pandas 3 the elif now triggers on every read because dtype is `str` not `object`. Result: `.astype('object')` runs as a no-op-ish cast. **Behavior unchanged, but the branch is misleading.** Captured as a known wrinkle in ADR-0008; cleanup is opportunistic, not blocking. ⚠️ |
| 8 | `assert_frame_equal` is dtype-strict and distinguishes `str` vs `object` | all 13 integration fixtures | Probe (Test 11): strict comparison fails between `str` and `object` columns. Our tests are safe because both sides go through `pd.read_csv` in the same pandas-3 process and both return `str`. Risk only materializes if a fixture is regenerated under pandas 2 and compared under pandas 3 — which our tasks explicitly forbid (no fixture regeneration as part of this change). ⚠️ |
| 9 | Empty (headers-only) CSV concat with non-empty new rows | `process_imported_csv` first-import path: `original_csv` empty, `new_rows` populated | Probe (Tests 13, 14): empty CSV reads with `object` dtype; new rows are `str` dtype; `pd.concat` produces `object` dtype output without any warning. Functionally identical to pandas 2. ✅ |
| 10 | `pd.to_datetime(dayfirst=True)` format inference (warns/raises in 3.x edge cases) | `sort_dataframe_by_date` | Probe (Test 3): works clean on our actual fixtures. No warning. ✅ |
| 11 | `Series.bool()`, `df.applymap` → `df.map` rename, `convert_dtypes` quirks | nowhere | grep: 0 matches. ✅ |
| 12 | `pd.set_option` deprecated keys (e.g., `mode.copy_on_write`) | tests use display options | grep: only `pd.set_option('display.*', ...)` — display options are stable. ✅ Probe: setting `mode.copy_on_write` raises `Pandas4Warning` (already deprecated for pandas 4); we don't set it. |
| 13 | NumPy ABI bump | every numeric path | **Corrected by probe**: pandas 3.0.2 declares `numpy>=1.26.0` (NOT `>=2`). Probe-install confirms `numpy==1.26.4` stays in place. So no ABI break today. PySide6 6.11 and chardet 7.4 have no NumPy linkage. ✅ A future pandas 3.x patch may force NumPy 2 — that becomes a separate bump. |
| 14 | `pd.Series(dtype='object')` length-mismatch broadcast (`initialize_labels_column` if-branch) | only when `LABELS_COLUMN` missing — not exercised by current tests because fixtures all include the column | Probe (Test 1): broadcasts to NaN-filled column of length N, dtype `object`. Works under pandas 3. ✅ |
| 15 | `iterrows()` performance/dtype-coercion behavior change | `process_imported_csv` row build | We use `iterrows()` only to materialize a list of plain dicts (no dtype-sensitive ops on the row Series itself). No behavior change. ✅ |
| 16 | `dt.strftime` returns `str` dtype now (was `object`) | `sort_dataframe_by_date` writes back | Probe (Test 10): `dt.strftime` returns `str` dtype. Subsequent `to_csv` writes the same characters. ✅ |
| 17 | `pd.concat` with all-NA / empty FutureWarning (now removed) | first-import path | Probe (Test 14): no warning, no error. ✅ |
| 18 | Strict alignment when assigning short Series to wide DataFrame column | `initialize_labels_column` if-branch | Probe (Test 1): pandas 3 still broadcasts (no `IndexError`). ✅ |

Empirical summary: of 18 distinct risk patterns audited, 16 are clean, 2 are wrinkles — both already known and captured in mitigations below.

## Goals / Non-Goals

**Goals:**

- Move to pandas 3.0.x with zero runtime regressions.
- Codify Copy-on-Write as the assumed memory model so future contributors don't introduce 2.x-style chained-assignment patterns.
- Pin a specific 3.0.x patch to keep the build reproducible.
- Document the new default `str` dtype and the dtype-strict `assert_frame_equal` contract.

**Non-Goals:**

- Adopting arrow-backed string columns explicitly (`dtype_backend="pyarrow"` in `read_csv`). Defer until there is a measured perf or correctness reason.
- Refactoring the row-by-row `df.loc` loops into vectorised form. They work under CoW; vectorisation is a separate maintenance concern.
- Cleaning up `initialize_labels_column` (the elif branch becomes a no-op-ish cast under pandas 3). Not blocking; track as a separate cleanup.
- Re-pinning all transitive dependencies. NumPy 2 will be pulled in transitively; we do not need a direct NumPy pin today.
- Regenerating any test fixture under pandas 3. Doing so would create cross-version dtype hazards (see risk #8 in the audit table).

## Decisions

### Decision 1: Pin to `pandas==3.0.2` (exact)

**Choice:** `pandas==3.0.2`.

**Alternatives considered:**

- `pandas>=3.0,<4` — looser, but our other deps are exact-pinned. Mixing styles makes builds non-reproducible.
- `pandas==2.3.3` (status quo) — defers the work but doesn't avoid it; pandas 2.x is in maintenance.
- `pandas==3.0.0` — earliest 3.0; 3.0.2 has post-release bugfixes with no behavior change.

**Rationale:** Exact pin matches the project convention. 3.0.2 is the latest stable patch as of 2026-05-06.

### Decision 2: No source changes; document via ADR-0008

**Choice:** Add `docs/architecture/decisions/adr-0008-pandas-3-cow.md` recording: (a) CoW is the assumed model; (b) the project deliberately keeps row-by-row `.loc` mutation in the categorize/label loops; (c) `df.loc[]` is the only sanctioned write API (chained assignment now silently no-ops); (d) the `str` dtype now default for string columns; (e) the `initialize_labels_column` elif branch is a known no-op-ish cast under pandas 3 — leave it alone for now.

**Alternatives considered:**

- Refactor `.loc[i, COL] = value` to vectorised form. Cleaner but expands scope; no functional benefit today.
- Skip the ADR. Loses institutional memory.
- Clean up `initialize_labels_column` as part of this change. Adds risk; do separately.

**Rationale:** ADR is cheap and prevents the next reviewer from "fixing" non-broken patterns or re-introducing chained assignment.

### Decision 3: Keep `assert_frame_equal` calls dtype-strict

**Choice:** Do not add `check_dtype=False` to integration test assertions.

**Rationale:** Probe (Test 11) shows `str` vs `object` is detected by strict comparison. Adding `check_dtype=False` would mask a real regression class. Our fixtures are safe because both sides of the comparison go through `pd.read_csv` in the same pandas-3 process. The mitigation that protects us is "do not regenerate fixtures during this change" — explicit in the tasks.

### Decision 4: Reaffirm the single-shot `pd.concat` pattern

**Choice:** No code change. The importer already builds a list and does one `pd.concat` (fixed during the previous review pass). Pandas 3 deprecates per-row concat patterns more aggressively, so reverting would now warn loudly. ADR-0008 captures this so future contributors don't "optimize" by re-introducing per-row concat.

## Coverage gaps the audit cannot reach (and how we mitigate them)

The grep + `-W error` probes cover known risk classes. They do NOT cover four runtime surfaces:

### Gap A — GUI / `QThread` worker path

`decorate_transactions` runs on a `QThread` (`ProcessingWorker`) when invoked from the GUI. The automated test suite invokes it directly from the main thread. Pandas itself is not GIL-thread-safe, but our pattern guarantees no concurrent access: only one worker runs at a time (the Process button is disabled until the worker emits `finished`), and no DataFrame crosses the thread boundary (the worker constructs its own via `pd.read_csv` and returns only `(bool, str)` via the `finished` signal).

**Mitigation, encoded in tasks:**

1. Manual smoke step in `docs/testing-strategy.md` step 12: trigger Run Processing, then drag the window during processing and confirm the GUI stays responsive (proves the worker is on a different thread; proves pandas 3 did not regress that wrapper).
2. If the manual smoke ever fails, add a unit test that invokes `ProcessingWorker.run()` directly (no `QThread`) to isolate worker logic from Qt threading. Not done preemptively because the wrapper is 12 lines and trivially auditable.

### Gap B — Frozen Windows / Linux deb / Linux snap runtime

PyInstaller and snapcraft hooks bundle pandas differently than dev mode. Hidden imports, optional submodules (e.g., `pandas.compat.pickle_compat`), and runtime data files can be missed by the bundler.

**Mitigation, encoded in tasks:**

1. The packaging-verification block (`tasks.md` §4) requires installing each artifact on a clean host and running the full golden-path smoke from `docs/testing-strategy.md`. NOT optional.
2. Each binary's startup must log the bundled `pandas.__version__` and `numpy.__version__`. If they don't match the pin, the artifact is rejected.
3. Specifically for Inno Setup: rerun `pyinstaller --clean` (not incremental) so stale `_internal/` caches don't ship.
4. Specifically for snap: install with `--dangerous --classic` on a clean snap host (not local rebuild) so confined-filesystem regressions surface.

### Gap C — NumPy ABI

Confirmed by probe: pandas 3.0.2 keeps NumPy 1.26.4. No ABI shift today. **However**, if a future pandas 3.x bump tightens to `numpy>=2`, every C-extension dep (only `numpy` itself in our tree; `chardet`/`PySide6` are pure Python or Qt-only) needs a NumPy-2 wheel.

**Mitigation, encoded in tasks:**

1. Task §1 includes `pip show pandas numpy` to record the actual versions installed during the probe.
2. If the install message mentions "Uninstalling numpy-1.x" or "Installing numpy-2.x", treat it as a separate change scope: file a follow-up proposal `upgrade-numpy-2` rather than bundle silently.
3. Pin `numpy<2` defensively in `pyproject.toml` if a future patch changes this (out of scope today; documented as an open question).

### Gap D — `chardet` encoding edge cases on real bank CSVs

Independent of pandas 3, but called out here because the migration smoke is the natural moment to retest. Probe shows `chardet` misidentifies CP1252 and ISO-8859-2 as `iso8859-16` on small files. Pandas reads with the wrong encoding will silently substitute wrong characters for accented Polish/German letters (mojibake). This is an existing limitation, NOT introduced by pandas 3.

**Mitigation, encoded in tasks AND existing docs:**

1. `docs/testing-strategy.md` "Encoding smoke" section requires testing import on the encodings the user actually expects (UTF-8-with-BOM, CP1252, ISO-8859-2). Workaround documented: pre-convert to UTF-8-with-BOM.
2. `docs/troubleshooting.md` documents the mojibake symptom and the BOM workaround so users hit it self-serve.
3. No change to `detect_encoding` in scope of this proposal — it would be a separate behavior change.

## Risks / Trade-offs

- **[Risk] User-installed snap / deb / Windows builds break on first auto-update because the bundled wheel cache is stale.** → Mitigation: bump the package version, do a clean rebuild for all three artifacts on a clean host, install from scratch in a sandbox before publishing.
- **[Risk] PyInstaller binary grows due to pandas 3 (NumPy unchanged from 1.26).** → Mitigation: accept; binary size is not a project constraint.
- **[Risk] A future bank export contains a column whose pandas-3 dtype inference differs from pandas-2 (e.g., a numeric-looking string column inferred as int).** → Mitigation: `is_string_dtype()` already used in `replace_multiple_whitespaces`. If `assert_frame_equal` ever fails on dtype after a real-world import, regenerate the affected fixture **and** document the dtype shift in ADR-0008.
- **[Risk] `initialize_labels_column` elif branch runs every time on pandas 3 (cosmetic; harmless cast).** → Mitigation: documented in ADR-0008. Cleanup tracked separately; not blocking.
- **[Risk] PyInstaller hook for pandas 3 lags the release.** → Mitigation: verified `pyinstaller==6.20.0` ships current pandas hooks; pin both together in `[project.optional-dependencies] dev`.
- **[Risk] A future contributor introduces chained assignment `df[col][i] = x`.** → Mitigation: ADR-0008 explicitly forbids; reviewer rejects at PR time. Probe (Test 12) shows pandas 3 emits a warning, but the warning category is `ChainedAssignmentError` only when CoW is enabled in 2.x — under 3.x it is a `Warning` that is suppressed by default. CI does not gate on it. Explicit code-review rule is the only durable defense.
- **[Risk] A future contributor regenerates a CSV fixture under pandas 3 → other contributors with stale-cache pandas 2 venvs see test failures.** → Mitigation: ADR-0008 + tasks both call this out. Bumping the lockfile is the contract.
- **[Risk] `dt.strftime` now returns `str` dtype (was `object`); a downstream consumer relying on `object` would break.** → Mitigation: only consumer is `to_csv` which accepts both. ✅

## Migration Plan

1. **Probe (done)** — `pip install pandas==3.0.2`; full test suite under `-W error` (every warning category) passes. Targeted probes covering 18 risk patterns all clean (see audit table above).
2. **Pin** — update `pyproject.toml` `[project] dependencies` to `pandas==3.0.2`.
3. **ADR** — add ADR-0008 capturing the CoW assumption, `str` dtype default, single-shot `pd.concat` requirement, no chained assignment, and the harmless `initialize_labels_column` wrinkle.
4. **Index** — register ADR-0008 in `docs/architecture/index.md`.
5. **Smoke test** — manual: launch `python src/gui.py`, run one Import + one Run Processing cycle on a known CSV; confirm output matches a pre-bump round-trip on the same input (binary diff).
6. **Rebuild artifacts** — Windows installer (Inno Setup) + Linux deb + snap, with the new wheel set. Defer to release cycle.

**Rollback strategy:** Revert the `pyproject.toml` pin to `pandas==2.3.3` and reinstall. No data migration needed since CSV output is unchanged. Any artifact built on pandas 3 keeps working under user data; downgrading the source venv only affects CI and dev.

## Open Questions

- Should we adopt `dtype_backend="pyarrow"` opportunistically in `pd.read_csv` for memory wins on large user ledgers? Out of scope; track separately if a user reports memory issues.
- Should the snap/deb packagers also pin NumPy directly to guard against unexpected upstream NumPy major bumps? Likely yes in a follow-up; not blocking.
- Should `initialize_labels_column` be cleaned up (drop the elif since pandas 3 always returns `str` for string columns from `read_csv`)? Yes, but as a separate change so the diff stays scoped.
