"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import sys
import logging

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

from spotivids import stderr_redirected, BSD, LINUX, MACOS, WINDOWS
from spotivids.config import Config
from spotivids.youtube import YouTube
from spotivids.gui.window import MainWindow


def choose_platform(config: Config) -> None:
    """
    Main function: chooses a platform and player and starts the corresponding
    API function. Also initializes the logger, youtube and GUI.
    """

    # Logger initialzation with precise milliseconds handler.
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.ERROR,
                        format="[%(asctime)s.%(msecs)03d] %(levelname)s:"
                        " %(message)s", datefmt="%H:%M:%S")

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

    # The YouTube object to obtain song videos
    youtube = YouTube(config.debug, config.width, config.height)

    # Choosing the platform
    if (BSD or LINUX) and not config.use_web_api:
        from spotivids.api.linux import play_videos_linux
        play_videos_linux(player, youtube, config)
    elif (WINDOWS or MACOS) and not config.use_web_api:
        from spotivids.api.swspotify import play_videos_swspotify
        play_videos_swspotify(player, window, youtube, config)
    else:
        from spotivids.api.web import play_videos_web
        play_videos_web(player, window, youtube, config)

    sys.exit(app.exec_())


def main() -> None:
    """
    Redirects stderr to /dev/null if debug is turned off, since
    sometimes VLC will throw non-fatal errors even when configured
    to be quiet.
    """

    # Initialization and parsing of the config from arguments and config file
    config = Config()
    config.parse()

    if config.debug:
        choose_platform(config)
    else:
        with stderr_redirected():
            choose_platform(config)


if __name__ == '__main__':
    main()
