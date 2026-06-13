; LabQC Windows Installer -- Inno Setup Script
; ==============================================
; Prerequisites:
;   1. Install Inno Setup 6 (https://jrsoftware.org/isinfo.php)
;   2. Build PyInstaller dist/ first:  pyinstaller labqc.spec
;   3. Compile this script:  "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
;
; Output: Output\LabQC_Setup_1.0.0.exe

#define AppName "LabQC"
#define AppVersion "1.0.0"
#define AppPublisher "凯思康 (KSC)"
#define AppURL "http://selivis.vip.cpolar.cn/labqc/"
#define SourceDir "dist\LabQC"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=LabQC_Setup_{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
WizardSmallImageFile=setup_sidebar.bmp
WizardImageFile=setup_main.bmp
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "其他快捷方式:"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LabQC"; Filename: "{app}\LabQC.exe"; WorkingDir: "{app}"
Name: "{group}\卸载 LabQC"; Filename: "{uninstallexe}"
Name: "{autodesktop}\LabQC"; Filename: "{app}\LabQC.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\LabQC.exe"; Description: "启动 LabQC"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\backend\data"

[Code]
function InitializeSetup: Boolean;
begin
  Result := True;
end;
