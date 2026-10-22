; Inno Setup Script for CpuCore0Meter
; Turnkey Windows Installer with auto-shortcut, auto-start, and clean uninstaller

#ifndef MyAppVersion
#define MyAppVersion "1.5"
#endif

#define MyAppName "CpuCore0Meter"
#define MyAppPublisher "CpuMeter"
#define MyAppExeName "CpuCore0Meter.exe"

[Setup]
AppId={{D37E84B1-2F1E-4B9A-8CEE-B5E3C7A1D4E0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist_installer
OutputBaseFilename=CpuCore0Meter_Setup_v{#MyAppVersion}
SetupIconFile=CpuCore0Meter.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "Jalankan otomatis saat Windows dinyalakan (Run at Startup)"; GroupDescription: "Pengaturan Startup:"

[Files]
Source: "dist\CpuCore0Meter.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "LibreHardwareMonitorLib.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "run.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "CpuCore0Meter.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{autoprograms}\{#MyAppName}\CpuCore0Meter (Compact 4cm)"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--core 0"; IconFilename: "{app}\CpuCore0Meter.ico"
Name: "{autoprograms}\{#MyAppName}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\CpuCore0Meter.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--core 0"; Tasks: desktopicon; IconFilename: "{app}\CpuCore0Meter.ico"

[Registry]
; Register in HKCU Run for auto-start on boot if task is selected
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --core 0"; Tasks: autostart; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--core 0"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
