
# Transaction Decorator

Python with PySide6 GUI

The App is taking csv file named `allTransaction.csv` in which all transactions should be listed in rows.  
Transaction can be [imported](#importing-csv) from any CSV file.  
CSV file need to have two columns `Note` and `Labels`, labels are computed based on notes.  

App is creating backup of the original CSV file before processing in `backup` folder.

In ``dictionary`` folder there are json files called
```
categories-dictionary.json
ignore-dictionary.json
import-dictionary.json
labels-dictionary.json
```

Project structure for development you can see [here](#structure-for-development) 
and for installing [here](#structure-of-folders-and-files-after-installation-which-are-required-for-app-to-work)

`src` folder should be marked as "Sources Root" in IDE (that way imports will be correctly visible by IDE)

---

## Release Versions

versions are specified in files:

Windows:
```
windows/installer/windowsInstallScript.iss
```

linux `.deb`:
```
linux/createDebFile.sh
```

snap:
```
snapcraft.yaml
linux/snap/transaction_decorator.desktop
```

---
## Run configurations

Run configurations for IDE are stored in `.run` folder.  
You can find ones for:
* direct launch app via python script
* running tests

---

## Installing on Windows

### Installing required packages into PyInstaller:

Create python virtual env by going `File` > `Project structure..` > `SDK` > `+ Add SDK` > `Python SDK..` :  
`Virtualenv Environment` > `New environment` (do not inherit packages)

If you use global env all packages will be copied into installer - and this can be large > 10 GB

##### try to temporary, only for installing it delete:
```
C:\Python311\Lib\site-packages\custom_packages_location.pth
```
and
```
C:\ProgramData\pip\pip.ini
```

Terminal path should be in same directory as `setup.py` file (project root directory)
```shell
pip install -e .
```

To create requirements with a current python local installation type:
```shell
pip freeze > requirements.txt
```
Then copy them into `install_requires` part of `setup.py`

### Create `.exe` file and installer
The easiest way will be using a script from root directory:
```
.\windows\installer\InstallerBuilder.bat
```
It Can be also done manually [PyInstaller](#pyinstaller-creating-exe-file) and [Inno Setup](#inno-setup-windows-installer)


---
## Importing CSV

To import CSV, click the button "Import CSV".   
Remember that:
 * CSV file needs to be in UTF-8 encoding and can't have any description lines at the beginning.   
   Often bank export csv have in the first line some data about exporting which make file not valid CSV.  
   In the above case use Excel to import and then save as `CSV UTF-8` file.
 * Columns count should be correct.  
 * All rows should have the same number of columns (delimiters) as first, header row with column names.  

CSV will be parsed, a date format will be parsed to default one, and rows will be inserted at the end of the file.

-------------------------

## Ignoring data

`ignore-dictionary.json` dictionary was added to make possible to ignore rows while importing.  
If row is ignored it is not copied from imported CSV file into `allTransactions.csv`.  

In json you can specify which columns with which values (and its combinations) should mark row as ignored.

```json
{
  "ignore_rules": [
    {
      "conditions": [
        {
          "column": "Amount",
          "value": "100"
        },
        {
          "column": "Name",
          "value": "VAT"
        },
        {
          "column": "Currency",
          "value": "PLN"
        }
      ]
    },
    {
      "conditions": [
        {
          "column": "Category",
          "value": "Food"
        }
      ]
    }
  ]
}
```
in the above example ignored will be rows where in columns:  
`Amount` have value `100` AND in column `Name` value `VAT` AND in column `Currency` value `PLN`  
OR  
in column `Category` have value `Food`

---

## Running unit tests

Just run files:
```
import_test.py
```
and
```
transaction_decorator_test.py
```

---

### PyInstaller creating exe file
Creating Windows `.exe` file:

You need to install `pyinstaller`:
```
pip install pyinstaller
```
if error 
```
pyinstaller: The term 'pyinstaller' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
```
see [this](#try-to-temporary-only-for-installing-it-delete)

The Terminal needs to be in the main project directory (for an app icon relative path to work)

use Run configuration for it or:
```shell
pyinstaller --clean --distpath "./" TransactionDecorator.spec
```

Compiled `TransactionDecorator.exe` file will be in `./windows/entrypoint/` folder.  
It will be not working correctly if there are no folders `icons, dictionary, csv, backup` on same level as executable. 
For testing without using Installer, you need to mimic folder structure.
See Windows app [structure](#structure-of-folders-and-files-after-installation-which-are-required-for-app-to-work)

---

### Inno Setup Windows Installer

Inno Setup script is located in `windows/installer/installScript.iss`.  


1. You can open this script via Inno Setup application and build it by pressing `F9` key or clicking button `Run`
2. Or use Run configuration, which will run `.bat` script
3. Or build via terminal started in project main directory:
    ```powershell
    & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\windows\installer\windowsInstallScript.iss"
    ```
---

## Structure of folders and files after installation which are required for app to work

## Project structure (for development)
```text
/Project main folder
├── backup/                                                 # Directory for backup-related files
│   └── allTransactions.csv_XXX.csv                             # Example file in backup directory
│
├── csv/                                                    # Directory for CSV files
│   ├── allTransactions.csv                                     # Example CSV file
│   └── template.csv                                            # Template CSV file
│
├── dictionary/                                             # Directory for dictionary-related files
│   ├── categories-dictionary.json                               # Categories dictionary file
│   ├── import-dictionary.json                                   # Import dictionary file
│   ├── ignore-dictionary.json                                   # Import dictionary file
│   └── labels-dictionary.json                                   # Labels dictionary file
│
├── icons/                                                  # Directory for icon files
│   ├── close.png                                               # Icon for GUI
│   ├── csv-file.png                                            # Icon for GUI
│   ├── dictionary.png                                          # Icon for GUI
│   ├── file-backup.png                                         # Icon for GUI
│   ├── logo.ico                                                # Main icon file
│   ├── logo.png
│   ├── maximize.png                                            # Icon for GUI
│   ├── minimize.png                                            # Icon for GUI
│   └── restore.png     
│
├── linux/                                                  # Directory for linux installers
│   ├── snap/                                                   # Directory for snap installer
│   │   ├── user-data/                                              # Directory for user data scripts
│   │   │   └── user-data-copy.sh                                       # Script for copying user data files when running snap
│   │   ├── transaction-decorator-entrypoint                        # Entry point script for snap app
│   │   └── transaction_decorator.desktop                           # Desktop shortcut for snap app
│   ├── createDebFile.sh                                        # Script for creating debian/ubuntu .deb package
│   └── linux.md                                                # Readme file with linux installation tips
│
├── src/                                                    # Source files - python scripts
│   ├── config/                                              
│   │    ├── constants.py                                              
│   │    └── style_config.py
│   ├── gui_elements/    
│   │    ├── confirmation_dialog.py                                                                                  
│   │    ├── title_bar.py                                                                                      
│   │    └── widget_assembler.py  
│   ├── processor/    
│   │    ├── process_import.py                                                                                                                                                                      
│   │    └── process_transactions.py       
│   ├── utils/      
│   │    └── utils.py                                                                                                                                                                                                                                                                                                                              
│   └── gui.py                                                  # Main python script - launch app via it
│
├── test-csv/                                               # Folder with prepared csv for app testing
│   ├── import/                                                 # CSV files ready to be imported in app
│   │   ├── testData-comma-with-artefacts-importing.csv
│   │   ├── testData-processing.csv                                 # Best CSV app to check overall importing and processing
│   │   └── testData-semicolon-with-artefacts-importing.csv
│   ├── processed-examples/                                     # CSV for comparison after processing imported testData-processing.csv
│   │   ├── correctly-force-all-processed.csv
│   │   ├── correctly-force-categories-processed.csv
│   │   ├── correctly-force-labels-processed.csv
│   │   ├── correctly-noforce-english-decimal-processed.csv
│   │   └── correctly-noforce-standard-decimal-processed.csv
│
├── windows/
│   ├── entrypoint/                                          # Folder for generating TransactionDecorator.exe file
│   │    └── [generated] TransactionDecorator.exe            # Generated by PyInstaller                                                                                                                                                                                                                                                                                                                
│   └── installer/                                              
│        ├── windowsInstallScript.iss                        # Inno Setup script for compiling windows installer                                                                                                                                                                                                                                                                                             
│        └── [generated] TransactionDecoratorInstaller.exe   # Windows Installer                                                                                                                                                                                                                                                                                                                       
│
├── .gitignore                                                
│
├── README.md                                                # This file
│
├── setup.py                                                 # List of python requirements libs
│
├── snapcraft.yaml                                           # Script for creating Linux snap installer
│
├── [generated] TransactionDecorator.exe                     # Generated by PyInstaller 
│
└── TransactionDecorator.spec                                # Specification file for PyInstaller 
```

### Structure of installed app on Windows:
Source files:
```text
InstallFolder/
│
├── TransactionDecorator.exe                                # The main executable of your application
└── icons/                                                  # Directory for icon files
    ├── logo.ico                                                # Main icon file
    ├── logo.png
    ├── close.png                                               # Icon for GUI
    ├── csv-file.png                                            # Icon for GUI
    ├── dictionary.png                                          # Icon for GUI
    ├── file-backup.png                                         # Icon for GUI
    ├── maximize.png                                            # Icon for GUI
    ├── minimize.png                                            # Icon for GUI
    └── restore.png                                             # Icon for GUI                                            
```
User data files:
```text
<userHome>/AppData/Roaming/TransactionDecorator/
├── backup/                                                 # Directory for backup-related files
│   └── allTransactions.csv_XXX.csv                             # Example file in backup directory
│
├── csv/                                                    # Directory for CSV files
│   └── allTransactions.csv                                     # Example CSV file
│
└── dictionary/                                             # Directory for dictionary-related files
    ├── categories-dictionary.json                               # Categories dictionary file
    ├── import-dictionary.json                                   # Import dictionary file
    ├── ignore-dictionary.json                                   # Import dictionary file
    └── labels-dictionary.json                                   # Labels dictionary file
```

### Structure of installed app via .deb package on Linux:
Source files:
```text
/usr/lib/transaction-decorator/
├── icons/                                                  # Directory for icon files
│   ├── logo.ico                                                # Main icon file
│   ├── logo.png
│   ├── close.png                                               # Icon for GUI
│   ├── csv-file.png                                            # Icon for GUI
│   ├── dictionary.png                                          # Icon for GUI
│   ├── file-backup.png                                         # Icon for GUI
│   ├── maximize.png                                            # Icon for GUI
│   ├── minimize.png                                            # Icon for GUI
│   └── restore.png                                             # Icon for GUI        
└── src/                                                    # All python scripts from project src directory                                  
```
User data files:
```text
/usr/share/transaction-decorator/
├── backup/                                                 # Directory for backup-related files
│   └── allTransactions.csv_XXX.csv                             # Example file in backup directory
│
├── csv/                                                    # Directory for CSV files
│   └── allTransactions.csv                                     # Example CSV file
│
└── dictionary/                                             # Directory for dictionary-related files
    ├── categories-dictionary.json                               # Categories dictionary file
    ├── import-dictionary.json                                   # Import dictionary file
    ├── ignore-dictionary.json                                   # Import dictionary file
    └── labels-dictionary.json                                   # Labels dictionary file
```


### Structure of installed app via snap on Linux:
Source and install files:
```text
/snap/transaction-decorator/current/
├── meta/                                                   # Meta directory created by snap when installing
│   ├── gui/
│   │   └── transaction-decorator.desktop                       # Desktop shortcut template used by snap installer 
│   └── snap.yaml                                           # File created from snapcraft.yaml during snap install
│
├── user-data/
│   └── user-data-copy.sh                                       # Script for copying user data when running snap
│
├── usr/
│   ├── bin/
│   │   └── transaction-decorator-entrypoint                        # Entrypoint starting app
│   ├── lib/transaction-decorator/src/                          # All python scripts from project src directory
│   ├── local/lib/python3.x                                     # Compiled python scripts
│   └── share/                                                  # Content for install only, NOT used by running app 
│       ├── application/
│       │   └── transaction-decorator.desktop                           # Desktop shortcut template used by snap installer
│       └── transaction-decorator/
│           ├── csv/
│           │   └── allTransactions.csv                                     # Example CSV file
│           ├── dictionary/ 
│           │   ├── categories-dictionary.json                               # Categories dictionary file
│           │   ├── import-dictionary.json                                   # Import dictionary file
│           │   ├── ignore-dictionary.json                                   # Import dictionary file
│           │   └── labels-dictionary.json                                   # Labels dictionary file
│           └── icons/                                                  # Directory for icon files
│               ├── logo.ico                                                # Main icon file
│               ├── logo.png
│               ├── close.png                                               # Icon for GUI
│               ├── csv-file.png                                            # Icon for GUI
│               ├── dictionary.png                                          # Icon for GUI
│               ├── file-backup.png                                         # Icon for GUI
│               ├── maximize.png                                            # Icon for GUI
│               ├── minimize.png                                            # Icon for GUI
│               └── restore.png                                             # Icon for GUI        
│
└── template.csv                                               # Template CSV file                                         
```
User data files:
```text
~/snap/transaction-decorator/current/
├── backup/                                                 # Directory for backup-related files
│   └── allTransactions.csv_XXX.csv                             # Example file in backup directory
│
├── csv/                                                    # Directory for CSV files
│   └── allTransactions.csv                                     # Example CSV file
│
└── dictionary/                                             # Directory for dictionary-related files
    ├── categories-dictionary.json                               # Categories dictionary file
    ├── import-dictionary.json                                   # Import dictionary file
    ├── ignore-dictionary.json                                   # Import dictionary file
    └── labels-dictionary.json                                   # Labels dictionary file
```

-------------------------

## Troubleshooter

### 1. Lack of a library in exe file  
   If when launched .exe file with app error occurs that there is lack of any python library,  
   edit `TransactionDecorator.spec` file and add a missing library to `hiddenimports=['chardet'],` section.  
   Then run:  
   as ADMIN
   ```shell
      pip install --upgrade pyinstaller <library_name>
   ```
   as NORMAL user
   where `<library_name` is for example `chardet`
   ```shell
      pyinstaller TransactionDecorator.spec
   ```
   And now try again to compile pyinstaller.

