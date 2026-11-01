For context menu


cry.bat:
@echo off
chcp 65001 >nul
python "%~dp0cry.py" "%~1"
pause


regedit.reg:
[HKEY_CURRENT_USER\Software\Classes\*\shell\MyScripts\shell\09_cry]
"MUIverb"="cry"

[HKEY_CURRENT_USER\Software\Classes\*\shell\MyScripts\shell\09_cry\command]
@="\"R:\\Projects\\CONTEXT\\cry.bat\" \"%1\""

