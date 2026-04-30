<div align="center">

<img src="icons/logo.png" alt="Transaction Decorator logo" width="120" />

# Transaction Decorator

**A desktop GUI for cleaning, categorizing, and labeling personal transaction CSVs.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/)
[![Pandas](https://img.shields.io/badge/Pandas-2.1-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-555?logo=linux&logoColor=white)](#installation)
[![Installer: Inno Setup](https://img.shields.io/badge/installer-Inno%20Setup-1E90FF)](https://jrsoftware.org/isinfo.php)
[![Packaging: snap %26 deb](https://img.shields.io/badge/packaging-snap%20%26%20deb-E95420?logo=ubuntu&logoColor=white)](#installation)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)](#tests)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Overview

Transaction Decorator imports transaction CSV exports from your bank, normalizes them, and assigns **categories** and **labels** to each row using rules you define in JSON dictionaries. The result is a single, consistent `allTransactions.csv` ready for analysis in Excel, a notebook, or downstream tooling.

The app is built with **Python + PySide6 (Qt)** and ships as a native installer on Windows, and as `.deb` and snap packages on Linux.

## Features

- **Rule-based categorization** — assign `Category` and `Labels` from keyword dictionaries you control.
- **CSV import with normalization** — UTF-8 parsing, date-format unification, column mapping via `import-dictionary.json`.
- **Ignore rules** — drop rows during import using AND/OR conditions defined in JSON ([details](docs/dictionaries.md)).
- **Automatic backups** — every run snapshots `allTransactions.csv` into `backup/` before touching it.
- **Cross-platform packaging** — Windows installer (Inno Setup), Debian `.deb`, and snap.
- **Custom Qt UI** — frameless window with a custom title bar and themed widgets.

## Installation

| Platform | Recommended |
| --- | --- |
| **Windows** | Run `TransactionDecoratorInstaller.exe` produced by Inno Setup. Build steps: [docs/windows-build.md](docs/windows-build.md) |
| **Debian / Ubuntu** | `sudo apt install ./build/transaction-decorator_<version>.deb` — see [linux/linux.md](linux/linux.md) |
| **Snap** | `snapcraft` from `linux/snap/` — see [linux/linux.md](linux/linux.md) |

After installation, user data lives under a per-platform location — see [docs/project-structure.md](docs/project-structure.md).

## Quick start

1. Launch the app.
2. Click **Import CSV** and pick your bank export ([format requirements](docs/importing.md)).
3. Edit the dictionaries in the `dictionary/` folder to teach the app your categories and labels.
4. Click the process button to apply rules across `allTransactions.csv`.

## How it works

```text
bank-export.csv ──▶ Import (normalize + ignore rules) ──▶ allTransactions.csv
                                                              │
                                                              ▼
                                              Categorize + Label (dictionaries)
                                                              │
                                                              ▼
                                                  decorated allTransactions.csv
                                                       (backup/ snapshotted)
```

`allTransactions.csv` must contain at least `Note` and `Labels` columns; labels and categories are computed from `Note`.

## Documentation

- [Importing CSV files](docs/importing.md)
- [Dictionaries & ignore rules](docs/dictionaries.md)
- [Project structure](docs/project-structure.md)
- [Building on Windows](docs/windows-build.md)
- [Building on Linux (.deb / snap)](linux/linux.md)
- [Development guide](docs/development.md)
- [Troubleshooting](docs/troubleshooting.md)

## Tech stack

- **Python 3.11**
- **PySide6 6.6** — Qt-based GUI
- **pandas 2.1** — CSV parsing and transformation
- **chardet** — encoding detection
- **PyInstaller** + **Inno Setup** — Windows packaging
- **snapcraft** + `dpkg-deb` — Linux packaging
- **pytest** — tests

## Tests

```shell
pytest
```

See [docs/development.md](docs/development.md) for IDE run configurations.

## License

Released under the [MIT License](LICENSE).

## Author

Built by **Łukasz Sarna** — [luksarna@gmail.com](mailto:luksarna@gmail.com)
