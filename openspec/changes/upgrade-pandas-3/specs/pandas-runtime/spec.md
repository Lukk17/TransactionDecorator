## ADDED Requirements

### Requirement: Pandas major version pin

The project SHALL pin a single, exact pandas version in `pyproject.toml` `[project] dependencies`. The pinned version MUST be in the 3.0.x series.

#### Scenario: Project metadata declares the pin

- **WHEN** a contributor reads `pyproject.toml`
- **THEN** the `dependencies` array contains an entry of the form `pandas==3.0.<patch>` with no version range or wildcard

#### Scenario: Fresh install reproduces the pin

- **WHEN** a contributor runs `pip install -e .` against the project
- **THEN** `pip show pandas` reports the same exact version recorded in `pyproject.toml`

### Requirement: Copy-on-Write is the assumed memory model

All DataFrame mutation in `src/processor/` SHALL be safe under pandas 3 Copy-on-Write semantics. Code MUST NOT use chained assignment (`df[col][i] = value`) — under CoW it silently no-ops without raising. The only sanctioned write API is `df.loc[i, col] = value`.

#### Scenario: Row-level assignment via `.loc` mutates the owning DataFrame

- **WHEN** the categorize or label loop executes `df.loc[i, COL] = value` on the DataFrame returned by `pd.read_csv`
- **THEN** the value persists when the same DataFrame is later written via `df.to_csv`

#### Scenario: Boolean-mask filtering returns an independent DataFrame under CoW

- **WHEN** the importer applies an ignore rule via `df = df[~condition]`
- **THEN** subsequent operations on the filtered DataFrame produce the same output as on pandas 2.x with CoW enabled, and writes to the filtered slice do NOT propagate back to the parent

#### Scenario: Chained assignment is rejected at code-review time

- **WHEN** a code change introduces `df[col][i] = value` in `src/`
- **THEN** the reviewer rejects the change and recommends `df.loc[i, col] = value` instead

### Requirement: String columns default to the `str` dtype

The project SHALL accept that `pd.read_csv` returns string columns as the native `str` dtype (`StringDtype(storage='python', na_value=nan)`) under pandas 3, NOT as `object`. All dtype-checking code MUST use `pd.api.types.is_string_dtype()` (which covers both `str` and `object`) rather than direct comparison to `'object'`.

#### Scenario: Whitespace cleanup applies to both `str` and `object` columns

- **WHEN** `replace_multiple_whitespaces(df)` runs
- **THEN** it processes columns where `is_string_dtype()` returns True, regardless of whether the underlying dtype is `str` or `object`

#### Scenario: Round-trip CSV preserves `str` dtype

- **WHEN** a DataFrame with `str`-dtype columns is written via `to_csv` and re-read via `read_csv`
- **THEN** the reloaded DataFrame has identical `str` dtypes for those columns

### Requirement: Single-shot `pd.concat` in the importer

The importer SHALL build new rows as a Python list of dicts and concatenate them in a single `pd.concat([original, pd.DataFrame(new_rows)])` call. Per-row concatenation inside a loop is FORBIDDEN.

#### Scenario: Importer batches new rows

- **WHEN** `process_imported_csv` processes N input rows
- **THEN** exactly one `pd.concat` call merges them into the original ledger

#### Scenario: Per-row concat is rejected at code-review time

- **WHEN** a code change introduces `pd.concat(...)` inside a `for` loop
- **THEN** the reviewer rejects the change

### Requirement: Integration tests run dtype-strict

The integration test suite SHALL invoke `pd.testing.assert_frame_equal` without `check_dtype=False`, so any unintended dtype regression (for example, an unexpected switch to `object` after a future refactor) surfaces as a failing test.

#### Scenario: Decorator round-trip matches fixture dtype-for-dtype

- **WHEN** `tests/transaction_decorator_test.py::test_process_imported_csv` runs against a fixture
- **THEN** the comparison passes only if both column values AND column dtypes match the expected fixture

### Requirement: No cross-major-version fixture regeneration

The project SHALL NOT regenerate CSV test fixtures using a different pandas major version than the one currently pinned in `pyproject.toml`. Fixture regeneration MUST be done atomically with the pin bump in the same change.

#### Scenario: Fixture regenerated under stale pandas

- **WHEN** a contributor regenerates `tests/decorator/expected/*.csv` using pandas 2.x
- **AND** the project is pinned to pandas 3.0.x
- **THEN** the change is rejected at code-review time

### Requirement: Architecture decision documented

An ADR SHALL exist under `docs/architecture/decisions/` documenting (a) the pandas 3 + Copy-on-Write contract, (b) the NumPy 2 transitive dependency, (c) the deliberate decision to retain row-by-row `.loc` mutation in the categorize/label loops, (d) the new `str` dtype default for `pd.read_csv` string columns, (e) the single-shot `pd.concat` contract, and (f) the no-chained-assignment rule.

#### Scenario: ADR is registered in the architecture index

- **WHEN** a contributor opens `docs/architecture/index.md`
- **THEN** the table of decisions includes a row for the pandas 3 / CoW ADR with status "Accepted"
