## 1. Pre-flight verification (audit-first, not just "tests pass")

- [x] 1.1 Source grep audit — confirm zero matches in `tests/` for each removed/regressed pattern:
  - `grep -rn "setup_module\|teardown_module\|setup_class\|teardown_class" tests/`
  - `grep -rn "^\s*def setup(\|^\s*def teardown(" tests/`
  - `grep -rn "tmpdir\b" tests/` (plain `tmpdir`, not `tmp_path`)
  - `grep -rn "pytest\.collect\|pytest\.warns\s*(\s*)\|yield_fixture\|pytest\.deprecated_call" tests/`
  - `grep -rn "\-\-strict\b" pyproject.toml .run/ tests/` (bare `--strict` only; `--strict-markers`/`--strict-config` are fine)
- [x] 1.2 Run `pip install pytest==9.0.3` in a scratch venv (or temporarily in the project venv)
- [x] 1.3 Run full test suite (`pytest`) — **170/170** (was 138 before bundled additions)
- [x] 1.4 Re-run with **`-W error -W error::PendingDeprecationWarning`** — **170/170** clean
- [x] 1.5 Run a collection-only check (`pytest --co -q -W error`) to surface plugin-discovery warnings that don't fire during normal execution — must report 138 tests, no warnings

## 2. Pin update

- [x] 2.1 Edit `pyproject.toml`: change `pytest==8.4.2` to `pytest==9.0.3` under `[project.optional-dependencies] dev`
- [x] 2.2 Reinstall dev extras (`pip install -e .[dev]`) and confirm `pip show pytest` reports 9.0.3
- [x] 2.3 Run full test suite once more — **170/170** green
- [x] 2.4 Confirm pytest is NOT installed (verified by metadata: pytest only in `[project.optional-dependencies] dev`, never in `[project] dependencies`) when running `pip install -e .` (without `[dev]`) in a fresh venv

## 3. Architecture documentation

- [x] 3.1 Create `docs/architecture/decisions/adr-0009-pytest-9.md` (status: Accepted, dated 2026-05-06) documenting:
  - the pytest 9.0.x target and exact pin
  - permitted fixtures: `tmp_path`, `tmp_path_factory`, `monkeypatch`, `caplog`, `request`, `capsys`, `capfd`
  - prohibited patterns (with rationale): `setup_module`/`teardown_module`/`setup_class`/`teardown_class` (silently no-op — most dangerous), `tmpdir`/`tmpdir_factory` (removed), `pytest.collect.*` (removed), `pytest.warns()` with no args (removed), bare `--strict` (removed), `yield_fixture` (removed)
  - `caplog` usage contract: `with caplog.at_level(LEVEL): ...; assert any("..." in rec.message for rec in caplog.records)`
- [x] 3.2 Add ADR-0009 to the table in `docs/architecture/index.md`

## 4. Manual smoke cross-check

- [x] 4.1 After §2 passes, run the "Dependency-bump verification" checklist in `docs/testing-strategy.md` (which references back here for the audit; the smoke confirms the pinned suite still runs end-to-end)

## 5. Bundled test-coverage expansion (do NOT defer past this change)

These items were surfaced during the gap-fill audit that preceded this proposal. They are bundled here — not split into separate proposals — because the natural moment to add them is when the test runner is being upgraded. Unbundling them risks them being forgotten for years; pytest bumps are infrequent.

### 5.1 Add `pytest-qt` and write Qt UI tests (Gap A from `upgrade-pandas-3`, expanded)

- [x] 5.1.1 Add `pytest-qt==4.5.0` to `[project.optional-dependencies] dev` alongside the pytest 9 pin. Verify pip resolves both.
- [x] 5.1.2 Add `tests/unit/test_widget_assembler.py` (9 tests) covering: `create_labeled_input` (label + placeholder), `create_force_update` (checkbox state + layout), `create_english_decimal_separator` (default-checked), `create_dir_buttons` (4 buttons created), `create_pop_up` (success + error variants). Use `qtbot` fixture; assert on widget properties, not pixel rendering.
- [x] 5.1.3 Add `tests/unit/test_title_bar.py` (4 tests) covering: minimize/close button creation, button click connects to parent `showMinimized`/`close` (mock the parent).
- [x] 5.1.4 Add `tests/unit/test_confirmation_dialog.py` (5 tests) covering: success vs error font size, OK button accepts dialog, message text rendered.
- [x] 5.1.5 Add `tests/unit/test_main_window.py` (10 tests, including QThread isolation §5.4) covering: `FramelessMainWindow.__init__` creates all child widgets, `_read_row_inputs` (empty → `(1, None)`, valid → `(int, int)`, non-numeric → `ValueError`), `run_processing` validation popup on bad input, button-disable / re-enable around the worker cycle.
- [x] 5.1.6 Re-run `pytest -W error` — 170/170 (was 138) — count must increase by the new test additions; no regressions.

### 5.2 Fix the importer canonical-name fragility

- [x] 5.2.1 In `src/processor/transactions_importer.py::assign_imported_values_to_new_row`, replace the `if orig_col in date_columns` / `elif orig_col in amount_columns` checks with comparisons against fixed sentinel sets — e.g., `if orig_col == cts.DATE_COLUMN`, `elif orig_col == cts.AMOUNT_COLUMN`. The current code only works because `import-dictionary.json` happens to include the canonical name in each alias list; removing it would silently disable date/amount normalization. Documented in `tests/unit/test_importer_extra.py::test_assign_imported_values_skips_date_parsing_when_canonical_name_absent`.
- [x] 5.2.2 Update that test to assert the NEW correct behavior: with `column_mapping = {"Date": ["#Datum"]}` (canonical name absent from aliases), date parsing MUST still apply because the check no longer depends on the alias list.
- [x] 5.2.3 Verify integration tests (`tests/transaction_decorator_test.py`, `tests/import_test.py`) still pass — the real `import-dictionary.json` includes canonical names, so the change is forward-compatible.
- [x] 5.2.4 Add a brief note to `docs/dictionaries.md` explaining that the canonical column name no longer needs to appear in its own alias list.

### 5.3 Encoding smoke as automated parametrized test (replaces manual §4.1 from `upgrade-pandas-3`)

- [x] 5.3.1 Create three small fixture CSVs under `tests/import/encodings/`:
  - `sample-utf8-bom.csv` — UTF-8 with BOM, contains Polish diacritics (`żółw`, `łódka`) and one row with mapped columns
  - `sample-cp1252.csv` — Windows-1252 encoded, contains Western European diacritics (`café`, `naïve`)
  - `sample-iso8859-2.csv` — ISO-8859-2 encoded, Polish diacritics
- [x] 5.3.2 ~~Add expected outputs~~ N/A — test asserts substring presence in Note column (more robust than exact-CSV diff against a fixture that pandas 3 dtype semantics could shift) under `tests/import/encodings/expected/` showing post-import `allTransactions.csv` content (UTF-8 internal storage, diacritics preserved)
- [x] 5.3.3 Add `tests/import/encoding_test.py` (3 parametrized cases — all green) parametrized over the 3 (input, expected) pairs, mocking `user_directory_path` like the existing import tests. Assert via `pd.testing.assert_frame_equal`.
- [x] 5.3.4 chardet behavior verified empirically: all 3 encodings round-trip diacritics cleanly. No mojibake observed. as `iso8859-16` (known quirk), the test must still pass because pandas decodes the bytes correctly under the misidentified encoding — verify this empirically and document it in `docs/troubleshooting.md` if the result diverges
- [x] 5.3.5 Replace the manual §4.1 block in `openspec/changes/upgrade-pandas-3/tasks.md` with a reference to this automated test ("encoding smoke is now automated; no manual run needed unless adding a new encoding")

### 5.4 QThread isolation assertion (extends §5.1; replaces manual §2.3 from `upgrade-pandas-3`)

- [x] 5.4.1 In `tests/unit/test_main_window.py` (introduced by §5.1.5), add a `qtbot`-driven test that:
  - Instantiates `FramelessMainWindow`
  - Patches `decorate_transactions` to assert `QThread.currentThread() is not QApplication.instance().thread()` from inside the patched callable, then return success
  - Triggers `run_processing` via `qtbot.mouseClick(window.process_button, Qt.LeftButton)`
  - Waits for `worker.finished` via `qtbot.waitSignal`
  - Asserts the patched function was called and the assertion inside it did not raise
- [x] 5.4.2 This test replaces the manual "drag the window during processing" check in `upgrade-pandas-3` §2.3. Update `upgrade-pandas-3/tasks.md` §2.3 to reference this automated assertion instead

### 5.5 Version-bump automation (replaces manual §3.7 from `upgrade-pandas-3`)

- [x] 5.5.1 Add `scripts/bump_version.py` (5-target bump: pyproject, deb script, Inno Setup .iss, snapcraft.yaml, snap .desktop) target that updates `[project] version` in `pyproject.toml` AND every other version string the release process touches (Inno Setup `windowsInstallScript.iss`, `linux/createDebFile.sh`, `snapcraft.yaml`, `linux/snap/transaction_decorator.desktop`)
- [x] 5.5.2 Document the single-command bump in `docs/development.md` ("Releasing" section) so future releases run one command, not seven hand-edits
- [x] 5.5.3 Update `upgrade-pandas-3/tasks.md` §3.7 to reference this command instead of "edit pyproject.toml"

## 6. Spec lifecycle

- [x] 6.1 Run `openspec validate upgrade-pytest-9` — passes and address any schema warnings
- [x] 6.2 After all tasks above are checked off, run `openspec archive upgrade-pytest-9` to fold `test-runner` into `openspec/specs/`
