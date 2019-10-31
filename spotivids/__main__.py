"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import os
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
    #   1. Waits for the user to start Spotify or play a song with it
    #      (until spotify.connect() doesn't raise errors).
    #   2. An initial function and its arguments will be called if the
    #      connection was successful.
    #   3. An event loop may be started. The event loops check for updates
    #      in the Spotify metadata to for example pause the video when
    #      the song does. DBus doesn't need one because it uses GLib's loop.
    logging.info("Initializing the API")
    if (BSD or LINUX) and not config.use_web_api:
        from spotivids.api.linux import DBusAPI, play_videos_linux
        spotify = DBusAPI(player, youtube, config.lyrics)
        msg = "Waiting for a Spotify session to be ready..."
        window.start(spotify.connect, play_videos_linux, spotify, message=msg)

    elif (WINDOWS or MACOS) and not config.use_web_api:
        from spotivids.api.swspotify import SwSpotifyAPI
        spotify = SwSpotifyAPI(player, youtube, config.lyrics)
        msg = "Waiting for a Spotify song to play..."
        window.start(spotify.connect, spotify.play_video, message=msg,
                     event_loop=spotify.event_loop, event_interval=500)

    else:
        from spotivids.api.web import play_videos_web, get_token, WebAPI
        # Trying to load the env variables
        if config.client_id is None:
            config.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        if config.client_secret is None:
            config.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if config.redirect_uri is None:
            config.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

        # Trying to reuse a previously generated token
        token = get_token(config.auth_token, config.expiration,
                          config.client_id, config.client_secret,
                          config.redirect_uri)

        if token is not None:
            # If the previous token was valid, the API can already start
            logging.info("Reusing a previously generated token")
            spotify = WebAPI(player, youtube, token, config.lyrics)
            msg = "Waiting for a Spotify song to play..."
            window.start(spotify.connect, play_videos_web, spotify, config,
                         message=msg, event_loop=spotify.event_loop,
                         event_interval=1000)
        else:
            # Otherwise, the credentials are obtained with the GUI. When
            # a valid auth token is ready, the GUI will initialize the API
            # automatically exactly like above. The GUI won't ask for a
            # redirect URI for now.
            logging.info("Asking the user for credentials")
            window.get_token(config, youtube)

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
