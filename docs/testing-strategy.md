# Testing strategy

This document describes how to verify the application works end-to-end. It complements the automated unit + integration tests under `tests/` with the manual checks that automation cannot reach: the live GUI, packaged binaries, and platform-specific runtime paths.

## What is automated vs manual

| Layer | Coverage | How |
| --- | --- | --- |
| Pure functions (`normalize_string`, `normalize_number_format`, `parse_date`, `find_start_row`, decorator helpers, path resolution) | High | `pytest tests/unit/` (46 tests) |
| Full CSV round-trip via `decorate_transactions` and `process_imported_csv` | High | `pytest tests/transaction_decorator_test.py tests/import_test.py` (13 tests, fixture-comparison) |
| GUI rendering, window dragging, dialogs | None | Manual smoke (this doc) |
| `ProcessingWorker` running on `QThread` | None | Manual smoke + targeted Worker invocation if needed |
| Frozen Windows / Linux deb / Linux snap runtime | None | Manual install-and-run on each target (this doc) |
| Real-world bank export encoding edge cases (CP1252, ISO-8859-2, etc.) | Partial — fixtures cover UTF-8 and a few European bank exports | Manual import of representative CSVs (this doc) |
| Snap confinement (env vars, sandboxed paths) | None | Manual install-from-snap and full cycle (this doc) |

## Quick reference — automated suite

From the project root (after `pip install -e .[dev]`):

```shell
pytest                          # all 59 tests, configured via pyproject.toml
pytest tests/unit/              # unit tests only
pytest -W error                 # treat any warning as a failure (catches dependency drift)
pytest -k "import"              # only tests with "import" in the name
pytest --co                     # collection-only, useful when bumping pytest
```

After bumping any pinned dependency, ALWAYS run `pytest -W error` (not just `pytest`) so newly-introduced deprecation warnings surface as test failures.

## Manual smoke — golden path (run on every release candidate)

Run on each platform you publish for. Each item is a **single concrete action** producing an observable outcome. If any step fails, do not ship the release.

### Setup

1. Use a clean copy of the user data directory (per-platform path documented in [project-structure.md](project-structure.md)). If you have prior data, back it up.
2. Place a known-good bank export CSV under a known location (e.g. `~/test-imports/sample-bank.csv`).
3. Note the SHA-256 of `csv/allTransactions.csv` BEFORE the run (or its absence).

### Smoke steps

1. **Launch the app.** Window appears, frameless, custom title bar visible.
2. **Drag the window** by the title bar to a different screen position. Window moves.
3. **Click "Open Dictionary Directory"** in the toolbar. The platform's file manager opens at `dictionary/`.
4. **Click "Open Backup Directory"**. File manager opens at `backup/`.
5. **Click "Open CSV Directory"**. File manager opens at `csv/`.
6. **Click "Import CSV"** → the file picker opens. Select your sample bank export.
7. The delimiter dialog opens. Pick the correct delimiter and confirm. The "English [.] decimal separator" checkbox is **checked by default**.
8. Wait for the success dialog. Click OK. The CSV directory opens automatically.
9. Open `csv/allTransactions.csv` in a spreadsheet tool. Verify:
   - The number of rows increased by the expected amount (matches input minus rows excluded by `ignore-dictionary.json`).
   - Dates are formatted `dd.mm.YYYY HH:MM`.
   - Amounts use the dot decimal separator (or comma, if you unchecked the box).
10. **Type `1` into "First Row"** and leave "Last Row" empty.
11. **Check "Force categories update"** and **"Force labels update"**.
12. **Click "Run Processing"**. The button greys out (worker thread is running). The window stays responsive — try dragging it during processing.
13. Wait for the success dialog. Click OK. The CSV directory opens automatically.
14. Open `backup/`. Verify a new `allTransactions.csv_<timestamp>.csv` file appeared with the timestamp matching the run.
15. Open `csv/allTransactions.csv` again. Verify:
    - Rows are sorted by `Date` descending (newest first).
    - Every row has a `Category` (rows that matched no dictionary rule should be `Other`, per [ADR-0005](architecture/decisions/adr-0005-force-update-other.md)).
    - `Labels` accumulate across multiple matches separated by commas.

### Edge-case smoke

Run these only when the relevant code path changed (for the routine release candidate, the golden path above is enough).

- **Empty `allTransactions.csv`** — delete `csv/allTransactions.csv` then run Import. The app must initialize a new CSV with the canonical headers and append the imported rows.
- **Missing `Labels` column** — manually edit `csv/allTransactions.csv` and remove the `Labels` column header. Run Processing with "Force labels update" off. The column should be re-added with derived label values.
- **Non-numeric input in row inputs** — type `abc` into "First Row". Click Run Processing. An error popup must appear ("First/Last Row must be integers."). The button must re-enable.
- **Cancel the import dialog** — click Cancel on the delimiter dialog. No change to `allTransactions.csv`.
- **Bad CSV (mismatched columns)** — point Import at a CSV with a row missing fields. The error dialog must surface a parse error rather than silently corrupting data.

### Encoding smoke (real-world bank exports)

`chardet` does not always identify European single-byte encodings precisely. Verify imports with the encodings you actually expect from your bank:

- **UTF-8 with BOM** — exports from many German/Polish online-banking portals.
- **Windows-1252 / CP1252** — common on older Windows-only banking exports.
- **ISO-8859-2** — Polish-language exports.

For each: import the file, then open `allTransactions.csv` in a tool that can show the actual bytes (`xxd csv/allTransactions.csv | head` or VS Code "Show byte order"). Verify Polish/diacritic characters round-trip correctly. If they do not, the encoding misdetection is a known limitation of `chardet` on small files; pre-convert the export to UTF-8 with BOM as a workaround.

## Dependency-bump verification

Whenever any pinned dependency in `pyproject.toml` changes:

1. **Strict-warning suite**: `pytest -W error` — must remain green. Any new warning is treated as a failure.
2. **Targeted source grep** for patterns the bumped dependency removed or behavior-changed. (See `openspec/changes/upgrade-pandas-3/tasks.md` and `upgrade-pytest-9/tasks.md` for the audit checklists used during the most recent bumps; reuse the pattern.)
3. **Smoke**: run the entire "Manual smoke — golden path" section on at least one platform.
4. **Packaged binary**: build the Windows installer (or Linux deb/snap) and run the same golden-path smoke against the packaged binary. Dev-mode tests do not catch PyInstaller-hook regressions.
5. **GUI thread + worker**: confirm by visually checking step 12 above (window stays responsive during processing). The worker runs `decorate_transactions` on a `QThread`; if the dependency bump changes thread-safety semantics, the GUI freezes during processing.

## Packaged binary verification

Per platform, after building the artifact:

### Windows

1. Install the `.exe` in a clean Windows user account (or VM).
2. Launch from the Start menu.
3. The app's startup log (visible in a console build, or via Event Viewer / log file otherwise) should print the bundled `pandas` and `numpy` versions matching the pin.
4. Run the golden-path smoke above.
5. Uninstall via Add/Remove Programs and verify `%APPDATA%\TransactionDecorator\` is preserved (user data should NOT be deleted on uninstall).

### Linux .deb

1. `sudo apt install ./build/transaction-decorator_<version>.deb` on a clean Debian/Ubuntu VM.
2. Run `transaction-decorator` from the terminal.
3. Run the golden-path smoke.
4. `sudo apt remove transaction-decorator` and verify `/usr/share/transaction-decorator/` (user data) is preserved.

### Linux snap

1. `sudo snap install --dangerous --classic ./linux/transaction-decorator_<version>_amd64.snap`.
2. Run `transaction-decorator` from the terminal.
3. Run the golden-path smoke.
4. Specifically verify that user data lives under `~/snap/transaction-decorator/current/` (per [ADR-0003](architecture/decisions/adr-0003-path-resolution.md)) and the app can read/write there under snap confinement.
5. `sudo snap remove transaction-decorator` — confirm user data behavior matches the snap conventions.

## Reporting

If a manual smoke step fails:

1. Capture the exact platform, app version, dependency versions (`pip show pandas pytest pyside6 chardet`), and any console output.
2. Attach the failing input CSV (with sensitive amounts redacted if needed).
3. File via the channel documented in `docs/troubleshooting.md`.
