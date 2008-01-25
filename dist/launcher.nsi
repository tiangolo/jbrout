; jBrout Launcher
;--------------
 
; Requires the ZipDLL plugin DLL to be in the Plugins directory of your NSIS installation
; this is avaliable from http://nsis.sourceforge.net/Setting_Environment_Variables_to_Active_Installer_Process

; Requires the SetEnv plugin DLL to be in the Plugins directory of your NSIS installation
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
  StrCmp $0 '0' +2
  MessageBox MB_OK 'jBrout exited error code $0 please see "$EXEDIR\jbrout.log" for details'
SectionEnd
