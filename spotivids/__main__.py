"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import os
import sys
import logging
from importlib import import_module

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

from spotivids import stderr_redirected, BSD, LINUX, MACOS, WINDOWS
from spotivids.config import Config
from spotivids.youtube import YouTube
from spotivids.player import Players, PlayerNotFoundError
from spotivids.player.generic import PlayerBase
from spotivids.api import APIs
from spotivids.api.generic import APIBase
from spotivids.gui import Res
from spotivids.gui.window import MainWindow


def choose_player(config: Config) -> PlayerBase:
    """
    Choosing a player from the list.
    """

    def initialize_player(player: Players) -> PlayerBase:
        """
        Initializing an abstract player instance with the information inside
        the `player` enumeration object.
        """

        # Importing the module first
        mod = import_module(player.module)
        # Then obtaining the player class
        cls = getattr(mod, player.class_name)
        # No other arguments are needed for now, so all this does is initialize
        # the player with the config flags (if present).
        try:
            flags = getattr(config, player.flags_name)
        except AttributeError:
            obj = cls()
        finally:
            obj = cls(flags)
        return obj

    # Finding the config player and initializing it.
    for player in Players:
        if config.player.lower() == player.name.lower():
            return initialize_player(player)

    raise PlayerNotFoundError


def choose_platform(config: Config, player: PlayerBase) -> None:
    """
    Main function: chooses a platform and player and starts the corresponding
    API function. Also initializes the logger, youtube and GUI.
    """

    # Logger initialzation with precise milliseconds handler.
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.ERROR,
                        format="[%(asctime)s.%(msecs)03d] %(levelname)s:"
                        " %(message)s", datefmt="%H:%M:%S")

    # Initializing the Qt application
    app = QApplication()
    app.setWindowIcon(QIcon(Res.icon))

    # Opening the window with the GUI
    window = MainWindow(player, config.width, config.height, config.fullscreen,
                        config.stay_on_top)
    window.show()

    # The YouTube object to obtain song videos
    youtube = YouTube(config.debug, config.width, config.height)

    # TODO
    available = []
    for API in APIData:
        if CURRENT_PLATFORM in API.platforms:
            # module = importlib.importlib(API.module)
            available.append(API)

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
        # play_videos_linux() is needed to start the event loop
        window.start(spotify.connect, play_videos_linux, spotify, message=msg)
    elif (WINDOWS or MACOS) and not config.use_web_api:
        from spotivids.api.swspotify import SwSpotifyAPI
        spotify = SwSpotifyAPI(player, youtube, config.lyrics)
        msg = "Waiting for a Spotify song to play..."
        window.start(spotify.connect, spotify.play_video, message=msg,
                     event_loop=spotify.event_loop, event_interval=500)
    else:
        from spotivids.api.web import get_token, WebAPI
        # Trying to reuse a previously generated token
        token = get_token(config.auth_token, config.refresh_token,
                          config.expiration, config.client_id,
                          config.client_secret, config.redirect_uri)

        if token is not None:
            # If the previous token was valid, the API can already start
            logging.info("Reusing a previously generated token")
            spotify = WebAPI(player, youtube, token, config.lyrics)
            msg = "Waiting for a Spotify song to play..."
            window.start(spotify.connect, spotify.play_video, message=msg,
                         event_loop=spotify.event_loop, event_interval=1000)
        else:
            # Otherwise, the credentials are obtained with the GUI. When
            # a valid auth token is ready, the GUI will initialize the API
            # automatically exactly like above. The GUI won't ask for a
            # redirect URI for now.
            logging.info("Asking the user for credentials")
            window.get_token(config, youtube)

    sys.exit(app.exec_())


@contextmanager
def stderr_redirected(to: str = os.devnull) -> None:
    """
    Redirecting stderr without leaks. This is used because sometimes VLC
    will print non-critical error messages even when told to be quiet.
    """

    fd = sys.stderr.fileno()

    def _redirect_stderr(to: str) -> None:
        sys.stderr.close()  # + implicit flush()
        os.dup2(to.fileno(), fd)  # fd writes to 'to' file
        sys.stderr = os.fdopen(fd, 'w')  # Python writes to fd

    with os.fdopen(os.dup(fd), 'w') as old_stderr:
        with open(to, 'w') as file:
            _redirect_stderr(to=file)
        try:
            # Allow code to be run with the redirected stderr
            yield
        finally:
            # Restore stderr. Some flags may change
            _redirect_stderr(to=old_stderr)


def main() -> None:
    # Initialization and parsing of the config from arguments and config file
    config = Config()
    config.parse()

    def init() -> None:
        player = choose_player(config)
        choose_api(config, p)

    # Redirects stderr to /dev/null if debug is turned off, since sometimes
    # VLC will print non-fatal errors even when configured to be quiet.
    if config.debug:
        init()
    else:
        with stderr_redirected():
            init()


if __name__ == '__main__':
    main()
