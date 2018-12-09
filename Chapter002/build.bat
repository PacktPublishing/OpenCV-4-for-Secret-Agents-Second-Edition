set PYINSTALLER=C:\PyInstaller\pyinstaller.py

REM Remove any previous build of the app.
rmdir build /s /q
rmdir dist /s /q

REM Train the classifier.
python HistogramClassifier.py

REM Build the app.
python "%PYINSTALLER%" Luxocator.spec

REM Make the app an executable.
rename dist\Luxocator Luxocator.exe