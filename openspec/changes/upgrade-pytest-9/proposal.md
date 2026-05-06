## Why

Pytest 9.0 was released in late 2025; the 8.x line is now in maintenance only. The 9.0 release removes a long list of behavior that has been deprecated since 6.x/7.x — `nose`-style `setup_module`/`teardown_module`, the legacy `LEGACY_PATH` / `py.path.local` fixtures, the bare `--strict` flag, several `pytest.warns` shortcuts, `yield_fixture`, and miscellaneous internal API exposed under `pytest.collect.*`. The most dangerous removal is `setup_module`/`teardown_module` because pytest 9 silently does NOT call them — there is no error, only a test that appears to pass while skipping its setup. Migrating now keeps us on the supported line and forces a documented audit confirming none of those legacy patterns leaked into the test suite during the recent refactor.

This proposal is grounded in two layers of evidence (not just "the test suite passes"):

1. **Source grep** of `tests/` for every removed pytest API (20 distinct patterns audited — see `design.md`).
2. **Targeted runtime probes** with `pytest==9.0.3` installed: full suite under `-W error -W error::PendingDeprecationWarning`, plus a collection-only run to surface plugin-discovery warnings that may not fire during normal execution.

Both layers ran clean. Of 20 patterns audited, zero require code changes.

## What Changes

- Bump `pytest==8.4.2` → `pytest==9.0.3` in `pyproject.toml` `[project.optional-dependencies] dev`.
- **BREAKING** for any future code: `nose`-style hooks (`setup_module`, `teardown_module`, `setup`, `teardown` at module/class scope) no longer run AND do not raise. Use fixtures or `setup_method`/`teardown_method`. Current suite uses neither, so no migration needed today — but this is the highest-risk regression class for new tests.
- **BREAKING** for any future code: `py.path.local` fixtures (`tmpdir`, `tmpdir_factory`) are removed. Pytest 9 raises a clear error on use. Current suite uses `tmp_path`/`tmp_path_factory` exclusively.
- **BREAKING** for any future code: the bare `--strict` CLI flag is removed; use `--strict-markers` and `--strict-config`. Current suite passes neither.
- **BREAKING** for any future code: `pytest.warns()` with no expected category is removed (must specify a warning class). Current suite uses none.
- **BREAKING** for any future code: `yield_fixture` (deprecated since pytest 4) is fully removed. Use `@pytest.fixture` with `yield`.
- Document the test-runner contract via ADR-0009 so future contributors understand which patterns are permitted and which silently no-op.

## Capabilities

### New Capabilities

- `test-runner`: Defines which pytest major version the project targets, the explicit allowlist of permitted fixtures/hooks, the explicit denylist of removed patterns, and the `caplog` usage contract.

### Modified Capabilities

(none — `openspec/specs/` is currently empty; this proposal introduces the first capability scoped to the test runner.)

## Impact

- **Code**: No source changes. Test files audited (20-pattern grep) — all 7 test modules use only stable pytest APIs.
- **Tests**: 59/59 passing on pytest 9.0.3 with strict warnings (`-W error -W error::PendingDeprecationWarning`). Collection-only run also clean.
- **CI / packaging**: `pyproject.toml` pin update only. Pytest is a `dev` extra and does not ship in user-facing artifacts (Windows installer / deb / snap), so end users are unaffected.
- **Plugins**: We use no pytest plugins. No compatibility surface.
- **ADR-0009** added to `docs/architecture/decisions/`.
