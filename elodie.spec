# -*- mode: python -*-

block_cipher = None


a = Analysis(['elodie/elodie.py'],
             pathex=['/Users/jaisenmathai/dev/tools/elodie'],
             binaries=None,
             datas=[('configs/ExifTool_config', 'configs')],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='elodie',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='elodie')
