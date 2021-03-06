# -*- mode: python ; coding: utf-8 -*-
# Don't use this file directly. Please run build_windows.ps1 to apply the
# necessary patches before building.

block_cipher = None

a = Analysis(['./vidify/__main__.py', './vidify/player/vlc.py',
              './vidify/api/spotify/swspotify.py',
              './vidify/api/spotify/web.py'],
             pathex=[''],
             binaries=[],
             datas=[('vidify/gui/res', 'vidify/gui/res')],
             hiddenimports=['appdirs', 'qtpy', 'pyqt5', 'pyqtwebengine', 'six',
                            'tekore', 'mpv',  'zeroconf',
                            'vidify.player.external', 'vidify.player.mpv',
                            'vidify.api.spotify.web',
                            'vidify.api.spotify.swspotify'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PySide2'],
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
