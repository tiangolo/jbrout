; jBrout Launcher
;--------------
 
; Requires the SetEnv plugin DLL to be in the Plugins directory of your NSIS installation
; this is avaliable from http://nsis.sourceforge.net/Setting_Environment_Variables_to_Active_Installer_Process

; Requires the ExecDos plugin DLL to be in the Plugins directory of your NSIS installation
;http://nsis.sourceforge.net/ExecDos_plug-in

Name "jBrout Launcher"
Caption "jBrout Launcher"
Icon "..\jbrout\data\gfx\jbrout.ico"
OutFile "jBrout.exe"
 
CRCCheck On
WindowIcon Off
SilentInstall silent
AutoCloseWindow true
ShowInstDetails nevershow

!Include "GetParameters.nsh"

Var PYTHONEXE
Var GTKDIRECTORY
Var PROGRAMDIRECTORY


Section ""
  StrCpy $PYTHONEXE "$EXEDIR\python_runtime\python.exe"
  GetFullPathName /SHORT $0 $EXEDIR
  StrCpy $GTKDIRECTORY "$0\GTK"
  StrCpy $PROGRAMDIRECTORY "$0\app"
  
  SetEnv::SetEnvVar "PATH" "$GTKDIRECTORY\bin"
  SetEnv::SetEnvVar "GTK_BASEPATH" "$GTKDIRECTORY"
  
  Call GetParameters
  Pop $R0
  SetOutPath "$ProgramDirectory"
  ExecDos::exec '"$PYTHONEXE" jbrout.py $R0' '' '$EXEDIR\jbrout.log'
  Pop $0
  StrCmp $0 '0'  +10 
  IfFileExists "$EXEDIR\jbrout.log" +3 0
  MessageBox MB_OK "jBrout exited with error code $0 but did not leave a log file"
  goto finish
  MessageBox MB_YESNO "jBrout exited with error code $0 do you wish to view the log file?" IDYES true IDNO finish
  true:
    IfFileExists "$WINDIR\notepad.exe" +3 0
    MessageBox MB_OK 'Notepad is not installed please view "$EXEDIR\jbrout.log" manually'
    goto finish
    Exec '"$WINDIR\notepad.exe" "$EXEDIR\jbrout.log"' 
  finish:
SectionEnd
