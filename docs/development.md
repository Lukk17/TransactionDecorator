# Development

## Source layout

Mark `src/` as **Sources Root** in your IDE so imports resolve correctly.

See [project-structure.md](project-structure.md) for the full tree.

## Installing dev dependencies

The project uses `pyproject.toml` (PEP 621). To set up a development venv:

```shell
python -m venv venv
venv/Scripts/activate          # Windows
source venv/bin/activate       # Linux/macOS
pip install -e .[dev]
```

The `[dev]` extra pulls in pytest and pyinstaller. The runtime dependencies (pandas, PySide6, chardet) are always installed.

## Run configurations

IDE run configurations are stored in the `.run/` folder:

- Direct launch of the app via `src/gui.py`
- Test runs

## Running tests

Tests live under `tests/`. Configuration is in `pyproject.toml` (`[tool.pytest.ini_options]`). Run from the project root:

```shell
pytest                                  # entire suite (59 tests)
pytest tests/unit/                      # unit tests only
pytest tests/import_test.py             # one integration suite
pytest tests/transaction_decorator_test.py
pytest -W error                         # strict — fail on any warning (use after dependency bumps)
```

For end-to-end manual checks the automated suite cannot reach (live GUI, packaged binaries, encoding edge cases), see [testing-strategy.md](testing-strategy.md).

## Building

- Windows installer — see [windows-build.md](windows-build.md)
- Linux `.deb` and snap — see [../linux/linux.md](../linux/linux.md)

## Architecture

For ADRs and component/sequence diagrams, see [architecture/index.md](architecture/index.md).
