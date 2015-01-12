!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
CRCCheck on
XPStyle on
Name "TW Blue"
OutFile "TWBlue_setup.exe"
InstallDir "$PROGRAMFILES\twblue"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "InstallLocation"
RequestExecutionLevel admin
SetCompress auto
SetCompressor /solid lzma
SetDatablockOptimize on
VIAddVersionKey ProductName "TW Blue"
VIAddVersionKey LegalCopyright "Copyright 2014 Manuel Cortez."
VIAddVersionKey ProductVersion "0.51"
VIAddVersionKey FileVersion "0.51"
VIProductVersion "0.51.0.0"
!insertmacro MUI_PAGE_WELCOME
!define MUI_LICENSEPAGE_RADIOBUTTONS
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
var StartMenuFolder
!insertmacro MUI_PAGE_STARTMENU startmenu $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_LINK "Visit TW Blue website"
!define MUI_FINISHPAGE_LINK_LOCATION "http://twblue.es"
!define MUI_FINISHPAGE_RUN "$INSTDIR\TWBlue.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS "-i"
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
!insertmacro MUI_RESERVEFILE_LANGDLL
Section
SetShellVarContext All
SetOutPath "$INSTDIR"
${If} ${RunningX64}
File /r TWBlue64\*
${Else}
File /r TWBlue\*
${EndIf}
CreateShortCut "$DESKTOP\TW Blue.lnk" "$INSTDIR\TWBlue.exe" "-i"
!insertmacro MUI_STARTMENU_WRITE_BEGIN startmenu
CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\TW Blue.lnk" "$INSTDIR\TWBlue.exe" "-i"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\TW Blue on the web.lnk" "http://twblue.es"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_END
WriteUninstaller "$INSTDIR\Uninstall.exe"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "DisplayName" "TW Blue"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "UninstallString" '"$INSTDIR\uninstall.exe"'
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" "InstallLocation" $INSTDIR
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" "Publisher" "Manuel Cortez"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "DisplayVersion" "0.51"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "URLInfoAbout" "http://twblue.es"
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "VersionMajor" 0
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "VersionMinor" 51
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue" "NoRepair" 1
SectionEnd
Section "Uninstall"
SetShellVarContext All
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\twblue"
RMDir /r /REBOOTOK $INSTDIR
Delete "$DESKTOP\TW Blue.lnk"
!insertmacro MUI_STARTMENU_GETFOLDER startmenu $StartMenuFolder
RMDir /r "$SMPROGRAMS\$StartMenuFolder"
SectionEnd
Function .onInit
${If} ${RunningX64}
StrCpy $instdir "$programfiles64\twblue"
${EndIf}
!insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd
