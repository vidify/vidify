"""
This module implements the official web API, using the `spotipy` module.
The web API provides much more metadata about the Spotify player but
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
from spotipy.util import RefreshingToken
import requests  # required in spotipy

from spotivids.api import split_title, ConnectionNotReady
from spotivids.config import Config
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube


class WebAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 youtube: YouTube, token: Union[Token, RefreshingToken],
                 show_lyrics: bool = True) -> None:
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

        self._youtube = youtube
        self._token = token
        self._spotify = Spotify(self._token)
        self._show_lyrics = show_lyrics
        self._event_timestamp = time.time()

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

        logging.info("Starting new video")
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


def get_token(auth_token: str, expiration: int, client_id: str = None,
              client_secret: str = None, redirect_uri: str = None
              ) -> RefreshingToken:
    """
    Tries to generate a self-refreshing token from the parameters. They
    could be anything so there have to be several checks to make sure the
    returned token is valid. Otherwise, this function will return None
    """

    # Trying to use the env variables
    if client_id is None:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
    if client_secret is None:
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if redirect_uri is None:
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

    # Checking that the credentials are valid
    for c in (auth_token, expiration, client_id, client_secret, redirect_uri):
        if c in (None, ''):
            return None

    # Checking if the token is expired
    if (expiration - int(time.time())) < 60:
        return None

    # Generating a RefreshingToken with the parameters
    scope = Scope(scopes.user_read_currently_playing)
    data = {
        'access_token': auth_token,
        'token_type': 'Bearer',
        'scope': scope,
        'expires_in': expiration - int(time.time())
    }
    creds = Credentials(client_id, client_secret, redirect_uri)
    token = RefreshingToken(Token(data), creds)

    # Doing an initial request to check that it was generated correctly:
    # an error could be raised from the requests package, or the returned
    # value could be None
    try:
        Spotify(token)
    except (ConnectionNotReady, requests.exceptions.HTTPError):
        return None

    # If it got here, it means the generated token is valid
    return token
