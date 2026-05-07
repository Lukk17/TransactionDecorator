# test-runner Specification

## Purpose
TBD - created by archiving change upgrade-pytest-9. Update Purpose after archive.
## Requirements
### Requirement: Pytest major version pin

The project SHALL pin a single, exact pytest version under `[project.optional-dependencies] dev` in `pyproject.toml`. The pinned version MUST be in the 9.0.x series.

#### Scenario: Project metadata declares the pin

- **WHEN** a contributor reads `pyproject.toml`
- **THEN** the `[project.optional-dependencies] dev` array contains an entry of the form `pytest==9.0.<patch>` with no version range or wildcard

#### Scenario: Pytest is not in the user-facing dependencies

- **WHEN** a user installs the project without dev extras (`pip install transaction-decorator`)
- **THEN** pytest is NOT pulled in as a transitive dependency

### Requirement: Permitted fixtures and hooks

Test modules SHALL use only the pytest APIs that remain supported in 9.x. The permitted set is:

- Built-in fixtures: `tmp_path`, `tmp_path_factory`, `monkeypatch`, `caplog`, `request`, `capsys`, `capfd`.
- Markers: `@pytest.mark.parametrize`, `@pytest.mark.skip`, `@pytest.mark.skipif`, `@pytest.mark.xfail`.
- Hooks: `pytest_collection_modifyitems`, `pytest_configure`, plain `conftest.py` fixtures via `@pytest.fixture`.
- xunit-style at class scope only: `setup_method`, `teardown_method`.

#### Scenario: Test suite uses only permitted patterns

- **WHEN** a contributor runs `grep -rn "tmpdir\|pytest\.collect\|pytest\.warns\s*(\s*)\|yield_fixture" tests/`
- **THEN** zero matches are returned

### Requirement: Prohibited patterns

Test modules SHALL NOT use any of the patterns removed in pytest 9. The denylist with rationale:

- `setup_module` / `teardown_module` / `setup_class` / `teardown_class` / module-level `def setup()` / `def teardown()` — pytest 9 silently does NOT call these (no error). Use fixtures or `setup_method`/`teardown_method` instead.
- `tmpdir` / `tmpdir_factory` — legacy `py.path.local` fixtures removed. Use `tmp_path` / `tmp_path_factory`.
- The bare `--strict` CLI flag — removed. Use `--strict-markers` and/or `--strict-config`.
- `pytest.collect.*` — namespace removed.
- `pytest.warns()` with no expected warning category — must specify a class.
- `pytest.yield_fixture` — removed. Use `@pytest.fixture` with `yield`.

#### Scenario: A contributor adds a `setup_module` to a test file

- **WHEN** a code change introduces `def setup_module(module): ...` at module scope in `tests/`
- **THEN** the reviewer rejects the change because pytest 9 will silently skip it without warning, producing a test that passes but is missing setup

#### Scenario: A contributor uses `tmpdir`

- **WHEN** a code change introduces `def test_foo(tmpdir): ...` in `tests/`
- **THEN** the reviewer rejects the change in favor of `tmp_path`

#### Scenario: tmp_path used for filesystem isolation

- **WHEN** a unit test needs an isolated working directory (e.g., `tests/unit/test_find_start_row.py`)
- **THEN** the test takes `tmp_path` (or `tmp_path_factory`) as a fixture parameter, never `tmpdir`

### Requirement: caplog usage contract

Tests that assert on logger output SHALL use `caplog.records[i].message` (not `getMessage()`-only) inside a `with caplog.at_level(<LEVEL>):` block. Bare `caplog.text` substring checks are permitted but discouraged in favor of structured record iteration.

#### Scenario: A test asserts a logger warning was emitted

- **WHEN** a test wants to verify that `normalize_number_format` warned on an unrecognized input
- **THEN** the test uses `with caplog.at_level("WARNING"):` followed by `assert any("..." in rec.message for rec in caplog.records)`

### Requirement: No pytest plugins without explicit ADR

The project SHALL NOT add a pytest plugin (e.g., `pytest-cov`, `pytest-xdist`) to `[project.optional-dependencies] dev` without a corresponding ADR explaining the need and pinning a compatible plugin version. **`pytest-qt` is the one explicitly approved exception**, added in this change to enable Qt UI testing — see Requirement "Qt UI test coverage via pytest-qt" below.

#### Scenario: A contributor adds pytest-cov

- **WHEN** a PR adds `pytest-cov==<version>` to `[project.optional-dependencies] dev`
- **THEN** the reviewer requires either a new ADR documenting the coverage workflow or rejects the change

### Requirement: Qt UI test coverage via pytest-qt

The project SHALL include `pytest-qt` in `[project.optional-dependencies] dev`, pinned to a version compatible with the active pytest 9.0.x pin. Test modules under `tests/unit/` SHALL cover the Qt UI surface that pure-Python tests cannot reach:

- `gui_elements/widget_assembler.py` — every public `create_*` helper.
- `gui_elements/title_bar.py` — minimize/close button creation and click wiring.
- `gui_elements/confirmation_dialog.py` — success vs error rendering, OK button behavior.
- `gui.FramelessMainWindow` — construction, `_read_row_inputs` (empty / valid / non-numeric branches), `run_processing` validation popup on bad input.

#### Scenario: pytest-qt is pinned alongside pytest

- **WHEN** a contributor reads `pyproject.toml`
- **THEN** `[project.optional-dependencies] dev` contains both `pytest==9.0.<patch>` and `pytest-qt==<compat>`

#### Scenario: Qt widgets have unit tests

- **WHEN** a contributor runs `ls tests/unit/test_widget_assembler.py tests/unit/test_title_bar.py tests/unit/test_confirmation_dialog.py tests/unit/test_main_window.py`
- **THEN** all four files exist and contain at least one `qtbot`-based test each

#### Scenario: `_read_row_inputs` validation is unit tested

- **WHEN** a unit test in `tests/unit/test_main_window.py` invokes `FramelessMainWindow._read_row_inputs` with empty, valid, and non-numeric inputs
- **THEN** the empty case returns `(1, None)`, the valid case returns the integer pair, and the non-numeric case raises `ValueError`

### Requirement: Encoding edge cases covered by automated test

The integration test suite SHALL include a parametrized test that imports CSVs encoded as UTF-8-with-BOM, Windows-1252, and ISO-8859-2, and verifies diacritics round-trip correctly into `allTransactions.csv`. This replaces the manual encoding smoke step in `docs/testing-strategy.md`.

#### Scenario: All three encodings import without manual intervention

- **WHEN** `pytest tests/import/encoding_test.py` runs
- **THEN** all three (encoding, fixture) parametrized cases pass without any manual file conversion

### Requirement: Worker thread isolation asserted in test, not visually verified

The Qt UI test suite SHALL include a test that asserts `decorate_transactions` runs on a thread distinct from the main GUI thread when triggered via `FramelessMainWindow.run_processing`. This replaces the manual "drag the window during processing" check.

#### Scenario: Processing runs off the main thread

- **WHEN** a test in `tests/unit/test_main_window.py` triggers `run_processing` and patches `decorate_transactions` to record the calling thread
- **THEN** the recorded thread is not `QApplication.instance().thread()`

### Requirement: Version bump is a single command

The project SHALL provide a single command (Makefile target or `scripts/bump-version.py`) that updates the version string everywhere the release process touches it. Hand-editing multiple files is FORBIDDEN.

#### Scenario: Bumping to 1.1.0 propagates everywhere

- **WHEN** the release engineer runs `make bump-version VERSION=1.1.0` (or the equivalent script)
- **THEN** `pyproject.toml`, `windows/installer/windowsInstallScript.iss`, `linux/createDebFile.sh`, `snapcraft.yaml`, and `linux/snap/transaction_decorator.desktop` ALL reflect 1.1.0 in one commit

### Requirement: Importer date/amount routing uses constant comparison

`src/processor/transactions_importer.py::assign_imported_values_to_new_row` SHALL determine whether to apply `parse_date` or `normalize_number_format` by comparing the canonical column name against constants (`cts.DATE_COLUMN`, `cts.AMOUNT_COLUMN`), NOT by checking membership in the alias list from `import-dictionary.json`.

The previous implementation accidentally worked only because the real dictionary always included the canonical name in each alias list. A user-edited dictionary that omitted the canonical name would silently lose date and amount normalization.

#### Scenario: Date parsing applies even when alias list omits the canonical name

- **WHEN** `assign_imported_values_to_new_row` runs with `column_mapping = {"Date": ["#Datum"]}` (no `"Date"` in the alias list)
- **AND** an imported row contains a parseable date string
- **THEN** the resulting row's `Date` field is reformatted to `cts.OUTPUT_DATE_FORMAT`, NOT passed through raw

#### Scenario: Amount normalization applies even when alias list omits the canonical name

- **WHEN** `assign_imported_values_to_new_row` runs with `column_mapping = {"Amount": ["Betrag"]}` (no `"Amount"` in the alias list)
- **AND** an imported row contains a European-formatted number (e.g., `"1.234,56"`)
- **THEN** the resulting row's `Amount` field is normalized per the current `dot_decimal_separator` setting

### Requirement: Architecture decision documented

An ADR SHALL exist under `docs/architecture/decisions/` documenting (a) the pytest 9.0.x target, (b) the permitted fixture/hook allowlist, (c) the prohibited patterns denylist with rationale, and (d) the `caplog` usage contract.

#### Scenario: ADR is registered in the architecture index

- **WHEN** a contributor opens `docs/architecture/index.md`
- **THEN** the table of decisions includes a row for the pytest 9 ADR with status "Accepted"

