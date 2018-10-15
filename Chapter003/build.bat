set PYINSTALLER=C:\PyInstaller\pyinstaller.py

REM Remove any previous build of the app.
rmdir build /s /q
rmdir dist /s /q

REM Build the app.
python "%PYINSTALLER%" AngoraBlue.spec

REM Make the app an executable.
rename dist\Luxocator AngoraBlue.exe