import os
import time
import logging
from requests import HTTPError
from typing import Union

from spotipy import Spotify, Scope, scopes, Token, Credentials
from spotipy.util import prompt_for_user_token, RefreshingToken

from spotivids import config
from spotivids.api import split_title, ConnectionNotReady, wait_for_connection
from spotivids.gui import MainWindow
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube


class WebAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 client_id: str = None, client_secret: str = None,
                 redirect_uri: str = None, auth_token: str = None,
                 expiration: int = None) -> None:
        """
        It includes `player`, the VLC or mpv window to play videos and control
        it when the song status changes. The `Youtube` object is also needed
        to play the videos.

        This also handles the Spotipy authentication.
        """

        self._logger = logging.getLogger('spotivids')
        self.player = player
        self.artist = ""
        self.title = ""
        self._position = 0
        self.is_playing = False
        self._youtube = YouTube(config.debug, config.width, config.height)

        # Trying to load the env variables
        if client_id is None:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
        if client_secret is None:
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if redirect_uri is None:
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

        if None in (client_id, client_secret, redirect_uri):
            raise Exception("The auth info was incomplete")

        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

        # The least needed to access the currently playing song
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

    def connect(self) -> None:
        """
        An initial metadata refresh is run. It raises `ConnectionNotReady`
        if no songs are playing in that moment.
        """

        try:
            self._refresh_metadata()
        except AttributeError:
            raise ConnectionNotReady("No song currently playing")

    @property
    def position(self) -> int:
        self._refresh_metadata()
        return self._position

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata of the player: artist, title, whether
        it's playing or not, and the current position.

        Some local songs don't have an artist name so `split_title`
        is called in an attempt to manually get it from the title.
        """

        metadata = self._spotify.playback_currently_playing()
        self.artist = metadata.item.artists[0].name
        self.title = metadata.item.name

        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self._position = metadata.progress_ms
        self.is_playing = metadata.is_playing

    def play_video(self) -> None:
        """
        """

        url = self._youtube.get_url(self.artist, self.title)
        self.player.position = self.position
        self.player.start_video(url, self.is_playing)

        if config.lyrics:
            print_lyrics(self.artist, self.title)

    def event_loop(self) -> None:
        """
        A callable event loop that checks if changes happen. This is called
        every 0.5 seconds from the QT window.

        It checks if the playback status changed (playing/paused), if a new
        song started to call `play_video` and the song position. The position
        changes will be ignored unless the difference is larger than the real
        elapsed time or if it was backwards. This is done because some systems
        may lag more than others and a fixed time difference would cause
        errors.
        """

        timer = time.time()
        artist = self.artist
        title = self.title
        position = self._position
        is_playing = self.is_playing
        self._refresh_metadata()

        # The first check should be if the song has ended to not touch
        # anything else that may not actually be true.
        if self.artist != artist or self.title != title:
            self.play_video()

        if self.is_playing != is_playing:
            self.player.toggle_pause()

        diff = self._position - position
        time_diff = int((time.time() - timer) * 1000)
        if diff >= (time_diff + 100) or diff < 0:
            self.player.position = self._position


def play_videos_web(player: Union['VLCPlayer', 'MpvPlayer'],
                    window: MainWindow) -> None:
    """
    Playing videos with the Web API (optional).

    Initializes the Web API and plays the first video.
    Also starts the event loop to detect changes and play new videos.
    """

    spotify = WebAPI(player, config.client_id, config.client_secret,
                     config.redirect_uri, config.auth_token, config.expiration)

    # Checks if Spotify is closed and if the auth details are valid
    msg = "Waiting for a Spotify song to play..."
    try:
        if not wait_for_connection(spotify.connect, msg):
            return
    except HTTPError as e:
        if e.response.status_code != 401:
            raise
        spotify = WebAPI(player, config.client_id, config.client_secret,
                         config.redirect_uri)
        if not wait_for_connection(spotify.connect, msg):
            return

    # Saves the used credentials inside the config file for future usage
    config.write_file('WebAPI', 'client_secret', spotify._client_secret)
    config.write_file('WebAPI', 'client_id', spotify._client_id)
    if spotify._redirect_uri != config._options.redirect_uri.default:
        config.write_file('WebAPI', 'redirect_uri', spotify._redirect_uri)
    config.write_file('WebAPI', 'auth_token', spotify._token.access_token)
    config.write_file('WebAPI', 'expiration', spotify._token.expires_at)

    spotify.play_video()
    window.start_event_loop(spotify.event_loop, 1000)
