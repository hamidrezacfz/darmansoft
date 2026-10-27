#define MyAppName "درمان‌سافت"
#define MyAppVersion "1.2"
#define MyAppPublisher "درمان‌سافت"
#define MyAppExeName "Clinita.exe"

[Setup]
AppId={{C3D00FDE-0A2D-4E64-8A0B-1A9B5FDE093A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Clinita
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\output\installer
OutputBaseFilename=DarmanSoft-Setup-1.2
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\Clinita\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای درمان‌سافت"; Flags: nowait postinstall skipifsilent
