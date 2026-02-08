; *** Inno Setup Script for ArkPets ***
; This script is based on Inno Setup 6, a free installer for Windows programs.
; Documentation: https://jrsoftware.org/ishelp.php
; Download Inno Setup: https://jrsoftware.org/isdl.php

#define MyAppName "AudioClient"
#define MyAppVersion "1.2.0"
#define AppCopyright "Copyright © 2025-2026 Half_nothing"
#define MyAppPublisher "Half_nothing"
#define MyAppPublisherURL "https://www.half-nothing.cn/"
#define MyAppURL "https://www.apocfly.com/"

[Setup]
; WARN: The value of AppId uniquely identifies this app. Do not use the same AppId value in installers for other apps.
; (To generate a new GUID, click Tools | Generate GUID inside the Inno Setup IDE.)
AppCopyright        ={#AppCopyright}
AppId               ={{BF6D540A-54EB-4191-8ABE-6750CD417CBA}
AppName             ={#MyAppName}
AppVersion          ={#MyAppVersion}
AppVerName          ="{#MyAppName} {#MyAppVersion}"
AppPublisher        ={#MyAppPublisher}
AppPublisherURL     ={#MyAppPublisherURL}
AppSupportURL       ={#MyAppURL}

AllowNoIcons        =yes
Compression         =lzma2/max
DefaultDirName      ="{userpf}\{#MyAppName}"
DefaultGroupName    ={#MyAppName}
PrivilegesRequired  =lowest
OutputBaseFilename  ={#MyAppName}-Setup-v{#MyAppVersion}
OutputDir           =..\build\package
SetupIconFile       =..\icon\logo.ico
SolidCompression    =yes
UninstallDisplayIcon={app}\{#MyAppName}.ico
WizardStyle         =modern
ChangesEnvironment  =false

[Languages]
Name: "chinese_simplified";  MessagesFile: "ChineseSimplified.isl"
Name: "chinese_traditional";  MessagesFile: "ChineseTraditional.isl"
Name: "english";  MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\dist\config.yaml"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; WorkingDir: "{app}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppName}.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#MyAppName}.exe"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\{#MyAppName}.exe"
Type: files; Name: "{app}\config.yaml"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\lib"
