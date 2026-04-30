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
