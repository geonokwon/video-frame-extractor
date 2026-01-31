; Inno Setup 스크립트 - 영상프레임추출기 Windows 인스톨러
; Inno Setup 다운로드: https://jrsoftware.org/isdl.php

#define MyAppName "영상프레임추출기"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName "영상프레임추출기.exe"

[Setup]
; 기본 정보
AppId={{YOUR-UNIQUE-APP-ID}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=영상프레임추출기_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; 권한
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; 아이콘 (있는 경우)
;SetupIconFile=icon.ico

; 라이센스 (있는 경우)
;LicenseFile=LICENSE.txt

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면 바로가기 만들기"; GroupDescription: "추가 아이콘:"; Flags: unchecked

[Files]
; 실행 파일
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 추가 파일 (필요한 경우)
;Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; 시작 메뉴 바로가기
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; 바탕화면 바로가기
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 설치 완료 후 실행
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
