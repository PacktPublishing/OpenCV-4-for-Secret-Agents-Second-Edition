#!/usr/bin/env sh


# Search for common names of PyInstaller in $PATH.
if [ -x "$(command -v "pyinstaller")" ]; then
    PYINSTALLER=pyinstaller
elif [ -x "$(command -v "pyinstaller-3.6")" ]; then
    PYINSTALLER=pyinstaller-3.6
elif [ -x "$(command -v "pyinstaller-3.5")" ]; then
    PYINSTALLER=pyinstaller-3.5
elif [ -x "$(command -v "pyinstaller-3.4")" ]; then
    PYINSTALLER=pyinstaller-3.4
elif [ -x "$(command -v "pyinstaller-2.7")" ]; then
    PYINSTALLER=pyinstaller-2.7
else
    echo "Failed to find PyInstaller in \$PATH"
    exit 1
fi
echo "Found PyInstaller in \$PATH with name \"$PYINSTALLER\""

# Remove any previous build of the app.
rm -rf build
rm -rf dist

# Build the app.
"$PYINSTALLER" --onefile AngoraBlue.spec

# Determine the platform.
platform=`uname -s`

if [ "$platform" = 'Darwin' ]; then
    # We are on Mac.
    # Copy custom metadata and resources into the app bundle.
    cp -r mac/Contents dist/AngoraBlue.app
fi
