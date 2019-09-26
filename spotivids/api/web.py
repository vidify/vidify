import os
import sys
import time
import logging
from typing import Union

from spotipy import Spotify, Scope, scopes, Token, Credentials
from spotipy.util import prompt_for_user_token, RefreshingToken

from ..utils import split_title, ConnectionNotReady
from ..youtube import YouTube


class WebAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 logger: logging.Logger, client_id: str, client_secret: str,
                 redirect_uri: str, auth_token: str, expiration: int) -> None:
        """
        The parameters are saved in the class and the main song properties
        are created. The logger is an instance from the logging module,
        configured to show debug or error messages.

        It includes `player`, the VLC or mpv window, so that some actions can
        be controlled from the API more intuitively, like automatic
        pausing/playing/skipping when the API detects it.

        It handles the Spotipy authentication. The auth scope is the least
        needed to access the currently playing song and the redirect uri
        is always on localhost, since it's an offline application.
        """

        self._logger = logger
        self.player = player

        self.artist = ""
        self.title = ""
        self._position = 0
        self.is_playing = False

        # Trying to load the env variables
        if not client_id:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
        if not client_secret:
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if not redirect_uri:
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

        scope = Scope(scopes.user_read_currently_playing)

        # Trying to use the config auth token
        if expiration is None:
            expired = True
        else:
            expired = (expiration - int(time.time())) < 60

        if auth_token not in (None, "") and not expired:
            data = {
                'access_token': auth_token,
                'token_type': 'Bearer',
                'scope': scope,
                'expires_in': expiration - int(time.time())
            }
            creds = Credentials(self._client_id, self._client_secret,
                                self._redirect_uri)
            self._token = RefreshingToken(Token(data), creds)
        else:
            print("To authorize the Spotify API, you'll have to log-in"
                  " in the new tab that is going to open in your browser.\n"
                  "Afterwards, just paste the contents of the URL you have"
                  " been redirected to, something like"
                  " 'http://localhost:8888/callback/?code=AQAa5v...'")
            self._token = prompt_for_user_token(
                client_id, client_secret, redirect_uri, scope)

        self._spotify = Spotify(self._token)

    @property
    def position(self) -> int:
        self._refresh_metadata()
        return self._position

    def connect(self) -> None:
        """
        An initial metadata refresh is run. It throws a `ConnectionNotReady`
        exception if no songs are playing in that moment.
        """

        try:
            self._refresh_metadata()
        except (AttributeError, TypeError):
            raise ConnectionNotReady("No song currently playing")

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata of the player: artist, title, whether
        it's playing or not, and the current position.

        Some local songs don't have an artist name so `split_title`
        is called in an attempt to manually get it from the title.
        """

        metadata = self._spotify.playback_currently_playing()
        self.artist = metadata.item.artists[0]
        self.title = metadata.item.name

        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self._position = metadata.progress_ms
        self.is_playing = metadata.is_playing

    def wait(self) -> None:
        """
        Waits until a new song is played. The API doesn't currently have an
        asynchronous way to recieve events like pausing the video or changing
        the position, so the wait function has to manually refresh every
        second and may be a bit inaccurate.

        It checks if the playback status changed (playing/paused), the
        song position, which will be ignored unless the difference
        is larger than the actual elapsed time or backward, and the song itself
        to break the loop. Said loop is also broken with a KeyboardInterrupt
        from the user.

        The elapsed time has to be manually checked because some systems
        may lag and change positions when they shouldn't.
        """

        self._logger.info("Starting loop")
        artist = self.artist
        title = self.title
        try:
            while True:
                timer = time.time()
                position = self._position
                is_playing = self.is_playing
                time.sleep(1)

                self._refresh_metadata()

                if self.artist != artist or self.title != title:
                    break

                if self.is_playing != is_playing:
                    self.player.toggle_pause()

                diff = self._position - position
                time_diff = int((time.time() - timer) * 1000)
                if diff >= time_diff + 100 or diff < 0:
                    self.player.position = self._position
        except KeyboardInterrupt:
            self._logger.info("Quitting from web player loop")
            sys.exit(0)


def play_videos_web(player: Union['VLCPlayer', 'MpvPlayer'], youtube: YouTube) -> None:
    """
    Playing videos with the Web API (optional).

    Unlike the other APIs, the position can be requested and the video is
    synced easily.
    """

    spotify = WebAPI(player, logger, config.client_id,
                     config.client_secret, config.redirect_uri,
                     config.auth_token, config.expiration)

    msg = "Waiting for a Spotify song to play..."
    if not wait_for_connection(spotify.connect, msg):
        return

    # Saves the auth token inside the config file for future usage
    config.write_file('WebAPI', 'client_secret',
                      spotify._client_secret)
    config.write_file('WebAPI', 'client_id',
                      spotify._client_id)
    if spotify._redirect_uri != config._options.redirect_uri.default:
        config.write_file('WebAPI', 'redirect_uri',
                          spotify._redirect_uri)
    config.write_file('WebAPI', 'auth_token',
                      spotify._token.access_token)
    config.write_file('WebAPI', 'expiration',
                      spotify._token.expires_at)

    while True:
        url = youtube.get_url(spotify.artist, spotify.title)
        player.start_video(url, spotify.is_playing)

        offset = spotify.position
        player.position = offset

        if config.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        spotify.wait()
