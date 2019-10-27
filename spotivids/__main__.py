"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import sys

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

from spotivids import config, stderr_redirected, BSD, LINUX, MACOS, WINDOWS
from spotivids.gui.window import MainWindow


def choose_platform() -> None:
    """
    Chooses a platform and player and starts the corresponding API function.
    """

    app = QApplication()
    app.setWindowIcon(QIcon('spotivids/gui/icon.svg'))

    if config.use_mpv:
        from spotivids.player.mpv import MpvPlayer
        player = MpvPlayer(config.mpv_flags)
    else:
        from spotivids.player.vlc import VLCPlayer
        player = VLCPlayer(config.vlc_args)

    window = MainWindow(player, config.width, config.height, config.fullscreen)
    window.show()

    if (BSD or LINUX) and not config.use_web_api:
        from spotivids.api.linux import play_videos_linux
        play_videos_linux(player)
    elif (WINDOWS or MACOS) and not config.use_web_api:
        from spotivids.api.swspotify import play_videos_swspotify
        play_videos_swspotify(player, window)
    else:
        from spotivids.api.web import play_videos_web
        play_videos_web(player, window)

    sys.exit(app.exec_())


def main() -> None:
    """
    Redirects stderr to /dev/null if debug is turned off, since
    sometimes VLC will throw non-fatal errors even when configured
    to be quiet.
    """

    if config.debug:
        choose_platform()
    else:
        with stderr_redirected():
            choose_platform()


if __name__ == '__main__':
    main()
