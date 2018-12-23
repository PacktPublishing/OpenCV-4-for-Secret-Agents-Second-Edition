set PYINSTALLER=pyinstaller

REM Remove any previous build of the app.
rmdir build /s /q
rmdir dist /s /q

REM Train the classifier.
python HistogramClassifier.py

REM Build the app.
"%PYINSTALLER%" --onefile --windowed Luxocator.spec

REM Make the app an executable.
rename dist\Luxocator Luxocator.exe
