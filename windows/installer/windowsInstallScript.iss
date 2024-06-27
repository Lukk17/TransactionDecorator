; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "TransactionDecorator"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Lukk"
#define MyAppURL "luksarna.com"
#define MyAppExeName "TransactionDecorator.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{1845FF1D-D3A7-4C5B-A094-C35FF2F3E830}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=./
OutputBaseFilename=TransactionDecoratorInstaller
SetupIconFile=..\..\icons\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Source: "..\..\csv\allTransactions.csv"; DestDir: "{userappdata}\{#MyAppName}\csv"; Flags: ignoreversion
Source: "..\..\dictionary\*"; DestDir: "{userappdata}\{#MyAppName}\dictionary"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icons\logo.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\icons\logo.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CreateCSVFile;
var
  CSVFileName: String;
  Headers: String;
begin
  // Specify the path where the CSV file should be created
  CSVFileName := ExpandConstant('{userappdata}\{#MyAppName}\csv\allTransactions.csv');
  // Ensure the directory exists before creating the file
  ForceDirectories(ExtractFileDir(CSVFileName));

  // Define the headers for the CSV file
  Headers := 'Date;Wallet;Type;Category name;Amount;Currency;Note;Labels;Author';

  // Create and write the headers to the file
  if not SaveStringToFile(CSVFileName, Headers, False) then
    MsgBox('Failed to create and write to CSV file.', mbError, MB_OK);
end;

function InitializeSetup: Boolean;
begin
  // Create the CSV file during installation
  CreateCSVFile;
  Result := True;
end;
