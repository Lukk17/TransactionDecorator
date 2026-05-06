## 1. Pre-flight verification (audit-first, not just "tests pass")

- [ ] 1.1 Source grep audit — confirm zero matches in `tests/` for each removed/regressed pattern:
  - `grep -rn "setup_module\|teardown_module\|setup_class\|teardown_class" tests/`
  - `grep -rn "^\s*def setup(\|^\s*def teardown(" tests/`
  - `grep -rn "tmpdir\b" tests/` (plain `tmpdir`, not `tmp_path`)
  - `grep -rn "pytest\.collect\|pytest\.warns\s*(\s*)\|yield_fixture\|pytest\.deprecated_call" tests/`
  - `grep -rn "\-\-strict\b" pyproject.toml .run/ tests/` (bare `--strict` only; `--strict-markers`/`--strict-config` are fine)
- [ ] 1.2 Run `pip install pytest==9.0.3` in a scratch venv (or temporarily in the project venv)
- [ ] 1.3 Run full test suite (`pytest`) — must show 59/59 passing
- [ ] 1.4 Re-run with **`-W error -W error::PendingDeprecationWarning`** — must still show 59/59 passing
- [ ] 1.5 Run a collection-only check (`pytest --co -q -W error`) to surface plugin-discovery warnings that don't fire during normal execution — must report 59 tests, no warnings

## 2. Pin update

- [ ] 2.1 Edit `pyproject.toml`: change `pytest==8.4.2` to `pytest==9.0.3` under `[project.optional-dependencies] dev`
- [ ] 2.2 Reinstall dev extras (`pip install -e .[dev]`) and confirm `pip show pytest` reports 9.0.3
- [ ] 2.3 Run full test suite once more — must remain 59/59 green
- [ ] 2.4 Confirm pytest is NOT installed when running `pip install -e .` (without `[dev]`) in a fresh venv

## 3. Architecture documentation

- [ ] 3.1 Create `docs/architecture/decisions/adr-0009-pytest-9.md` (status: Accepted, dated 2026-05-06) documenting:
  - the pytest 9.0.x target and exact pin
  - permitted fixtures: `tmp_path`, `tmp_path_factory`, `monkeypatch`, `caplog`, `request`, `capsys`, `capfd`
  - prohibited patterns (with rationale): `setup_module`/`teardown_module`/`setup_class`/`teardown_class` (silently no-op — most dangerous), `tmpdir`/`tmpdir_factory` (removed), `pytest.collect.*` (removed), `pytest.warns()` with no args (removed), bare `--strict` (removed), `yield_fixture` (removed)
  - `caplog` usage contract: `with caplog.at_level(LEVEL): ...; assert any("..." in rec.message for rec in caplog.records)`
- [ ] 3.2 Add ADR-0009 to the table in `docs/architecture/index.md`

## 4. Manual smoke cross-check

- [ ] 4.1 After §2 passes, run the "Dependency-bump verification" checklist in `docs/testing-strategy.md` (which references back here for the audit; the smoke confirms the pinned suite still runs end-to-end)

## 5. Spec lifecycle

- [ ] 5.1 Run `openspec validate upgrade-pytest-9` and address any schema warnings
- [ ] 5.2 After all tasks above are checked off, run `openspec archive upgrade-pytest-9` to fold `test-runner` into `openspec/specs/`
