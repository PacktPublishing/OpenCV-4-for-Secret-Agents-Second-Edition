#!/bin/sh

PYINSTALLER=~/PyInstaller/pyinstaller.py

# Remove any previous build of the app.
rm -rf build
rm -rf dist

# Build the app.
python "$PYINSTALLER" AngoraBlue.spec

# Determine the platform.
platform=`uname -s`

if [ "$platform" = 'Darwin' ]; then
    # We are on Mac.
    # Copy custom metadata and resources into the app bundle.
    cp -r mac/Contents dist/AngoraBlue.app
fi