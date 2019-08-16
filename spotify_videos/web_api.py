import sys
import time

from . import spotipy
from .spotipy import util

from .vlc_player import VLCPlayer
from .utils import split_title, ConnectionNotReady


# Web player with the Spotify properties (other OS than Linux)
class WebAPI:
    """
    The Web API class, containing all information from the web API.

    The logger is an instance from the logging module, configured
    to show debug or error messages.

    It includes `player`, the VLC window, so that some actions can
    be controlled from the API more intuitively, like automatic
    pausing/playing/skipping when the API detects it.
    """

    def __init__(self, player: VLCPlayer, logger: 'logging.Logger',
                 username: str, client_id: str, client_secret: str) -> None:
        """
        The parameters are saved in the class and the main song properties
        are created.

        Handles the Spotipy authentication.
        The Spotipy trace is disabled even in debug mode because it outputs
        too much unnecessary information.

        The auth scope is the least needed to access the currently playing song
        and the redirect uri is always on localhost, since it's an offline
        application.
        """

        self._logger = logger
        self.player = player

        self.artist = ""
        self.title = ""
        self.position = 0
        self.is_playing = False

        scope = 'user-read-currently-playing'
        redirect_uri = 'http://localhost:8888/callback/'
        self._token = util.prompt_for_user_token(
            username, scope, client_id, client_secret, redirect_uri)

        if self._token:
            self._logger.info("Authorized correctly")
            self._spotify = spotipy.Spotify(auth=self._token)
        else:
            raise Exception(f"Can't get token for {username}. "
                            "Please check the README for more info.")

        self._spotify.trace = False

    def do_connect(self) -> None:
        """
        An initial metadata refresh is run. It throws a `ConnectionNotReady`
        exception if no songs are playing in that moment.
        """

        try:
            self._refresh_metadata()
        except TypeError:
            raise ConnectionNotReady("No song currently playing")

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata and status of the player: artist,
        title and current position.

        Some local songs don't have an artist name so `split_title`
        is called in an attempt to manually get it from the title.
        """

        metadata = self._spotify.current_user_playing_track()
        self.artist = metadata['item']['artists'][0]['name']
        self.title = metadata['item']['name']

        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self.position = metadata['progress_ms']
        self.is_playing = metadata['is_playing']

    def get_position(self) -> int:
        """
        Returns the position in milliseconds of the player.
        """

        self._refresh_metadata()
        return self.position

    def wait(self) -> None:
        """
        Waits until a new song is played. The API doesn't currently have an
        asynchronous way to recieve events like pausing the video or changing
        the position, so the wait function has to manually refresh every
        second and may be a bit inaccurate.

        It checks if the playback status changed (playing/paused), the
        song position, which will be ignored unless the difference
        is larger than 3 seconds or backward, and the song itself
        to break the loop. Said loop is also broken with a
        KeyboardInterrupt from the user.
        """

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
