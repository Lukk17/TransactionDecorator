## 1. Pre-flight verification (audit-first, not just "tests pass")

- [ ] 1.1 Source grep audit — confirm zero matches for each removed/regressed pattern:
  - `grep -rn "inplace=True\|\.append(\|mangle_dupe_cols\|error_bad_lines\|warn_bad_lines\|delim_whitespace\|infer_datetime_format\|applymap\|\.bool()\|date_parser\|squeeze" src/`
  - `grep -rn "df\[[^]]*\]\[" src/` (chained assignment — must be empty)
  - `grep -rn "pd\.set_option" src/` (display-only is fine; flag any `mode.copy_on_write` set)
- [ ] 1.2 Run `pip install pandas==3.0.2` in a scratch venv (or temporarily in the project venv) and confirm `python -c "import pandas as pd; print(pd.options.mode.copy_on_write)"` reports `True`
- [ ] 1.3 Capture the actual installed NumPy version: `pip show pandas numpy | grep -E "^Name|^Version"`. Record both. If the install output shows `Uninstalling numpy-1.x` or `Installing numpy-2.x`, STOP — file a separate `upgrade-numpy-2` proposal first; do not bundle the NumPy ABI bump silently.
- [ ] 1.4 Run full test suite (`pytest`) — must show 59/59 passing
- [ ] 1.5 Re-run with **`-W error`** (every warning category as an error, not just `DeprecationWarning`/`FutureWarning`) — must still show 59/59 passing
- [ ] 1.6 Run targeted runtime probes (one Python `-W error` invocation each) covering:
  - empty (headers-only) CSV concat with new rows
  - `pd.Series(dtype='object')` length-mismatch broadcast (the missing-`Labels`-column branch)
  - `pd.to_datetime(dayfirst=True)` on the actual fixture date strings
  - `is_string_dtype` over the new `str` dtype
  - CoW slice semantics (`df = df[~cond]; df.loc[...] = ...`)
  - `assert_frame_equal` between `str` and `object` dtypes (must FAIL — confirms strict-mode is detecting the difference)

## 2. GUI / `QThread` worker verification (Gap A)

- [ ] 2.1 Launch `python src/gui.py` against the new pandas pin
- [ ] 2.2 Perform one Import + one Run Processing cycle following the golden-path in `docs/testing-strategy.md`
- [ ] 2.3 During Run Processing, **drag the window** to a new position. The window MUST stay responsive while processing (proves the worker is on a separate thread; proves pandas 3 did not regress the wrapper)
- [ ] 2.4 Binary-diff the output `csv/allTransactions.csv` against a pre-upgrade run on the same input — must be byte-identical
- [ ] 2.5 If 2.3 or 2.4 fails: add a unit test that invokes `ProcessingWorker.run()` directly (not via `QThread`) to bisect whether the regression is in the worker logic or in Qt threading

## 3. Packaging verification (Gap B — must run before each release)

- [ ] 3.1 Add a one-line startup log to `src/gui.py` that prints `pandas.__version__` and `numpy.__version__` at app boot. (Already partially present via `logger.info("platform=...")`; extend to include dep versions.)
- [ ] 3.2 Rebuild the Windows installer with **`pyinstaller --clean`** (NOT incremental — stale `_internal/` caches can hide hidden-import regressions). Install on a clean Windows user account or VM
- [ ] 3.3 Launch from the Start menu; check the startup log shows pandas 3.0.2 and the recorded NumPy version
- [ ] 3.4 Run the full golden-path smoke from `docs/testing-strategy.md` against the installed binary. NOT against the dev venv
- [ ] 3.5 Rebuild Linux `.deb`; install on a clean Debian/Ubuntu container; run the golden-path smoke
- [ ] 3.6 Rebuild snap; install with `sudo snap install --dangerous --classic` on a clean snap host (NOT the build host); run the golden-path smoke. Specifically verify user data lands under `~/snap/transaction-decorator/current/` and the app can read/write there under confinement
- [ ] 3.7 Bump app version (`pyproject.toml [project] version`) to 1.1.0 to signal the dependency major bump

## 4. Encoding edge cases (Gap D — once per migration; carries over from earlier scope)

- [ ] 4.1 Run the **Encoding smoke** section of `docs/testing-strategy.md`: import sample CSVs encoded as UTF-8-with-BOM, CP1252, and ISO-8859-2. Verify Polish/German diacritics round-trip correctly in `csv/allTransactions.csv`
- [ ] 4.2 If any encoding produces mojibake: confirm the workaround documented in `docs/troubleshooting.md` ("re-save as UTF-8 with BOM") still works against pandas 3
- [ ] 4.3 No `detect_encoding` source change in scope. If the migration surfaces a real regression, file a separate change

## 5. Pin update (only after §1–§4 pass)

- [ ] 5.1 Edit `pyproject.toml`: change `pandas==2.3.3` to `pandas==3.0.2` in `[project] dependencies`
- [ ] 5.2 Reinstall the project (`pip install -e .[dev]`) and confirm `pip show pandas` reports 3.0.2 and `pip show numpy` matches what §1.3 recorded
- [ ] 5.3 Run full test suite once more — must remain 59/59 green
- [ ] 5.4 **Do NOT regenerate any test fixture** as part of this change. Regenerating under pandas 3 would create a cross-version dtype hazard. Fixture regeneration is a separate, explicit change.

## 6. Architecture documentation

- [ ] 6.1 Create `docs/architecture/decisions/adr-0008-pandas-3-cow.md` (status: Accepted, dated 2026-05-06) documenting:
  - the pandas 3 + CoW contract (NumPy unchanged at 1.26 today; track for future bumps)
  - the new `str` dtype default for `pd.read_csv` string columns (and that it is `StringDtype(storage='python', na_value=nan)`, not `string[pyarrow]`)
  - `df.loc[i, COL] = value` as the only sanctioned mutation API (chained assignment silently no-ops)
  - the single-shot `pd.concat([original, pd.DataFrame(new_rows)])` contract for the importer (do not revert to per-row concat)
  - the harmless `initialize_labels_column` elif wrinkle (cleanup tracked separately)
  - the explicit "do not regenerate fixtures across pandas major versions" rule
  - reference `docs/testing-strategy.md` for manual smoke and packaged-binary verification procedure
- [ ] 6.2 Add ADR-0008 to the table in `docs/architecture/index.md`

## 7. Spec lifecycle

- [ ] 7.1 Run `openspec validate upgrade-pandas-3` and address any schema warnings
- [ ] 7.2 After all tasks above are checked off, run `openspec archive upgrade-pandas-3` to fold `pandas-runtime` into `openspec/specs/`
