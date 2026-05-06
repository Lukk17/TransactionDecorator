# Troubleshooting

## Missing library inside the built `.exe`

If the packaged `.exe` errors out with a missing Python library:

1. Open `TransactionDecorator.spec` and add the library to `hiddenimports`, e.g.:

   ```python
   hiddenimports=['chardet', '<library_name>'],
   ```

2. As **Administrator**, upgrade PyInstaller and install the missing library:

   ```shell
   pip install --upgrade pyinstaller <library_name>
   ```

3. As your **normal user**, rebuild:

   ```shell
   pyinstaller TransactionDecorator.spec
   ```

## `pyinstaller: command not recognized`

This usually means `pip` installed into the wrong site-packages directory because of a global config. As a temporary workaround for the install step only, remove:

```
C:\Python311\Lib\site-packages\custom_packages_location.pth
C:\ProgramData\pip\pip.ini
```

Reinstall PyInstaller into your project venv, then restore the files if needed.

## Tests pass in dev but the packaged binary misbehaves

The dev test suite (`pytest`) does not exercise the PyInstaller-frozen runtime. After bumping a pinned dependency, follow the **Packaged binary verification** section in [testing-strategy.md](testing-strategy.md) to install the built artifact and run the manual smoke. Most "works in dev, broken in install" issues come from missing PyInstaller `hiddenimports` — see "Missing library inside the built `.exe`" above.

## Imported CSV shows mojibake (garbled diacritics)

`chardet` can misidentify European single-byte encodings (CP1252 vs ISO-8859-2) on small files. If Polish/German diacritics come out wrong:

1. Open the original export in a text editor that shows the actual encoding (VS Code's status bar; Notepad++).
2. Re-save as **UTF-8 with BOM**.
3. Re-import. The BOM makes detection unambiguous.
