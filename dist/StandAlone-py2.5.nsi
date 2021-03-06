; Installer script for for standalone jBrout application.
; http://jbrout.googlecode.com

; requires the ZipDLL plugin DLL to be in the Plugins directory of your NSIS installation
; this is avaliable from http://nsis.sourceforge.net/ZipDLL_plug-in

!define PRODUCT_NAME "jBrout Stand-alone"
!include version.nsi
!define PRODUCT_PUBLISHER "jBrout Development Team"
!define PRODUCT_WEB_SITE "http://jbrout.googlecode.com"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"
!define PRODUCT_STARTMENU_REGVAL "NSIS:StartMenuDir"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!define MUI_LICENSEPAGE_RADIOBUTTONS
!insertmacro MUI_PAGE_LICENSE "..\jbrout\data\gpl.txt"
; Components page
;!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Start menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "jBrout"
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${PRODUCT_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\app\readme.txt"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "Italian"

!insertmacro MUI_RESERVEFILE_LANGDLL

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "c:\jBrout-${PRODUCT_VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES\jBrout"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section -SETTINGS
  SetOverwrite ifnewer
SectionEnd

Section "jBrout Application" SEC01
  SetOutPath "$INSTDIR"
  File "jBrout.exe"
  SetOutPath "$INSTDIR\app"
  File "..\jbrout\jbrout.py"
  File "..\jbrout\__init__.py"
  File "..\readme.txt"
  SetOutPath "$INSTDIR\app\data"
  File "..\jbrout\data\gpl.txt"
  File "..\jbrout\data\jbrout.glade"
  File "..\jbrout\data\version.txt"
  SetOutPath "$INSTDIR\app\data\gfx"
  File "..\jbrout\data\gfx\basket.png"
  File "..\jbrout\data\gfx\calendar.png"
  File "..\jbrout\data\gfx\check_disabled.png"
  File "..\jbrout\data\gfx\check_false.png"
  File "..\jbrout\data\gfx\check_no.png"
  File "..\jbrout\data\gfx\check_not.png"
  File "..\jbrout\data\gfx\check_true.png"
  File "..\jbrout\data\gfx\dir_disabled.png"
  File "..\jbrout\data\gfx\dir_false.png"
  File "..\jbrout\data\gfx\dir_no.png"
  File "..\jbrout\data\gfx\dir_true.png"
  File "..\jbrout\data\gfx\folder.png"
  File "..\jbrout\data\gfx\imgError.png"
  File "..\jbrout\data\gfx\imgNotFound.png"
  File "..\jbrout\data\gfx\imgNoThumb.png"
  File "..\jbrout\data\gfx\jbrout.ico"
  File "..\jbrout\data\gfx\jbrout.png"
  File "..\jbrout\data\gfx\new_jbrout.svg"
  File "..\jbrout\data\gfx\raw.png"
  File "..\jbrout\data\gfx\refresh.png"
  SetOutPath "$INSTDIR\app\data\tools"
  File "..\jbrout\data\tools\jpegtran.exe"
  File "..\jbrout\data\tools\exiftool.exe"
  SetOutPath "$INSTDIR\app\jbrout"
  File "..\jbrout\jbrout\__init__.py"
  File "..\jbrout\jbrout\char_utils.py"
  File "..\jbrout\jbrout\common.py"
  File "..\jbrout\jbrout\commongtk.py"
  File "..\jbrout\jbrout\conf.py"
  File "..\jbrout\jbrout\db.py"
  File "..\jbrout\jbrout\externaltools.py"
  File "..\jbrout\jbrout\folderselect.glade"
  File "..\jbrout\jbrout\folderselect.py"
  File "..\jbrout\jbrout\listview.py"
  File "..\jbrout\jbrout\pyexiv.py"
  File "..\jbrout\jbrout\tools.py"
  File "..\jbrout\jbrout\winbookmarks.py"
  File "..\jbrout\jbrout\winpref.py"
  File "..\jbrout\jbrout\winshow.py"
  SetOutPath "$INSTDIR\app\libs"
  File "..\jbrout\libs\__init__.py"
  File "..\jbrout\libs\dict4ini.py"
  File "..\jbrout\libs\extListview.py"
  File "..\jbrout\libs\gladeapp.py"
  File "..\jbrout\libs\i18n.py"
  SetOutPath "$INSTDIR\app\plugins"
  File "..\jbrout\plugins\__init__.py"
    SetOutPath "$INSTDIR\app\po"
  File "..\jbrout\po\jbrout.pot"
  SetOutPath "$INSTDIR\app\po\de\LC_MESSAGES"
  File "..\jbrout\po\de\LC_MESSAGES\jbrout.mo"
  File "..\jbrout\po\de\LC_MESSAGES\jbrout.po"
  SetOutPath "$INSTDIR\app\po\fr\LC_MESSAGES"
  File "..\jbrout\po\fr\LC_MESSAGES\jbrout.mo"
  File "..\jbrout\po\fr\LC_MESSAGES\jbrout.po"
  SetOutPath "$INSTDIR\app\po\it\LC_MESSAGES"
  File "..\jbrout\po\it\LC_MESSAGES\jbrout.mo"
  File "..\jbrout\po\it\LC_MESSAGES\jbrout.po"
  SetOutPath "$INSTDIR\app\po\sv\LC_MESSAGES"
  File "..\jbrout\po\sv\LC_MESSAGES\jbrout.mo"
  File "..\jbrout\po\sv\LC_MESSAGES\jbrout.po"

; Shortcuts
  SetOutPath "$INSTDIR\app"
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\jBrout.lnk" \
                 "$INSTDIR\jBrout.exe" \
                 '' \
                 "$INSTDIR\app\data\gfx\jBrout.ico" \
                 0 \
                 SW_SHOWNORMAL \
                 "" \
                 "jBrout Photo Manager"
  ;CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\jBrout Read Only.lnk" \
  ;               "$INSTDIR\jBrout.exe" \
  ;               ' --view' \
  ;               "$INSTDIR\app\data\gfx\jBrout.ico" \
  ;               0 \
  ;               SW_SHOWNORMAL \
  ;               "" \
  ;               "jBrout Photo Manager in Read Only Mode"
  CreateShortCut "$DESKTOP\jBrout.lnk" \
                 "$INSTDIR\jBrout.exe" \
                 '' \
                 "$INSTDIR\app\data\gfx\jBrout.ico" \
                 0 \
                 SW_SHOWNORMAL \
                 "" \
                 "jBrout Photo Manager"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Python Runtime" SEC02
  SetOutPath "$TEMP"
  FILE "winRuntime\python_runtime-2.5.zip"
  ZipDLL::extractall "$TEMP\python_runtime-2.5.zip" "$INSTDIR"
  Delete "$TEMP\python_runtime-2.5.zip"
SectionEnd

Section "GTK Runtime" SEC03
  AddSize 32638
  SetOutPath "$TEMP"
  FILE "winRuntime\GTK_runtime.zip"
  ZipDLL::extractall "$TEMP\GTK_runtime.zip" "$INSTDIR"
  Delete "$TEMP\GTK_runtime.zip"
SectionEnd

Section "Comment Plug-in" SEC11
  SetOutPath "$INSTDIR\app\plugins\comment"
  File "..\jbrout\plugins\comment\__init__.py"
  File "..\jbrout\plugins\comment\comment.py"
  File "..\jbrout\plugins\comment\comment.glade"
  SetOutPath "$INSTDIR\app\plugins\comment\gfx"
  File "..\jbrout\plugins\comment\gfx\gtk-edit.png"
  SetOutPath "$INSTDIR\app\plugins\comment\po"
  File "..\jbrout\plugins\comment\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\comment\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\comment\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\comment\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\comment\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\comment\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\comment\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\comment\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\comment\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\comment\po\it\LC_MESSAGES\plugin.po"
SectionEnd

Section "Download Plug-in"
  SetOutPath "$INSTDIR\app\plugins\download"
  File "..\jbrout\plugins\download\__init__.py"
  File "..\jbrout\plugins\download\download.py"
  File "..\jbrout\plugins\download\download.glade"
  File "..\jbrout\plugins\download\nameBuilder.py"
  File "..\jbrout\plugins\download\nameBuilder.glade"
  SetOutPath "$INSTDIR\app\plugins\download\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\download\po\de\LC_MESSAGES\plugin.po"
  File "..\jbrout\plugins\download\po\de\LC_MESSAGES\plugin.mo"
  SetOutPath "$INSTDIR\app\plugins\download\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\download\po\fr\LC_MESSAGES\plugin.po"
  File "..\jbrout\plugins\download\po\fr\LC_MESSAGES\plugin.mo"

SectionEnd

Section "Open in Explorer Plug-in" SEC12
  SetOutPath "$INSTDIR\app\plugins\openExplorer"
  File "..\jbrout\plugins\openExplorer\__init__.py"
  SetOutPath "$INSTDIR\app\plugins\openExplorer\po"
  File "..\jbrout\plugins\openExplorer\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\openExplorer\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\openExplorer\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\openExplorer\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\openExplorer\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\openExplorer\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\openExplorer\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\openExplorer\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\openExplorer\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\openExplorer\po\it\LC_MESSAGES\plugin.po"
 SectionEnd

Section "Re-date Plug-in" SEC13
  SetOutPath "$INSTDIR\app\plugins\redate"
  File "..\jbrout\plugins\redate\redate.glade"
  File "..\jbrout\plugins\redate\__init__.py"
  File "..\jbrout\plugins\redate\redate.py"
  SetOutPath "$INSTDIR\app\plugins\redate\po"
  File "..\jbrout\plugins\redate\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\redate\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\redate\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\redate\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\redate\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\redate\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\redate\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\redate\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\redate\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\redate\po\it\LC_MESSAGES\plugin.po"
SectionEnd

Section "Folders by Dates Plug-in" SEC14
  SetOutPath "$INSTDIR\app\plugins\foldersByDates"
  File "..\jbrout\plugins\foldersByDates\__init__.py"
  SetOutPath "$INSTDIR\app\plugins\foldersByDates\po"
  File "..\jbrout\plugins\foldersByDates\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\foldersByDates\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\foldersByDates\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\foldersByDates\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\foldersByDates\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\foldersByDates\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\foldersByDates\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\foldersByDates\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\foldersByDates\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\foldersByDates\po\it\LC_MESSAGES\plugin.po"
SectionEnd

Section "Multi Export PLug-in" SEC15
  SetOutPath "$INSTDIR\app\plugins\multiexport"
  File "..\jbrout\plugins\multiexport\__init__.py"
  File "..\jbrout\plugins\multiexport\crypt.py"
  File "..\jbrout\plugins\multiexport\winexport.glade"
  File "..\jbrout\plugins\multiexport\winexport.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\xsl"
  File "..\jbrout\plugins\multiexport\xsl\album.photosite.xsl"
  File "..\jbrout\plugins\multiexport\xsl\album.xsl"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs"
  File "..\jbrout\plugins\multiexport\libs\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\flickr.py"
  File "..\jbrout\plugins\multiexport\libs\mailer.py"
  File "..\jbrout\plugins\multiexport\libs\pycasaweb.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\__init__.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb\atom"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\auth.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\client.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\core.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\data.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\http.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\http_core.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\http_interface.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\mock_http.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\mock_http_core.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\mock_service.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\service.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\token_store.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\atom\url.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb\gdata"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\auth.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\client.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\data.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\gauth.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\service.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\urlfetch.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb\gdata\base"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\base\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\base\service.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb\gdata\oauth"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\oauth\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\oauth\rsa.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb\gdata\tlslite"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\api.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\BaseDB.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\Checker.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\constants.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\errors.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\FileObject.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\HandshakeSettings.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\mathtls.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\messages.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\Session.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\SessionCache.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\SharedKeyDB.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\TLSConnection.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\TLSRecordLayer.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\VerifierDB.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\X509.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\X509CertChain.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\__init__.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\AES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\ASN1Parser.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\cipherfactory.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\codec.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\compat.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\Cryptlib_AES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\Cryptlib_RC4.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\Cryptlib_TripleDES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\cryptomath.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\dateFuncs.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\hmac.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\jython_compat.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\keyfactory.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\OpenSSL_AES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\OpenSSL_RC4.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\OpenSSL_RSAKey.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\OpenSSL_TripleDES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\PyCrypto_AES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\PyCrypto_RC4.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\PyCrypto_RSAKey.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\PyCrypto_TripleDES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\Python_AES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\Python_RC4.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\Python_RSAKey.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\RC4.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\rijndael.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\RSAKey.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\TripleDES.py"
  File "..\jbrout\plugins\multiexport\libs\picasaweb\gdata\tlslite\utils\xmltools.py"
  SetOutPath "$INSTDIR\app\plugins\multiexport"
  File "..\jbrout\plugins\multiexport\winexport.glade"
  SetOutPath "$INSTDIR\app\plugins\multiexport\po"
  File "..\jbrout\plugins\multiexport\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\multiexport\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\multiexport\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\multiexport\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\multiexport\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\multiexport\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\multiexport\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\multiexport\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\multiexport\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\multiexport\po\it\LC_MESSAGES\plugin.po"
SectionEnd

Section "Instant Web Server Plug-in" SEC16
  SetOutPath "$INSTDIR\app\plugins\instantWeb"
  File "..\jbrout\plugins\instantWeb\instantweb.py"
  File "..\jbrout\plugins\instantWeb\__init__.py"
  File "..\jbrout\plugins\instantWeb\instantweb.glade"
  SetOutPath "$INSTDIR\app\plugins\instantWeb\po"
  File "..\jbrout\plugins\instantWeb\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\instantWeb\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\instantWeb\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\instantWeb\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\instantWeb\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\instantWeb\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\instantWeb\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\instantWeb\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\instantWeb\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\instantWeb\po\it\LC_MESSAGES\plugin.po"
SectionEnd

Section "Rotation Plug-in" SEC17
  SetOutPath "$INSTDIR\app\plugins\rotate\gfx"
  File "..\jbrout\plugins\rotate\gfx\rotate-left.png"
  File "..\jbrout\plugins\rotate\gfx\rotate-right.png"
  SetOutPath "$INSTDIR\app\plugins\rotate"
  File "..\jbrout\plugins\rotate\__init__.py"
  SetOutPath "$INSTDIR\app\plugins\rotate\po"
  File "..\jbrout\plugins\rotate\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\rotate\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\rotate\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\rotate\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\rotate\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\rotate\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\rotate\po\fr\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\rotate\po\it\LC_MESSAGES"
  File "..\jbrout\plugins\rotate\po\it\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\rotate\po\it\LC_MESSAGES\plugin.po"
SectionEnd

Section "Bulk Tagging Plug-in" SEC18
  SetOutPath "$INSTDIR\app\plugins\bulkTag"
  File "..\jbrout\plugins\bulkTag\bulkTag.glade"
  File "..\jbrout\plugins\bulkTag\bulkTag.py"
  File "..\jbrout\plugins\bulkTag\__init__.py"
  SetOutPath "$INSTDIR\app\plugins\bulkTag\po"
  File "..\jbrout\plugins\bulkTag\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\bulkTag\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\bulkTag\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\bulkTag\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\bulkTag\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\bulkTag\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\bulkTag\po\fr\LC_MESSAGES\plugin.po"
SectionEnd

Section "View EXIF Plug-in" SEC19
  SetOutPath "$INSTDIR\app\plugins\viewExif"
  File "..\jbrout\plugins\viewExif\viewExif.glade"
  File "..\jbrout\plugins\viewExif\viewExif.py"
  File "..\jbrout\plugins\viewExif\__init__.py"
SectionEnd

Section "IPTC/XMP tags synchronization Plug-in" SEC20
  SetOutPath "$INSTDIR\app\plugins\syncTags"
  File "..\jbrout\plugins\syncTags\__init__.py"
  SetOutPath "$INSTDIR\app\plugins\syncTags\po"
  File "..\jbrout\plugins\syncTags\po\plugin.pot"
  SetOutPath "$INSTDIR\app\plugins\syncTags\po\de\LC_MESSAGES"
  File "..\jbrout\plugins\syncTags\po\de\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\syncTags\po\de\LC_MESSAGES\plugin.po"
  SetOutPath "$INSTDIR\app\plugins\syncTags\po\fr\LC_MESSAGES"
  File "..\jbrout\plugins\syncTags\po\fr\LC_MESSAGES\plugin.mo"
  File "..\jbrout\plugins\syncTags\po\fr\LC_MESSAGES\plugin.po"
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Uninstall.lnk" "$INSTDIR\uninst.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\app\gfx\jbrout.ico"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP

  Delete "$SMPROGRAMS\$ICONS_GROUP\Uninstall.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Website.lnk"
  Delete "$DESKTOP\jBrout.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\jBrout.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\jBrout Read Only.lnk"
  RMDir "$SMPROGRAMS\$ICONS_GROUP"
  RMDir /r "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  SetAutoClose true
SectionEnd
