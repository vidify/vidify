import sys
import time
import logging

from SwSpotify import spotify, SpotifyNotRunning

from ..utils import ConnectionNotReady


class SwSpotifyAPI(object):
    def __init__(self, logger: logging.Logger) -> None:
        """
        The SwSpotify API for Windows and Darwin (macOS) is really limited,
        since all it can do is get the artist and title of the current song.

        The logger is an instance from the logging module, configured to show
        debug or error messages.
        """

        self._logger = logger
        self.artist = ""
        self.title = ""

    def connect(self) -> None:
        """
        First metadata refresh that raises ConnectionNotReady if the artist
        or title are empty, and from the function itself if SpotifyNotRunning
        is thrown inside SwSpotify.
        """

        self._refresh_metadata()
        if "" in (self.artist, self.title):
            raise ConnectionNotReady("No Spotify session currently running"
                                     " or no song currently playing.")

    def _refresh_metadata(self) -> None:
        try:
            self.title, self.artist = spotify.current()
        except SpotifyNotRunning:
            raise ConnectionNotReady("No song currently playing")

    def wait(self) -> None:
        """
        Waits until a new song is played.
        """

        self._logger.info("Starting loop")
        try:
            while True:
                time.sleep(0.5)
                artist = self.artist
                title = self.title
                # If the song is paused mid-way, SwSpotify will throw an error.
                try:
                    self._refresh_metadata()
                except ConnectionNotReady:
                    pass

                if self.artist != artist or self.title != title:
                    break
        except KeyboardInterrupt:
            self._logger.info("Quitting from web player loop")
            sys.exit(0)
