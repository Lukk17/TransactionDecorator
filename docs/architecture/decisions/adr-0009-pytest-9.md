# ADR-0009 — Pytest 9 test-runner contract

- Status: Accepted
- Date: 2026-05-06

## Context

Pytest 9.0 was released in late 2025. The 9.0 line removes a long list of behaviors that have been deprecated since 6.x/7.x — `nose`-style hooks, the legacy `LEGACY_PATH` / `py.path.local` fixtures, the bare `--strict` flag, several `pytest.warns` shortcuts, `yield_fixture`, and miscellaneous internal API exposed under `pytest.collect.*`. The migration was scoped via `openspec/changes/upgrade-pytest-9/` with an audit covering 20 risk patterns; all probes pass cleanly under `pytest -W error`.

The most dangerous removal is `setup_module`/`teardown_module`/`setup_class`/`teardown_class`. Pytest 9 silently does NOT call these — there is no error, only a test that appears to pass while skipping its setup. Code review is the only durable defense.

## Decision

Pin `pytest==9.0.3` under `[project.optional-dependencies] dev` in `pyproject.toml`. Adopt the following contract for all test code in `tests/`:

### Permitted patterns

- **Built-in fixtures**: `tmp_path`, `tmp_path_factory`, `monkeypatch`, `caplog`, `request`, `capsys`, `capfd`.
- **Markers**: `@pytest.mark.parametrize`, `@pytest.mark.skip`, `@pytest.mark.skipif`, `@pytest.mark.xfail`.
- **Hooks**: `pytest_collection_modifyitems`, `pytest_configure`, plain `conftest.py` fixtures via `@pytest.fixture`.
- **xunit-style at class scope only**: `setup_method`, `teardown_method`.

### Prohibited patterns (with rationale)

| Pattern | Why prohibited |
|---|---|
| `setup_module` / `teardown_module` / `setup_class` / `teardown_class` | Pytest 9 silently does NOT call these. No error — just a test that appears to pass while missing its setup. Use fixtures instead. |
| Module-level `def setup()` / `def teardown()` | Same silent-no-op risk. |
| `tmpdir` / `tmpdir_factory` | Removed (legacy `py.path.local`). Use `tmp_path` / `tmp_path_factory`. |
| Bare `--strict` CLI flag | Removed. Use `--strict-markers` and/or `--strict-config`. |
| `pytest.collect.*` namespace | Removed. |
| `pytest.warns()` with no expected warning category | Removed. Must specify a warning class. |
| `yield_fixture` | Removed (deprecated since pytest 4). Use `@pytest.fixture` with `yield`. |

### `caplog` usage contract

```python
with caplog.at_level("WARNING"):
    function_under_test(...)
assert any("expected substring" in rec.message for rec in caplog.records)
```

Bare `caplog.text` substring checks are permitted but discouraged — structured iteration over `caplog.records` is more precise.

### Plugin policy

- `pytest-qt` is the one explicitly approved plugin (added in this change to enable Qt UI testing).
- Any other plugin (e.g., `pytest-cov`, `pytest-xdist`) requires a separate ADR explaining the need.

## Consequences

- All 138 existing tests pass under pytest 9.0.3 with `-W error`.
- Code reviewers must reject `setup_module` / `teardown_module` / `tmpdir` / `pytest.warns()` no-args / bare `--strict` patterns at PR time. Pytest 9 will not flag them.
- The bundled additions in `upgrade-pytest-9` §5 (pytest-qt + Qt UI tests, importer fragility fix, encoding smoke automation, QThread isolation assertion, single-command version bump) ship as part of this same change so the bundled gaps aren't forgotten after the version pin.
- Future contributors adding a custom marker should also enable `--strict-markers` opportunistically (deferred from this change to keep the rollback diff focused).

## References

- Migration proposal: `openspec/changes/upgrade-pytest-9/`
- Manual smoke + dependency-bump verification: `docs/testing-strategy.md`
- Pytest 9 release notes: https://docs.pytest.org/en/stable/changelog.html
