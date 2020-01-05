"""
This module implements the SwSpotify API. It's a package that can obtain
metadata about Spotify without having to use the web API on Windows,
Mac OS and Linux.
The Linux module is implemented in a different file because in comparison
to the Windows and Mac OS methods, it's an officially supported API and has
more control over Spotify.
The Windows implementation for example just reads the title of the Spotify
window to obtain what song is playing. It's much more limited.

This implementation is based on the generic implementation of an API. Please
check out vidify.api.generic for more details about how API modules
work. This module only contains comments specific to the API, so it may be
confusing at first glance.
"""

import logging

from SwSpotify import spotify, SpotifyPaused, SpotifyClosed

from vidify.api import ConnectionNotReady, split_title
from vidify.api.generic import APIBase


class SwSpotifyAPI(APIBase):
    artist: str = None
    title: str = None
    is_playing: bool = None

    def __init__(self) -> None:
        super().__init__()
        self.artist = ""
        self.title = ""
        self.is_playing = False

    @property
    def position(self) -> int:
        """
        This feature isn't available for any of the platforms supported by
        SwSpotify, so `NotImplementedError` is raised instead to keep
        consistency with the rest of the APIs.
        """

        raise NotImplementedError

    def connect_api(self) -> None:
        self._refresh_metadata()

    def _refresh_metadata(self) -> None:
        """
        Refreshes the API metadata: updates the artist and title of the song.

        The SwSpotify API works with exceptions so `SpotifyPaused` means
        the song isn't currently playing (the artist and title should remain
        the same), and `SpotifyClosed` means that there isn't a Spotify
        session open at that moment.
        """

        try:
            self.title, self.artist = spotify.current()
            self.is_playing = True
        except SpotifyPaused:
            self.is_playing = False
        except SpotifyClosed:
            raise ConnectionNotReady("No song currently playing") from None

        # Splitting the artist and title for local songs
        if self.artist == '':
            self.artist, self.title = split_title(self.title)

        # Checking that the metadata is valid
        if "" in (self.artist, self.title):
            raise ConnectionNotReady(
                "No Spotify session currently running or no song currently"
                " playing.") from None

    def event_loop(self) -> None:
        """
        A callable event loop that checks if changes happen. This is called
        every 0.5 seconds from the QT window.

        It checks for changes in:
            * The playback status (playing/paused) to change the player's too
            * The currently playing song: if a new song started, it's played
        """

        artist = self.artist
        title = self.title
        is_playing = self.is_playing
        self._refresh_metadata()

        # The first check should be if the song has ended to not touch
        # anything else that may not actually be true.
        if self.artist != artist or self.title != title:
            logging.info("New video detected")
            self.new_song_signal.emit(self.artist, self.title, 0)

        if self.is_playing != is_playing:
            logging.info("Status change detected")
            self.status_signal.emit(self.is_playing)
