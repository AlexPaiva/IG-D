# reels_downloader.spec
block_cipher = None

a = Analysis(['reels_downloader.py'],
             pathex=[],
             binaries=[],
             datas=[('potatowatts.ico', '.'), ('image_1.png', '.')],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='reels_downloader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='potatowatts.ico')

app = BUNDLE(exe,
             name='reels_downloader.app',
             icon=None,
             bundle_identifier=None)
