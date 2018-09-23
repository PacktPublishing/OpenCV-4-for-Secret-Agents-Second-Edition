a = Analysis(['AngoraBlue.py'],
             pathex=['.'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)


# Include our app's detection and recognition models.
a.datas.append(('cascades/haarcascade_frontalcatface.xml',
                'cascades/haarcascade_frontalcatface.xml',
                'DATA'))
a.datas.append(('cascades/haarcascade_frontalface_alt.xml',
                'cascades/haarcascade_frontalface_alt.xml',
                'DATA'))
a.datas.append(('recognizers/lbph_cat_faces.xml',
                'recognizers/lbph_cat_faces.xml',
                'DATA'))
a.datas.append(('recognizers/lbph_human_faces.xml',
                'recognizers/lbph_human_faces.xml',
                'DATA'))


pyz = PYZ(a.pure)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='AngoraBlue',
          icon='win\icon-windowed.ico',
          debug=False,
          strip=None,
          upx=True,
          console=True)

app = BUNDLE(exe,
             name='AngoraBlue.app',
             icon=None)