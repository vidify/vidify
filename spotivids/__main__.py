import sys
import time
import logging
from typing import Callable, Union

import lyricwikia
from PySide2.QtWidgets import QApplication

from .config import Config
from .utils import stderr_redirected, ConnectionNotReady
from .gui import MainWindow
from .youtube import YouTube


# Cross platform info
BSD = sys.platform.find('bsd') != -1
LINUX = sys.platform.startswith('linux')
MACOS = sys.platform.startswith('darwin')
WINDOWS = sys.platform.startswith('win')

# Initialization and parsing of the config from arguments and config file
config = Config()
config.parse()

# Logger initialzation with precise milliseconds handler
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
level = logging.DEBUG if config.debug else logging.ERROR
logger.setLevel(level)



def format_name(artist: str, title: str) -> str:
    """
    Some local songs may not have an artist name so the formatting
    has to be different.
    """

    return title if artist in (None, '') else f"{artist} - {title}"


def print_lyrics(artist: str, title: str) -> None:
    """
    Using lyricwikia to get lyrics.

    Colors are not displayed on Windows because it doesn't support ANSI
    escape codes and importing colorama isn't worth it currently.
    """

    name = format_name(artist, title)

    if WINDOWS:
        print(f">> {name}")
    else:
        print(f"\033[4m{name}\033[0m")

    try:
        print(lyricwikia.get_lyrics(artist, title) + "\n")
    except (lyricwikia.LyricsNotFound, AttributeError):
        print("No lyrics found\n")


def wait_for_connection(connect: Callable, msg: str,
                        attempts: int = 30) -> bool:
    """
    Waits for a Spotify session to be opened or for a song to play.
    Times out after `attempts` seconds to avoid infinite loops or
    too many API/process requests.

    Returns True if the connection was succesfull and False otherwise.
    """

    counter = 0
    while counter < attempts:
        try:
            connect()
        except ConnectionNotReady:
            if counter == 0:
                print(msg)
            counter += 1
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        else:
            return True
    else:
        print("Timed out")

    return False


def choose_platform() -> None:
    """
    Chooses a platform and player and starts the corresponding API function.
    """

    app = QApplication()

    if config.use_mpv:
        from .player.mpv import MpvPlayer
        player = MpvPlayer(logger, config.mpv_flags, config.fullscreen)
    else:
        from .player.vlc import VLCPlayer
        player = VLCPlayer(logger, config.vlc_args, config.fullscreen)

    window = MainWindow(player, config.width, config.height)
    window.show()

    youtube = YouTube(config.debug, config.width, config.height)
    if (BSD or LINUX) and not config.use_web_api:
        from .api.linux import play_videos_linux
        play_videos_linux(player, youtube)
    elif (WINDOWS or MACOS) and not config.use_web_api:
        from .api.swspotify import play_videos_swspotify
        play_videos_swspotify(player, youtube)
    else:
        from .api.web import play_videos_web
        play_videos_web(player, youtube)

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
