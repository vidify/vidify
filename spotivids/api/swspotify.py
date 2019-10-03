import sys
import time
import logging
from typing import Union

from SwSpotify import spotify, SpotifyNotRunning

from spotivids.api import ConnectionNotReady, wait_for_connection
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube


class SwSpotifyAPI:
    def __init__(self) -> None:
        """
        The SwSpotify API for Windows and Darwin (macOS) is really limited,
        since all it can do is get the artist and title of the current song.
        """

        self._logger = logging.getLogger('spotivids')
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
        artist = self.artist
        title = self.title
        try:
            while True:
                time.sleep(0.5)
                # Temporary until pause is implemented in SwSpotify
                try:
                    self._refresh_metadata()
                except ConnectionNotReady:
                    pass

                if self.artist != artist or self.title != title:
                    break
        except KeyboardInterrupt:
            self._logger.info("Quitting from web player loop")
            sys.exit(0)


def play_videos_swspotify(player: Union['VLCPlayer', 'MpvPlayer']) -> None:
    """
    Playing videos with the SwSpotify API (macOS and Windows).
    """

    from spotivids import config
    youtube = YouTube(config.debug, config.width, config.height)
    spotify = SwSpotifyAPI()
    msg = "Waiting for a Spotify session to be ready..."
    if not wait_for_connection(spotify.connect, msg):
        return

    while True:
        start_time = time.time_ns()
        url = youtube.get_url(spotify.artist, spotify.title)
        player.start_video(url)

        # Waits until the player starts the video to set the offset
        while player.position == 0:
            pass
        player.position = int((time.time_ns() - start_time) / 10**9)

        if config.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        spotify.wait()
