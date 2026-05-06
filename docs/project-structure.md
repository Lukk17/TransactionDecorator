# Project structure

## Repository layout (development)

```text
TransactionDecorator/
├── backup/                                # Auto-generated CSV backups
│   └── allTransactions.csv_XXX.csv
├── csv/
│   ├── allTransactions.csv                # Main transactions file
│   └── template.csv
├── dictionary/
│   ├── categories-dictionary.json
│   ├── import-dictionary.json
│   ├── ignore-dictionary.json
│   └── labels-dictionary.json
├── icons/                                 # GUI assets (logo + window icons)
├── linux/
│   ├── snap/
│   │   ├── user-data/user-data-copy.sh
│   │   ├── transaction-decorator-entrypoint
│   │   └── transaction_decorator.desktop
│   ├── createDebFile.sh                   # .deb builder
│   └── linux.md
├── src/
│   ├── config/
│   │   ├── constants.py
│   │   └── style_config.py
│   ├── gui_elements/
│   │   ├── confirmation_dialog.py
│   │   ├── title_bar.py
│   │   └── widget_assembler.py
│   ├── processor/
│   │   ├── transactions_decorator.py      # Decorate / categorize / label pipeline
│   │   └── transactions_importer.py       # Bank-CSV import + normalization
│   ├── utils/
│   │   └── utils.py
│   └── gui.py                             # Application entry point
├── tests/
│   ├── conftest.py
│   ├── import_test.py                     # Integration: import flow
│   ├── transaction_decorator_test.py      # Integration: decorate flow
│   ├── decorator/                         # Decorator fixtures + expected outputs
│   ├── import/                            # Importer fixtures + expected outputs
│   └── unit/                              # Pure-function unit tests
├── docs/
│   ├── architecture/                      # ADRs + Mermaid diagrams
│   └── *.md
├── openspec/                              # Spec-driven change proposals
├── windows/
│   ├── entrypoint/                        # PyInstaller output
│   └── installer/
│       └── windowsInstallScript.iss       # Inno Setup script
├── pyproject.toml                         # PEP 621 metadata + pinned deps
├── snapcraft.yaml
└── TransactionDecorator.spec              # PyInstaller spec
```

## Windows installation

After running the installer:

```text
InstallFolder/
├── TransactionDecorator.exe
└── icons/
    ├── logo.ico
    ├── logo.png
    └── ...                                # GUI icons
```

User data:

```text
%APPDATA%/TransactionDecorator/
├── backup/
│   └── allTransactions.csv_XXX.csv
├── csv/
│   └── allTransactions.csv
└── dictionary/
    ├── categories-dictionary.json
    ├── import-dictionary.json
    ├── ignore-dictionary.json
    └── labels-dictionary.json
```

## Linux `.deb` installation

```text
/usr/lib/transaction-decorator/
├── icons/
└── src/
```

User data:

```text
/usr/share/transaction-decorator/
├── backup/
├── csv/
└── dictionary/
```

## Linux snap installation

```text
/snap/transaction-decorator/current/
├── meta/
│   ├── gui/transaction-decorator.desktop
│   └── snap.yaml
├── user-data/user-data-copy.sh
├── usr/
│   ├── bin/transaction-decorator-entrypoint
│   ├── lib/transaction-decorator/src/
│   ├── local/lib/python3.x
│   └── share/
│       ├── application/transaction-decorator.desktop
│       └── transaction-decorator/
│           ├── csv/
│           ├── dictionary/
│           └── icons/
└── template.csv
```

User data:

```text
~/snap/transaction-decorator/current/
├── backup/
├── csv/
└── dictionary/
```
