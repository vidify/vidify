# -*- mode: python ; coding: utf-8 -*-
# Don't use this file directly. Please run build_linux.sh to apply the
# necessary patches before building.

block_cipher = None

a = Analysis(['vidify/__main__.py', 'vidify/player/mpv.py',
              'vidify/player/vlc.py', 'vidify/api/mpris.py',
              'vidify/api/spotify/web.py', 'vidify/audiosync.py'],
             pathex=[''],
             binaries=[],
             datas=[('/usr/lib/libmpv.so', '.'),
                    ('/usr/lib/libvlc.so', '.'),
                    ('/usr/lib/libvlccore.so', '.'),
                    ('/usr/lib/vlc/plugins', 'plugins'),
                    ('/usr/lib/vlc/libvlc_pulse.so', '.'),
                    ('/usr/lib/vlc/libvlc_vdpau.so', '.'),
                    ('vidify/gui/res', 'res')
             ],
             hiddenimports=['appdirs', 'qtpy', 'vlc', 'mpv', 'six',
                            'audiosync', 'pydbus', 'gi', 'lyricwikia',
                            'zeroconf', 'vidify.audiosync',
                            'vidify.player.external', 'vidify.player.mpv',
                            'vidify.player.vlc', 'vidify.api.mpris',
                            'vidify.api.spotify.web'],
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
          icon="../vidify/gui/res/icon.svg",
          exclude_binaries=True,
          name='vidify',
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
               name='vidify')
