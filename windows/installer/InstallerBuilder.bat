@echo off
REM going to project root
cd ..\..
REM installing python dependency from setup.py in project root
pip install -e .
REM Creating .exe file via PyInstaller
pyinstaller --distpath "./" TransactionDecorator.spec
REM Creating Windows installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "D:\Development\projekty-IT\TransactionDecorator\windows\installer\windowsInstallScript.iss"
echo Compilation finished.
