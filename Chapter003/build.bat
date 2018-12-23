set PYINSTALLER=pyinstaller

REM Remove any previous build of the app.
rmdir build /s /q
rmdir dist /s /q

REM Build the app.
"%PYINSTALLER%" --onefile AngoraBlue.spec

REM Make the app an executable.
rename dist\Luxocator AngoraBlue.exe
