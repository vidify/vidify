# -*- mode: python ; coding: utf-8 -*-
# Example spec file used to build Vidify for Windows. See BUILDING.md for more.

block_cipher = None

a = Analysis(['..\\vidify\\__main__.py'],
             pathex=['C:\\Users\\quini\\Downloads\\vidify'],
             binaries=[],
             datas=[('C:/Program Files/VideoLAN/VLC/libvlc.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/axvlc.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/libvlccore.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/npvlc.dll', '.'),
                    ('C:/Program Files/VideoLAN/VLC/plugins', 'plugins')
             ],
             hiddenimports=['six', 'vidify.player.vlc', 'tekore'],
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
          icon='../vidify/gui/res/icon16x16.ico',
          exclude_binaries=True,
          name='vidify',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='vidify')
