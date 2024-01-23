
# Transaction Decorator

Python with PySide6 GUI

The App is taking csv file named `allTransaction.csv` in which all transactions should be listed in rows.  
CSV file need to have two columns `Note` and `Labels`, labels are computed based on notes.  

App is creating backup of the original CSV file before processing in `backup` folder.

In ``dictionary`` folder there is json file called `labels-dictionary.json`

Project structure for development you can see [here](#structure-for-development) 
and for installing [here](#structure-of-folders-and-files-after-installation-which-are-required-for-app-to-work)

Run configurations for IDE are stored in `.run` folder.  
You can find ones for:
 * direct launch app via python script
 * building exe file by PyInstaller
 * building Windows installer by Inno Setup

-------------------------
## Importing CSV

To import CSV, click the button "Import CSV".   
Remember that:
 * CSV file needs to be in UTF-8 encoding and can't have any description lines at the beginning   
   (often bank export csv have in first line some data about exporting which make file not valid CSV).  
 * Columns count should be correct.  
 * All rows should have same number of columns (delimiters) as first, header row with column names.  

CSV will be parsed, a date format will be parsed to default one, and rows will be inserted at the end of the file.

-------------------------

## Installing on Windows

### Installing required packages into PyInstaller:
```shell
pip install -r ./src/requirements.txt
```

### Creating Windows `.exe` file:

The Terminal needs to be in the main project directory (for an app icon relative path to work)
```powershell
pyinstaller --noconsole --onefile --name "TransactionDecorator" --icon "./icons/logo.ico" --distpath "windows/entrypoint/" src/gui.py
```

Compiled `TransactionDecorator.exe` file will be in `./windows/entrypoint/` folder.  
It will be not working correctly if there are no folders `icons, dictionary, csv, backup` on same level as executable. 
For testing without using Installer, you need to mimic folder structure.
See Windows app [structure](#structure-of-folders-and-files-after-installation-which-are-required-for-app-to-work)


### Windows Installer

Inno Setup script is located in `windows/installer/installScript.iss`.  
1. You can open this script via Inno Setup application and build it by pressing `F9` key or clicking button `Run`
2. Or build via terminal started in project main directory:
    ```powershell
    & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\windows\installer\installScript.iss"
    ```
-------------------------

## Structure of folders and files after installation which are required for app to work

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
```text
<userHome>/AppData/Roaming/TransactionDecorator folder
├── backup/                                                 # Directory for backup-related files
│   └── allTransactions.csv_20231129234112.csv                  # Example file in backup directory
│
├── csv/                                                    # Directory for CSV files
│   └── allTransactions.csv                                     # Example CSV file
│
├── dictionary/                                             # Directory for dictionary-related files
│   └── labels-dictionary.json                                  # Example dictionary file
```

## Structure for development
```text
/Project main folder
│
├── src
│   └── gui.py                                              # Main python script - launch app via it
│
├── backup/                                                 # Directory for backup-related files
│   └── allTransactions.csv_20231129234112.csv                  # Example file in backup directory
│
├── csv/                                                    # Directory for CSV files
│   └── allTransactions.csv                                     # Example CSV file
│
├── dictionary/                                             # Directory for dictionary-related files
│   └── dictionary.json                                         # Example dictionary file
│
└── icons/                                                  # Directory for icon files
    ├── logo.ico                                                # Main icon file
    ├── logo.png
    ├── close.png                                               # Icon for GUI
    ├── csv-file.png                                            # Icon for GUI
    ├── dictionary.png                                          # Icon for GUI
    ├── file-backup.png                                         # Icon for GUI
    ├── maximize.png                                            # Icon for GUI
    ├── minimize.png                                            # Icon for GUI
    └── restore.png     
```
