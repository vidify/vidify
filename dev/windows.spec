# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['..\\spotivids\\__main__.py'],
             pathex=['C:\\Users\\quini\\Downloads\\spotify-music-videos'],
             binaries=[],
             datas=[('C:/Program Files/VideoLAN/VLC/libvlc.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/axvlc.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/libvlccore.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/npvlc.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/plugins', 'plugins')
             ],
             hiddenimports=['six'],
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
          [],
          icon='../spotivids/gui/res/icon.ico',
          exclude_binaries=True,
          name='spotivids',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='spotivids')
