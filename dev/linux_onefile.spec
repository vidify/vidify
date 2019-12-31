# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['../vidify/__main__.py'],
             pathex=['/home/mario/Programming/vidify/dev'],
             binaries=[],
             datas=[('/usr/lib/libmpv.so', '.'),
                    ('/usr/lib/libvlc.so', '.'),
                    ('/usr/lib/libvlccore.so', '.'),
                    ('/usr/lib/vlc/plugins', 'plugins'),
                    ('/usr/lib/vlc/libvlc_pulse.so', '.'),
                    ('/usr/lib/vlc/libvlc_vdpau.so', '.'),
             ],
             hiddenimports=['appdirs', 'qtpy', 'vlc', 'mpv', 'packaging',
                            'pydbus', 'gi', 'lyricwikia', 'six'],
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
          name='vidify',
          icon="../vidify/gui/res/icon.svg",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)
