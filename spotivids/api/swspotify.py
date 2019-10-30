"""
This module implements the SwSpotify API. It's a package that can obtain
metadata about Spotify without having to use the web API on Windows,
Mac OS and Linux.
The Linux module is implemented in a different file because in comparison
to the Windows and Mac OS methods, it's an officially supported API and has
more control over Spotify.
The Windows implementation for example just reads the title of the Spotify
window to obtain what song is playing. It's much more limited.

The API is controlled from the `play_videos_swspotify` function. The overall
usage and bevhavior of the class should be the same for all the APIs so
that they can be used interchangeably.
"""

import time
import logging
from typing import Union

from SwSpotify import spotify, SpotifyPaused, SpotifyClosed

from spotivids.api import ConnectionNotReady
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube


class SwSpotifyAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 youtube: YouTube, show_lyrics: bool = True) -> None:
        """
        It includes `player`, the VLC or mpv window to play videos and control
        it when the song status changes. The `Youtube` object is also needed
        to play the videos.
        """

        self.artist = ""
        self.title = ""
        self.player = player
        self._youtube = youtube
        self._show_lyrics = show_lyrics

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
            raise ConnectionNotReady("No song currently playing")

    def play_video(self) -> None:
        """
        Plays the currently playing song's music video.

        The SwSpotify API doesn't offer information about the position so
        it's roughly calculated with a timer.
        """

        logging.info("Starting new video")
        start_time = time.time_ns()
        url = self._youtube.get_url(self.artist, self.title)
        self.player.start_video(url, self.is_playing)

        # Waits until the player starts the video to set the offset
        while self.player.position == 0:
            pass
        self.player.position = int((time.time_ns() - start_time) / 10**9)

        if self._show_lyrics:
            print_lyrics(self.artist, self.title)

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
            self.play_video()

        if self.is_playing != is_playing:
            self.player.pause = not self.is_playing
