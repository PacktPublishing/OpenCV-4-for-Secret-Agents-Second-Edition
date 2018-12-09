import os

a = Analysis(['Luxocator.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

# Determine the platform.
platform = os.name

if platform == 'nt':
    # We are on Windows.
    # A bug causes the 'pyconfig' module to be included twice.
    # Remove the duplicate.
    for data in a.datas:
        if 'pyconfig' in data[0]:
            a.datas.remove(data)
            break

# Include SSL certificates for the sake of the 'requests' module.
a.datas.append(('cacert.pem', 'cacert.pem', 'DATA'))

# Include our app's classifier data.
a.datas.append(('classifier.mat', 'classifier.mat', 'DATA'))

pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Luxocator',
          icon='win\icon-windowed.ico',
          debug=False,
          strip=None,
          upx=True,
          console=False )

app = BUNDLE(exe,
             name='Luxocator.app',
             icon=None)