import sys
import time
import logging
from typing import Union

from spotipy import Spotify, Credentials, Scope, scopes
from spotipy.util import prompt_for_user_token

from ..player.vlc import VLCPlayer
from ..player.mpv import MpvPlayer
from ..utils import split_title, ConnectionNotReady


class WebAPI(object):
    """
    The Web API class, containing all information from the web API.

    The logger is an instance from the logging module, configured
    to show debug or error messages.

    It includes `player`, the VLC or mpv window, so that some actions can
    be controlled from the API more intuitively, like automatic
    pausing/playing/skipping when the API detects it.
    """

    def __init__(self, player: Union[VLCPlayer, MpvPlayer],
                 logger: logging.Logger, client_id: str, client_secret: str,
                 redirect_uri: str, auth_token: str) -> None:
        """
        The parameters are saved in the class and the main song properties
        are created.

        Handles the Spotipy authentication.

        The auth scope is the least needed to access the currently playing song
        and the redirect uri is always on localhost, since it's an offline
        application.
        """

        self._logger = logger
        self.player = player

        self.artist = ""
        self.title = ""
        self._position = 0
        self.is_playing = False

        # Trying to use the config auth token
        if auth_token in (None, ""):
            pass
            # TODO
        else:
            scope = Scope(scopes.user_read_currently_playing)
            print("To authorize the Spotify API, you'll have to log-in"
                  " in the new tab that is going to open in your browser.\n"
                  "Afterwards, just paste the contents of the URL you have"
                  " been redirected to, something like"
                  " 'http://localhost:8888/callback/?code=AQAa5v...'")
            self._token = prompt_for_user_token(
                client_id, client_secret, redirect_uri, scope)

            if self._token:
                print("Authorized correctly")
                self._spotify = Spotify(self._token.access_token)
            else:
                raise Exception(f"Couldn't get token."
                                " Please check the README for more info.")

    def connect(self) -> None:
        """
        An initial metadata refresh is run. It throws a `ConnectionNotReady`
        exception if no songs are playing in that moment.
        """

        try:
            self._refresh_metadata()
        except AttributeError:
            raise ConnectionNotReady("No song currently playing")

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata of the player: artist, title, whether
        it's playing or not, and the current position.

        Some local songs don't have an artist name so `split_title`
        is called in an attempt to manually get it from the title.
        """

        metadata = self._spotify.playback_currently_playing()
        self.artist = metadata['item']['artists'][0]['name']
        self.title = metadata['item']['name']

        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self._position = metadata['progress_ms']
        self.is_playing = metadata['is_playing']

    @property
    def position(self) -> int:
        """
        Returns the position in milliseconds of the player.
        """

        self._refresh_metadata()
        return self._position

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
                position = self._position
                self._refresh_metadata()

                if self.is_playing != is_playing:
                    self._logger.info("Paused/Played video")
                    self.player.toggle_pause()

                diff = self._position - position
                if diff >= 3000 or diff < 0:
                    self._logger.info("Position changed")
                    self.player.position = self._position

                if self.artist != artist or self.title != title:
                    self._logger.info("Song changed")
                    break
        except KeyboardInterrupt:
            self._logger.info("Quitting from web player loop")
            sys.exit(0)
