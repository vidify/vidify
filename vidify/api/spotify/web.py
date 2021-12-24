"""
This module implements the official web API, using the `tekore` module.
The web API provides much more metadata about the Spotify player but
it's limited in terms of usabilty:
    * The user has to sign in and manually set it up
    * Only Spotify Premium users are able to use some functions
    * API calls are limited, so it's not as responsive

This implementation is based on the generic implementation of an API. Please
check out vidify.api.generic for more details about how API modules
work. This module only contains comments specific to the API, so it may be
confusing at first glance.
"""

import logging
import time

from tekore import RefreshingToken, Spotify

from vidify.api import ConnectionNotReady, split_title
from vidify.api.generic import APIBase


class SpotifyWeb(APIBase):
    player_name: str = "Spotify"
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
        if metadata is None or metadata.item is None:
            raise ConnectionNotReady("No song currently playing")
        self.artist = metadata.item.artists[0].name
        self.title = metadata.item.name

        # Some local songs don't have an artist name so `split_title`
        # is called in an attempt to manually get it from the title.
        if self.artist == "":
            self.artist, self.title = split_title(self.title)

        self._position = metadata.progress_ms
        self.is_playing = metadata.is_playing

    def event_loop(self) -> None:
        """
        The event loop callback that checks if changes happen. This is called
        periodically within the Qt window.

        It checks for changes in:
            * The playback status (playing/paused) to change the player's too
            * The currently playing song: if a new song started, it's played
            * The position
        """

        # Previous properties are saved to compare them with the new ones
        # after the metadata refresh
        artist = self.artist
        title = self.title
        position = self._position
        is_playing = self.is_playing
        self._refresh_metadata()

        # First checking if a new song started, so that position or status
        # changes are related to the new song.
        if self.artist != artist or self.title != title:
            logging.info("New video detected")
            self.new_song_signal.emit(self.artist, self.title, 0)

        if self.is_playing != is_playing:
            logging.info("Status change detected")
            self.status_signal.emit(self.is_playing)

        # The position difference between calls is compared to the elapsed
        # time to know whether the position has been modified.
        # Changes will be ignored unless the position difference is
        # greater than the elapsed time (plus a margin) or if it's negative
        # (backwards).
        playback_diff = self._position - position
        calls_diff = int((time.time() - self._event_timestamp) * 1000)
        if playback_diff >= (calls_diff + 100) or playback_diff < 0:
            logging.info("Position change detected")
            self.position_signal.emit(self._position)

        # The time passed between calls is refreshed
        self._event_timestamp = time.time()
