"""
This module implements the official web API, using the `spotipy` module.
The web API provides much more metadata about the Spotify player but
it's limited in terms of usabilty:
    * The user has to sign in and manually set it up
    * Only Spotify Premium users are able to use some functions
    * API calls are limited, so it's not as responsive

This implementation is based on the generic implementation of an API. Please
check out spotivids.api.generic for more details about how API modules
work. This module only contains comments specific to the API, so it may be
confusing at first glance.
"""

import os
import time
import logging
from typing import Union

from spotipy import Spotify
from spotipy.scope import scopes
from spotipy.auth import Token
from spotipy.util import RefreshingToken, RefreshingCredentials
import requests  # required in spotipy

from spotivids.api import split_title, ConnectionNotReady
from spotivids.api.generic import APIBase
from spotivids.config import Config


class SpotifyWebAPI(APIBase):
    artist: str = None
    title: str = None
    is_playing: bool = None

    def __init__(self, token: RefreshingToken) -> None:
        super().__init__()
        self.artist = ""
        self.title = ""
        self.is_playing = False
        self._position = 0
        self._token = token
        self._spotify = Spotify(self._token)
        self._event_timestamp = time.time()

    def connect_api(self) -> None:
        self._refresh_metadata()

    @property
    def position(self) -> int:
        """
        _refresh_metadata() has to be called because the song position is
        constantly changing.
        """

        self._refresh_metadata()
        return self._position

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata of the player: artist, title, whether
        it's playing or not, and the current position.
        """

        metadata = self._spotify.playback_currently_playing()
        if metadata is None:
            raise ConnectionNotReady("No song currently playing")
        self.artist = metadata.item.artists[0].name
        self.title = metadata.item.name

        # Some local songs don't have an artist name so `split_title`
        # is called in an attempt to manually get it from the title.
        if self.artist == '':
            self.artist, self.title = split_title(self.title)

        self._position = metadata.progress_ms
        self.is_playing = metadata.is_playing

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
            #  self.play_video()

        if self.is_playing != is_playing:
            #  self.player.pause = not self.is_playing
            pass

        playback_diff = self._position - position
        calls_diff = int((time.time() - self._event_timestamp) * 1000)
        if playback_diff >= (calls_diff + 100) or playback_diff < 0:
            #  self.player.position = self._position
            pass

        # The time passed between calls is refreshed
        self._event_timestamp = time.time()


def get_token(auth_token: str, refresh_token: str, expiration: int,
              client_id: str, client_secret: str, redirect_uri: str
              ) -> RefreshingToken:
    """
    Tries to generate a self-refreshing token from the parameters. They
    could be anything so there have to be several checks to make sure the
    returned token is valid. Otherwise, this function will return None

    `refresh_token` is a special token needed to refresh `auth_token`. It's
    needed to create the RefreshingToken so that it automatically refreshes
    itself when it's expired.
    """

    # Trying to use the env variables
    if client_id is None:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
    if client_secret is None:
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if redirect_uri is None:
        redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')

    # Checking that the credentials are valid
    for c in (auth_token, refresh_token, expiration, client_id, client_secret,
              redirect_uri):
        if c in (None, ''):
            logging.info("Rejecting the token because one of the credentials"
                         " provided is empty.")
            return None

    # Generating a RefreshingToken with the parameters
    data = {
        'access_token': auth_token,
        'token_type': 'Bearer',
        'scope': scopes.user_read_currently_playing,
        'expires_in': expiration - int(time.time()),
        'refresh_token': refresh_token
    }
    creds = RefreshingCredentials(client_id, client_secret, redirect_uri)
    token = RefreshingToken(Token(data), creds)

    # Doing an initial request to check that it was generated correctly:
    # an error could be raised from the requests package, or the returned
    # value could be None
    try:
        s = Spotify(token)
        s.playback_currently_playing()
    except (ConnectionNotReady, requests.exceptions.HTTPError) as e:
        logging.info("Rejecting the token because of an error while trying"
                     f" to connect to Spotify: {e}")
        return None

    # If it got here, it means the generated token is valid
    return token
