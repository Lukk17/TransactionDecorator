# Building on Windows

This document covers building the `.exe` and Windows installer from source. End-users should just run the prebuilt installer.

## 1. Prepare a virtual environment

In your IDE: `File` > `Project Structure...` > `SDK` > `+ Add SDK` > `Python SDK...` and pick:

> **Virtualenv Environment** > **New environment** (do **not** inherit packages).

A clean venv is important — using a global env means PyInstaller will copy *every* installed package into the installer (often >10 GB).

If `pip` resolves to your global config, temporarily remove (only for the install step):

```
C:\Python311\Lib\site-packages\custom_packages_location.pth
C:\ProgramData\pip\pip.ini
```

From the project root:

```shell
pip install -e .
```

To regenerate the requirements list:

```shell
pip freeze > requirements.txt
```

Then mirror them into `install_requires` inside `setup.py`.

## 2. Build the `.exe` and installer

The fastest path is the bundled script:

```shell
.\windows\installer\InstallerBuilder.bat
```

This runs PyInstaller and Inno Setup in sequence. Manual steps are below.

### PyInstaller — build the executable

```shell
pip install pyinstaller
pyinstaller --clean --distpath "./" TransactionDecorator.spec
```

The terminal must be in the project root for the icon's relative path to resolve.

The compiled `TransactionDecorator.exe` lands in `./windows/entrypoint/`. To run it without an installer, replicate the [installed folder structure](project-structure.md#windows-installation).

### Inno Setup — build the installer

The script lives at `windows/installer/windowsInstallScript.iss`. Build options:

1. Open it in the Inno Setup IDE and press `F9` (or click **Run**).
2. Use the IDE run configuration that wraps `.bat` execution.
3. From a terminal in the project root:

   ```powershell
   & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\windows\installer\windowsInstallScript.iss"
   ```

## Release versions

Versions live in:

- Windows: `windows/installer/windowsInstallScript.iss`
- Linux `.deb`: `linux/createDebFile.sh`
- Snap: `snapcraft.yaml`, `linux/snap/transaction_decorator.desktop`
