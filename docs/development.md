# Development

## Source layout

Mark `src/` as **Sources Root** in your IDE so imports resolve correctly.

See [project-structure.md](project-structure.md) for the full tree.

## Run configurations

IDE run configurations are stored in the `.run/` folder:

- Direct launch of the app via `src/gui.py`
- Test runs

## Running tests

Tests live in the `test/` directory. Run them through your IDE's test runner or directly:

```shell
pytest test/import_test.py
pytest test/transaction_decorator_test.py
```

## Building

- Windows installer — see [windows-build.md](windows-build.md)
- Linux `.deb` and snap — see [../linux/linux.md](../linux/linux.md)
