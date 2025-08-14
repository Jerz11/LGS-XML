[Setup]
AppName=LGS XML
AppVersion=1.0.0
AppPublisher=LGS Systems
AppPublisherURL=https://github.com/Jerz11/LGS-XML
AppSupportURL=https://github.com/Jerz11/LGS-XML
AppUpdatesURL=https://github.com/Jerz11/LGS-XML
DefaultDirName={userpf}\LGS XML
DefaultGroupName=LGS XML
AllowNoIcons=yes
LicenseFile=
OutputDir=dist\installer
OutputBaseFilename=LGS-XML-Setup-1.0.0
SetupIconFile=
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "dist\LGS XML\LGS XML.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\LGS XML\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "config.json"; DestDir: "{userappdata}\LGS Trzby"; Flags: ignoreversion onlyifdoesntexist
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\LGS XML"; Filename: "{app}\LGS XML.exe"
Name: "{group}\{cm:UninstallProgram,LGS XML}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\LGS XML"; Filename: "{app}\LGS XML.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\LGS XML"; Filename: "{app}\LGS XML.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\LGS XML.exe"; Description: "{cm:LaunchProgram,LGS XML}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\LGS Trzby"

[CustomMessages]
czech.LaunchProgram=Spustit %1
