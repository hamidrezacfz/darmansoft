#define MyAppName "درمان‌سافت — نسخه نمایشی"
#define MyAppVersion "1.6 Demo"
#define MyAppPublisher "درمان‌سافت"
#define MyAppExeName "DarmanSoftDemo.exe"

[Setup]
AppId={{B9D5F32B-9774-4AB9-A8E4-5A4F57A83191}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\DarmanSoftDemo
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\output\demo
OutputBaseFilename=DarmanSoft-Demo-Setup-1.6
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\DarmanSoftDemo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای نسخه نمایشی درمان‌سافت"; Flags: nowait postinstall skipifsilent
