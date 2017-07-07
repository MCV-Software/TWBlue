!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
Unicode true
CRCCheck on
ManifestSupportedOS all
XPStyle on
Name "TWBlue"
OutFile "TWBlue_setup.exe"
InstallDir "$PROGRAMFILES\twblue"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "InstallLocation"
RequestExecutionLevel admin
SetCompress auto
SetCompressor /solid lzma
SetDatablockOptimize on
VIAddVersionKey ProductName "TWBlue"
VIAddVersionKey LegalCopyright "Copyright 2016 Manuel Cortéz."
VIAddVersionKey ProductVersion "0.91"
VIAddVersionKey FileVersion "0.91"
VIProductVersion "0.91.0.0"
VIFileVersion "0.91.0.0"
!insertmacro MUI_PAGE_WELCOME
!define MUI_LICENSEPAGE_RADIOBUTTONS
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
var StartMenuFolder
!insertmacro MUI_PAGE_STARTMENU startmenu $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_LINK "Visit TWBlue website"
!define MUI_FINISHPAGE_LINK_LOCATION "http://twblue.es"
!define MUI_FINISHPAGE_RUN "$INSTDIR\TWBlue.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Italian"
!insertmacro MUI_LANGUAGE "Finnish"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "Polish"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Hungarian"
!insertmacro MUI_LANGUAGE "Turkish"
!insertmacro MUI_LANGUAGE "Arabic"
!insertmacro MUI_LANGUAGE "Galician"
!insertmacro MUI_LANGUAGE "Catalan"
!insertmacro MUI_LANGUAGE "Basque"
!insertmacro MUI_LANGUAGE "Croatian"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "SerbianLatin"
!insertmacro MUI_LANGUAGE "Romanian"
!insertmacro MUI_RESERVEFILE_LANGDLL
Section
SetShellVarContext All
SetOutPath "$INSTDIR"
${If} ${RunningX64}
File /r TWBlue64\*
${Else}
File /r TWBlue\*
${EndIf}
CreateShortCut "$DESKTOP\TWBlue.lnk" "$INSTDIR\TWBlue.exe"
!insertmacro MUI_STARTMENU_WRITE_BEGIN startmenu
CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\TWBlue.lnk" "$INSTDIR\TWBlue.exe"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\TWBlue on the web.lnk" "http://twblue.es"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_END
WriteUninstaller "$INSTDIR\Uninstall.exe"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "DisplayName" "TWBlue"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "UninstallString" '"$INSTDIR\uninstall.exe"'
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" "InstallLocation" $INSTDIR
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" "Publisher" "Manuel Cortéz"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "DisplayVersion" "0.91"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "URLInfoAbout" "http://twblue.es"
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "VersionMajor" 0
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "VersionMinor" 91
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "NoRepair" 1
SectionEnd
Section "Uninstall"
SetShellVarContext All
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue"
RMDir /r /REBOOTOK $INSTDIR
Delete "$DESKTOP\TWBlue.lnk"
!insertmacro MUI_STARTMENU_GETFOLDER startmenu $StartMenuFolder
RMDir /r "$SMPROGRAMS\$StartMenuFolder"
SectionEnd
Function .onInit
${If} ${RunningX64}
StrCpy $instdir "$programfiles64\twblue"
${EndIf}
!insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd
