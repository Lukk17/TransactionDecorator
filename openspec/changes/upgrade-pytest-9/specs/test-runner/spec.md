## ADDED Requirements

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

The project SHALL NOT add a pytest plugin (e.g., `pytest-cov`, `pytest-xdist`, `pytest-mock`) to `[project.optional-dependencies] dev` without a corresponding ADR explaining the need and pinning a compatible plugin version.

#### Scenario: A contributor adds pytest-cov

- **WHEN** a PR adds `pytest-cov==<version>` to `[project.optional-dependencies] dev`
- **THEN** the reviewer requires either a new ADR documenting the coverage workflow or rejects the change

### Requirement: Architecture decision documented

An ADR SHALL exist under `docs/architecture/decisions/` documenting (a) the pytest 9.0.x target, (b) the permitted fixture/hook allowlist, (c) the prohibited patterns denylist with rationale, and (d) the `caplog` usage contract.

#### Scenario: ADR is registered in the architecture index

- **WHEN** a contributor opens `docs/architecture/index.md`
- **THEN** the table of decisions includes a row for the pytest 9 ADR with status "Accepted"
