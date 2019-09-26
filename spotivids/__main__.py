import sys

from PySide2.QtWidgets import QApplication

from . import config, stderr_redirected, BSD, LINUX, MACOS, WINDOWS
from .gui import MainWindow


def choose_platform() -> None:
    """
    Chooses a platform and player and starts the corresponding API function.
    """

    app = QApplication()

    if config.use_mpv:
        from .player.mpv import MpvPlayer
        player = MpvPlayer(config.mpv_flags, config.fullscreen)
    else:
        from .player.vlc import VLCPlayer
        player = VLCPlayer(config.vlc_args, config.fullscreen)

    window = MainWindow(player, config.width, config.height)
    window.show()

    if (BSD or LINUX) and not config.use_web_api:
        from .api.linux import play_videos_linux
        play_videos_linux(player)
    elif (WINDOWS or MACOS) and not config.use_web_api:
        from .api.swspotify import play_videos_swspotify
        play_videos_swspotify(player, config.lyrics, config.debug)
    else:
        from .api.web import play_videos_web
        play_videos_web(player)

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
