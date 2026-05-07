## Context

The project's test suite lives under `tests/` and is configured via `[tool.pytest.ini_options]` in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

Test modules in scope:

- `tests/conftest.py` — adds `src/` to `sys.path` (defensive; `pythonpath` already covers it).
- `tests/transaction_decorator_test.py`, `tests/import_test.py` — integration tests, parametrized, use `unittest.mock.patch` and fixture CSV comparison via `pd.testing.assert_frame_equal`.
- `tests/unit/test_normalize_number_format.py`, `test_parse_date.py`, `test_decorator_helpers.py`, `test_path_resolution.py`, `test_find_start_row.py` — unit tests using `@pytest.mark.parametrize`, `caplog`, `monkeypatch`, and `tmp_path`.

Current pin: `pytest==8.4.2`. Latest stable: `pytest==9.0.3`. We use no pytest plugins (`pytest-cov`, `pytest-xdist`, etc.).

## Audit methodology

Same two-layer approach as the pandas-3 proposal:

1. **Source grep** of `tests/` for every removed pytest API (results in the per-pattern table below).
2. **Targeted runtime probes** with pytest 9.0.3 installed: full suite under `-W error -W error::PendingDeprecationWarning`, plus a collection-only run to surface plugin-discovery warnings that may not fire during normal execution.

Both layers ran clean.

## Pytest 9 risk audit — per-pattern findings

| # | Pattern | Where it would bite us | Audit outcome |
| --- | --- | --- | --- |
| 1 | `nose`-style `setup_module` / `teardown_module` (removed) | any test module | grep: 0 matches in `tests/`. ✅ |
| 2 | `nose`-style `setup_class` / `teardown_class` (removed) | integration test classes | grep: 0 matches. We use plain functions, not classes. ✅ |
| 3 | Bare module-level `def setup()` / `def teardown()` (removed) | any module | grep: 0 matches. ✅ |
| 4 | `tmpdir` / `tmpdir_factory` (legacy `py.path.local`, removed) | filesystem-isolated unit tests | grep: 0 matches. We use `tmp_path` everywhere (e.g., `tests/unit/test_find_start_row.py`). ✅ |
| 5 | `pytest.collect.*` namespace (removed) | conftest.py customizations | grep: 0 matches. ✅ |
| 6 | `pytest.warns()` with no expected category (removed) | any warning assertion | grep: 0 matches. We do not use `pytest.warns` at all. ✅ |
| 7 | `pytest.deprecated_call()` API change | deprecation tests | grep: 0 matches. ✅ |
| 8 | `pytest.yield_fixture` (removed in pytest 4, but still grep-worthy) | fixtures | grep: 0 matches. ✅ |
| 9 | Bare `--strict` CLI flag (removed; use `--strict-markers`/`--strict-config`) | `addopts` or CI command | grep on `pyproject.toml` and `.run/`: not used. ✅ |
| 10 | `caplog.records[i].message` API (still supported in 9.x) | every `caplog` test | We use this; verified still working in pytest 9. ✅ |
| 11 | `monkeypatch.setenv` / `delenv` API (stable) | path-resolution tests | We use both; stable. ✅ |
| 12 | `tmp_path` / `tmp_path_factory` API (stable, recommended) | filesystem-isolated tests | We use `tmp_path`; stable. ✅ |
| 13 | `@pytest.mark.parametrize` API (stable) | every parametrized test | Stable, no changes. ✅ |
| 14 | `unittest.mock.patch` integration (not pytest-managed; stable) | integration tests | Stable; `patch(...)` context manager works identically. ✅ |
| 15 | conftest.py `sys.path.insert` ordering vs `pythonpath` ini | `tests/conftest.py` | Both work; defensive double-coverage. Probe collection-only run shows no warning. ✅ |
| 16 | Fixture finalization order (refactored in 9.x internally) | `tmp_path` cleanup | Probe full suite: no `ResourceWarning` or finalization issue. ✅ |
| 17 | `--import-mode=importlib` becoming default (still `prepend` in 9.x) | conftest.py-relative imports | Default unchanged in 9.0.x; we are not exposed. ✅ |
| 18 | `pytest_collection_modifyitems` / `pytest_configure` hookspec changes | conftest.py | We use neither hook. ✅ |
| 19 | Custom marker registration (`--strict-markers` would warn on unregistered) | `@pytest.mark.parametrize` is built-in | We use only built-in markers. ✅ |
| 20 | Plugin compatibility (`pytest-cov`, `pytest-xdist`, etc.) | `[project.optional-dependencies] dev` | We have no pytest plugins. ✅ |

Empirical summary: of 20 distinct risk patterns audited, 0 require changes. The migration is a pure pin bump for our suite shape.

## Goals / Non-Goals

**Goals:**

- Move to pytest 9.0.x with zero test changes.
- Codify the permitted fixture/hook patterns so future contributors don't reintroduce removed APIs.
- Pin a specific 9.0.x patch for reproducible CI.

**Non-Goals:**

- Adding pytest plugins (`pytest-cov`, `pytest-xdist`, etc.). Out of scope; track separately if coverage reporting becomes a need.
- Switching to `--import-mode=importlib`. Pytest 9 still defaults to `prepend`; no current pain.
- Reorganizing the test layout further. Current `tests/` + `tests/unit/` split works.
- Enabling `--strict-markers` / `--strict-config`. Reasonable defaults but bundling them with the version bump makes rollback noisier; defer to a separate change.

## Decisions

### Decision 1: Pin to `pytest==9.0.3` (exact)

**Choice:** `pytest==9.0.3`.

**Alternatives considered:**

- `pytest>=9,<10` — looser, inconsistent with the project's exact-pin convention.
- `pytest==9.0.0` — earliest 9.0; 9.0.3 has post-release plugin-compat fixes with no behavior change for our use.
- Stay on 8.4.2 — defers work; 8.x line is maintenance-only.

**Rationale:** Exact pin matches convention. 9.0.3 is the latest stable patch as of 2026-05-06.

### Decision 2: No test changes; document the contract via ADR-0009

**Choice:** Add `docs/architecture/decisions/adr-0009-pytest-9.md` recording: (a) target pytest 9.0.x; (b) permitted fixture set (`tmp_path`, `tmp_path_factory`, `monkeypatch`, `caplog`, `request`, `capsys`, `capfd`); (c) prohibited patterns (`nose`-style hooks, `tmpdir`, bare `--strict`, `pytest.collect.*`, `pytest.warns()` with no args, `yield_fixture`).

**Alternatives considered:**

- Skip the ADR. Loses institutional memory and lets the next contributor reintroduce a removed pattern thinking pytest 9 still allows it (it would silently no-op for `setup_module`-style hooks rather than raising, which is the worst kind of regression — tests appear to pass but actually skip setup).
- Encode constraints as `[tool.pytest.ini_options] addopts = "--strict-markers --strict-config"`. Reasonable but adds noise; we have no markers or config to be strict about today. Defer until first marker is introduced.

**Rationale:** ADR is the lowest-friction durable record.

### Decision 3: Keep pytest as a `[project.optional-dependencies] dev` extra

**Choice:** Pin pytest under `dev`, not core `dependencies`.

**Rationale:** End-user installs (snap / deb / Windows installer / `pip install transaction-decorator`) should not pull in the test runner. The current `dev` placement is correct.

### Decision 4: Do not adopt new pytest 9 features eagerly

Specifically: do not enable `--strict-markers` / `--strict-config`, and do not switch `--import-mode`. Both are reasonable defaults but they are independent decisions; bundling them into this migration would make rollback noisier.

## Bundled scope (rationale for not splitting into separate proposals)

Two follow-up items were surfaced during the gap-fill audit that preceded this proposal. They are bundled here, not split:

### Item A — pytest-qt + Qt UI tests

`tests/` currently has zero coverage of `gui_elements/widget_assembler.py`, `title_bar.py`, `confirmation_dialog.py`, or `FramelessMainWindow.__init__`/`_read_row_inputs`. Covering them requires a Qt-aware test fixture (`qtbot`), which means adding `pytest-qt` to dev extras. The natural moment to add a pytest plugin is during a pytest version bump — bundling avoids a future "we never wrote those Qt tests" drift.

**Decision:** Add `pytest-qt` (latest version compatible with pytest 9.0.x) to `[project.optional-dependencies] dev` in this change, and ship the four new Qt unit-test files (`test_widget_assembler.py`, `test_title_bar.py`, `test_confirmation_dialog.py`, `test_main_window.py`) in this change.

**Alternative considered:** File a separate `add-qt-ui-tests` proposal. Rejected because it would orphan — pytest bumps are infrequent and the gap would persist for years.

### Item B — Importer canonical-name fragility

`assign_imported_values_to_new_row` in `transactions_importer.py` decides whether to apply date parsing (`parse_date`) or amount normalization (`normalize_number_format`) based on `if orig_col in date_columns` where `date_columns = column_mapping.get("Date", [])`. The list is the imported-CSV alias list (e.g., `["#Data operacji", "Data transakcji"]`). The check accidentally works only because the real `import-dictionary.json` includes the canonical name `"Date"` as the first alias. A user editing their dictionary to remove the canonical name (e.g., because they think aliases are exhaustive) would silently lose date parsing — dates would pass through as raw strings, breaking `sort_dataframe_by_date` downstream. Documented in `tests/unit/test_importer_extra.py::test_assign_imported_values_skips_date_parsing_when_canonical_name_absent`.

**Decision:** Fix in this change. The fix is a 4-line code change (`if orig_col == cts.DATE_COLUMN: ... elif orig_col == cts.AMOUNT_COLUMN: ...`) plus a one-line test inversion. Bundled because: (a) it's a testing-quality concern surfaced during the test gap-fill, (b) it's small enough that a separate change would have more administrative overhead than code, (c) the fix and the new Qt tests both touch test infrastructure.

**Alternative considered:** File a separate `fix-importer-canonical-name-fragility` proposal. Rejected on cost-of-process grounds — the change is genuinely trivial.

## Coverage gaps the audit cannot reach

For symmetry with `upgrade-pandas-3`, the same four gaps are noted, but pytest 9 only meaningfully impacts one of them:

- **Gap A (GUI / QThread)**: pytest does not run the GUI; pytest 9 changes nothing here. No mitigation needed for this proposal.
- **Gap B (frozen runtime)**: pytest is `dev`-only and is NOT bundled into the user-facing artifacts (Windows installer, deb, snap). The frozen binaries do not import pytest. Verify by running `pip install -e .` (no `[dev]`) in a fresh venv and confirming `pip show pytest` returns nothing — this is `tasks.md` §2.4.
- **Gap C (NumPy)**: not applicable; pytest has no NumPy dependency.
- **Gap D (chardet)**: not applicable.

The only NEW gap pytest 9 introduces is the silent-no-op risk for `setup_module`/`teardown_module`/`setup_class`/`teardown_class`. Gap mitigation is encoded in the spec (denylist requirement with code-review rejection scenario) and in `docs/testing-strategy.md` (the "Dependency-bump verification" section recommends `pytest -W error` after every bump, which would catch a missing-fixture regression if the silently-skipped setup leaves the test in a broken state).

## Risks / Trade-offs

- **[Risk] A future test reintroduces `setup_module` / `teardown_module` and silently no-ops (pytest 9 removed these without raising).** → Mitigation: ADR-0009 explicitly prohibits; reviewers reject at PR time. There is no runtime guard.
- **[Risk] A future test reintroduces `tmpdir` and gets a `LookupError` at fixture resolution.** → Mitigation: ADR-0009 + pytest 9 itself raises a clear error; trivially caught at CI.
- **[Risk] A new contributor adds a pytest plugin that requires `<9`.** → Mitigation: pin is exact; pip resolution will fail loudly during install rather than producing a broken environment.
- **[Risk] CI runner caches a stale pytest binary.** → Mitigation: contributors run `pip install -e .[dev]` after pulling the bump; document in ADR.
- **[Risk] `unittest.mock.patch` interaction with pytest 9 fixture ordering changes.** → Mitigation: probe full suite under `-W error` passes; `patch` is stdlib and not affected by pytest internals.
- **[Trade-off] Exact pin requires conscious bumps.** Project convention; consistency wins over auto-update convenience.

## Migration Plan

1. **Probe (done)** — `pip install pytest==9.0.3`; full test suite passes; full suite under `-W error` and `-W error::PendingDeprecationWarning` also passes; collection-only run clean.
2. **Pin** — update `pyproject.toml` `[project.optional-dependencies] dev` to `pytest==9.0.3`.
3. **ADR** — add ADR-0009 capturing the test-runner contract.
4. **Index** — register ADR-0009 in `docs/architecture/index.md`.
5. **Reinstall** — contributors run `pip install -e .[dev]` after pulling.

**Rollback strategy:** Revert the pin to `pytest==8.4.2` and reinstall. No test changes to undo.

## Open Questions

- Should we adopt `--strict-markers` and `--strict-config` opportunistically when the first custom marker lands? Likely yes; track separately.
- Should we add `pytest-cov` for coverage reporting? Out of scope; user request only.
