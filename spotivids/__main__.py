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
from spotivids.gui import Res
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
    app.setWindowIcon(QIcon(Res.icon))

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

    # Choosing the platform: initializes the corresponding API and calls
    # window.start(). This does three main things:
    #   * Waits for the user to start Spotify or play a song with it
    #     (until spotify.connect() doesn't raise errors).
    #   * An initial function and its arguments will be called if the
    #     connection was successful.
    #   * An event loop may be started. The event loops check for updates
    #     in the Spotify metadata to for example pause the video when
    #     the song does. DBus doesn't need one because it uses GLib's loop.
    logging.info("Initializing the API")
    if (BSD or LINUX) and not config.use_web_api:
        from spotivids.api.linux import DBusAPI
        spotify = DBusAPI(player, youtube, config.lyrics)
        msg = "Waiting for a Spotify session to be ready..."
        window.start(spotify.connect, spotify.play_video, message=msg)
    elif (WINDOWS or MACOS) and not config.use_web_api:
        from spotivids.api.swspotify import SwSpotifyAPI
        spotify = SwSpotifyAPI(player, youtube, config.lyrics)
        msg = "Waiting for a Spotify song to play..."
        window.start(spotify.connect, spotify.play_video, message=msg,
                     event_loop=spotify.event_loop, event_interval=500)
    else:
        from spotivids.api.web import play_videos_web, WebAPI
        spotify = WebAPI(player, youtube, config.lyrics, config.client_id,
                         config.client_secret, config.redirect_uri,
                         config.auth_token, config.expiration)
        msg = "Waiting for a Spotify song to play..."
        # `play_videos_web` also saves the credentials
        window.start(spotify.connect, play_videos_web, spotify, config,
                     message=msg, event_loop=spotify.event_loop,
                     event_interval=1000)

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
