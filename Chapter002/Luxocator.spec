a = Analysis(['Luxocator.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)


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
          console=False)

app = BUNDLE(exe,
             name='Luxocator.app',
             icon=None)
