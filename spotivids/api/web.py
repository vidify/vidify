"""
This module implements the official web API, using the `spotipy` module.
The web API provides much more information about the Spotify player but
it's limited in terms of usabilty:
    * The user has to sign in and manually set it up
    * Only Spotify Premium users are able to use some functions
    * API calls are limited, so it's not as responsive

The API is controlled from the `play_videos_web` function. The overall
usage and bevhavior of the class should be the same for all the APIs so
that they can be used interchangeably.
"""

import os
import time
import logging
from typing import Union

from spotipy import Spotify, Scope, scopes, Token, Credentials
from spotipy.util import prompt_for_user_token, RefreshingToken

from spotivids.api import split_title, ConnectionNotReady, wait_for_connection
from spotivids.config import Config
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube
from spotivids.gui.window import MainWindow


class WebAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 youtube: YouTube, show_lyrics: bool = True,
                 client_id: str = None, client_secret: str = None,
                 redirect_uri: str = None, auth_token: str = None,
                 expiration: int = None) -> None:
        """
        It includes `player`, the VLC or mpv window to play videos and control
        it when the song status changes.

        This also handles the Spotipy authentication.
        """

        self.player = player
        self.artist = ""
        self.title = ""
        self._position = 0
        self.is_playing = False

        #  The `YouTube` object is also needed to obtain the URL of the songs
        self._youtube = youtube
        self._show_lyrics = show_lyrics
        self._event_timestamp = time.time()

        # Trying to load the env variables
        if client_id is None:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
        if client_secret is None:
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if redirect_uri is None:
            redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

        if None in (client_id, client_secret, redirect_uri):
            raise AttributeError("The auth info was invalid")

        # Spotify API credentials
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

        # The least needed to access the currently playing song
        self._scope = Scope(scopes.user_read_currently_playing)

        # Trying to use the config auth token passed by parameter
        if expiration is None:
            expired = True
        else:
            expired = (expiration - int(time.time())) < 60

        # Either using the existing token or generating a new one
        if auth_token not in (None, "") and not expired:
            self._token = self._get_token(auth_token, expiration)
        else:
            self._token = self._authenticate()

        # The Spotipy instance
        self._spotify = Spotify(self._token)

    def _authenticate(self) -> RefreshingToken:
        """
        Asks the user to sign-in to Spotify and generates a self-refreshing
        token.
        """

        print("To authorize the Spotify API, you'll have to log-in"
              " in the new tab that is going to open in your browser.\n"
              "Afterwards, just paste the contents of the URL you have"
              " been redirected to, something like"
              " 'http://localhost:8888/callback/?code=AQAa5v...'")
        return prompt_for_user_token(self._client_id, self._client_secret,
                                     self._redirect_uri, self._scope)

    def _get_token(self, auth_token: str,
                   expiration: int) -> RefreshingToken:
        """
        Generates a self-refreshing token from an already existing one
        that hasn't expired.
        """

        data = {
            'access_token': auth_token,
            'token_type': 'Bearer',
            'scope': self._scope,
            'expires_in': expiration - int(time.time())
        }
        creds = Credentials(self._client_id, self._client_secret,
                            self._redirect_uri)
        return RefreshingToken(Token(data), creds)

    def connect(self) -> None:
        """
        An initial metadata refresh is run. `ConnectionNotReady` will be
        raised if no songs are playing in that moment.
        """

        self._refresh_metadata()

    @property
    def position(self) -> int:
        """
        Property that refreshes the metadata and returns the position. This
        has to be done because the song position is constantly changing and
        a new request has to be made.
        """

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
        if metadata is None:
            raise ConnectionNotReady("No song currently playing")
        self.artist = metadata.item.artists[0].name
        self.title = metadata.item.name

        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self._position = metadata.progress_ms
        self.is_playing = metadata.is_playing

    def play_video(self) -> None:
        """
        Starts the video for the currently playing song.
        """

        url = self._youtube.get_url(self.artist, self.title)
        self.player.start_video(url, self.is_playing)
        self.player.position = self.position

        if self._show_lyrics:
            print_lyrics(self.artist, self.title)

    def event_loop(self) -> None:
        """
        A callable event loop that checks if changes happen. This is called
        every 0.5 seconds from the Qt window.

        It checks for changes in:
            * The playback status (playing/paused) to change the player's too
            * The currently playing song: if a new song started, it's played
            * The position. Changes will be ignored unless the difference is
              larger than the real elapsed time or if it was backwards.
              This is done because some systems may lag more than others and
              a fixed time difference would cause errors
        """

        # Previous properties are saved to compare them with the new ones
        # after the metadata refresh
        artist = self.artist
        title = self.title
        position = self._position
        is_playing = self.is_playing
        self._refresh_metadata()

        # The first check should be if the song has ended to not touch
        # anything else that may not actually be true.
        if self.artist != artist or self.title != title:
            logging.info("New video detected")
            self.play_video()

        if self.is_playing != is_playing:
            self.player.pause = not self.is_playing

        playback_diff = self._position - position
        calls_diff = int((time.time() - self._event_timestamp) * 1000)
        if playback_diff >= (calls_diff + 100) or playback_diff < 0:
            self.player.position = self._position

        # The time passed between calls is refreshed
        self._event_timestamp = time.time()


def play_videos_web(player: Union['VLCPlayer', 'MpvPlayer'],
                    window: MainWindow, youtube: YouTube,
                    config: Config) -> None:
    """
    Playing videos with the Web API.

    Initializes the Web API and plays the first video.
    Also starts the event loop to detect changes and play new videos.
    """

    spotify = WebAPI(player, youtube, config.lyrics, config.client_id,
                     config.client_secret, config.redirect_uri,
                     config.auth_token, config.expiration)

    # Checks if Spotify is closed and if the auth details are valid
    msg = "Waiting for a Spotify song to play..."
    if not wait_for_connection(spotify.connect, msg):
        return

    # Saves the used credentials inside the config file for future usage
    config.client_secret = spotify._client_secret
    config.client_id = spotify._client_id
    config.auth_token = spotify._token.access_token
    config.expiration = spotify._token.expires_at
    if spotify._redirect_uri != config._options.redirect_uri.default:
        config.redirect_uri = spotify._redirect_uri

    spotify.play_video()
    window.start_event_loop(spotify.event_loop, 1000)
