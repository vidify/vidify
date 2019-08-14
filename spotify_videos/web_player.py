import sys
import time

from . import spotipy
from .spotipy import util

from .vlc import VLCWindow
from .utils import split_title


# Web player with the Spotify properties (other OS than Linux)
class WebPlayer:
    """
    The Web API class, containing all information from the web API.

    The logger is an instance from the logging module, configured
    to show debug or error messages.

    It includes `player`, the VLC window, so that some actions can
    be controlled from the API more intuitively, like automatic
    pausing/playing/skipping when the API detects it.
    """

    def __init__(self, player: VLCWindow, logger: 'logging.Logger',
            username: str, client_id: str, client_secret: str) -> None:
        
        self._logger = logger

        # Main player properties
        self.artist = ""
        self.title = ""
        self.position = 0
        self.is_playing = False
        self.player = player

        # Creation of the Spotify token
        self._token = util.prompt_for_user_token(
                username,
                scope = 'user-read-currently-playing',
                client_id = client_id,
                client_secret = client_secret,
                redirect_uri = "http://localhost:8888/callback/"
        )
        if self._token:
            self._logger.info("Authorized correctly")
            self._spotify = spotipy.Spotify(auth = self._token)
        else:
            logger.error(f"Can't get token for {username}. "
                          "Please check the README for more.")
            sys.exit(1)

        self._spotify.trace = False
        self._refresh_metadata()

    # Refreshes the metadata and status of the player (artist, title, position)
    def _refresh_metadata(self) -> None:
        # Waiting for a song to start
        first_msg = True
        while True:
            metadata = self._spotify.current_user_playing_track()

            if metadata is not None:
                break

            if first_msg:
                print("No song currently playing.")
                first_msg = False

        self.artist = metadata['item']['artists'][0]['name']
        self.title = metadata['item']['name']

        # Some local songs have both the artist and the title inside
        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self.position = metadata['progress_ms']
        self.is_playing = metadata['is_playing']

    # Returns the position in milliseconds of the player
    def get_position(self) -> int:
        self._refresh_metadata()
        return self.position

    # Waits until a new song is played, checking for changes every second
    def wait(self) -> None:
        try:
            while True:
                time.sleep(1)
                artist = self.artist
                title = self.title
                is_playing = self.is_playing
                position = self.position
                self._refresh_metadata()

                if self.is_playing != is_playing:
                    self._logger.info("Paused/Played video")
                    self.player.toggle_pause()

                # Changes position if the difference is considered
                # enough to be a manual skip (>= 3secs, < 0 secs)
                diff = self.position - position
                if diff >= 3000 or diff < 0:
                    self._logger.info("Position changed")
                    self.player.set_position(self.position)

                if self.artist != artist or self.title != title:
                    self._logger.info("Song changed")
                    break
        except KeyboardInterrupt:
            self._logger.info("Quitting from web player loop")
            sys.exit(0)

