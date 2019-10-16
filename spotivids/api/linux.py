import sys
import time
import logging
from typing import Tuple, Union

import pydbus
from gi.repository import GLib

from spotivids import config
from spotivids.api import split_title, ConnectionNotReady, wait_for_connection
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube


class DBusAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer']) -> None:
        """
        It includes `player`, the VLC or mpv window to play videos and control
        it when the song status changes. The `Youtube` object is also needed
        to play the videos.
        """

        self._logger = logging.getLogger('spotivids')
        self.player = player
        self.artist = ""
        self.title = ""
        self.is_playing = False
        self._youtube = YouTube(config.debug, config.width, config.height)

    def connect(self) -> None:
        """
        Connects to the DBus session. Tries to access the proxy object
        and configures the call on property changes.

        A `ConnectionNotReady` exception is thrown if no Spotify bus
        exists or if no song is playing.
        """

        self._logger.info("Connecting")
        self._bus = pydbus.SessionBus()
        try:
            self._obj = self._bus.get('org.mpris.MediaPlayer2.spotify',
                                      '/org/mpris/MediaPlayer2')
        except GLib.Error:
            raise ConnectionNotReady("No Spotify session currently running")

        self.player_interface = self._obj['org.mpris.MediaPlayer2.Player']
        self._loop = GLib.MainLoop()
        self._disconnect_obj = self._obj.PropertiesChanged.connect(
            self._on_properties_changed)

        try:
            self._refresh_metadata()
        except IndexError:
            raise ConnectionNotReady("No song is currently playing")

    def disconnect(self) -> None:
        """
        Safely disconnects from the bus and loop.
        """

        self._logger.info("Disconnecting")
        try:
            self._disconnect_obj.disconnect()
            self._loop.quit()
        except AttributeError:
            pass

    def wait(self) -> None:
        """
        Waits for events in the DBus main loop until KeyboardInterupt
        is detected or a new song starts
        """

        self._logger.info("Starting loop")
        try:
            self._loop.run()
        except KeyboardInterrupt:
            self.disconnect()
            sys.exit(0)

    def _format_metadata(self, metadata: dict) -> Tuple[str, str]:
        """
        Returns the artist and title out of a raw metadata object
        as a tuple, first the artist and then the title.

        Some local songs don't have an artist name, so it has to be
        obtained with `split_title` from the title.
        """

        artist = metadata['xesam:artist'][0]
        title = metadata['xesam:title']

        if artist == '':
            artist, title = split_title(title)

        return artist, title

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata and status of the player as a tuple
        first the artist and then the title.
        """

        metadata = self.player_interface.Metadata
        self.artist, self.title = self._format_metadata(metadata)

        status = str(self.player_interface.PlaybackStatus)
        self.is_playing = self._bool_status(status)

    def _bool_status(self, status: str) -> bool:
        """
        Converts a status string from DBus to a bool, to keep consistency
        with the other API status variables and because using booleans is
        easier and less confusing.
        """

        return status.lower() == 'playing'

    def play_video(self) -> None:
        """
        Plays the currently playing song's music video.

        Spotify doesn't currently support the MPRIS property `Position`
        so the starting offset is calculated manually and may be a bit rough.
        """

        start_time = time.time_ns()
        url = self._youtube.get_url(self.artist, self.title)
        self.player.start_video(url, self.is_playing)

        # Waits until the player starts the video to set the offset
        if self.is_playing:
            while self.player.position == 0:
                pass
            self.player.position = int((time.time_ns() - start_time) / 10**9)

        if config.lyrics:
            print_lyrics(self.artist, self.title)

    def _on_properties_changed(self, interface: str, properties: dict,
                               signature: list) -> None:
        """
        Function called from DBus on event changes like the song or if it
        has been paused.
        """

        if 'Metadata' in properties:
            metadata = properties['Metadata']
            artist, title = self._format_metadata(metadata)
            if self.artist != artist or self.title != title:
                self._logger.info("New video detected")
                self._loop.quit()
                # Refreshes the metadata with the new data and plays the video
                self.artist = artist
                self.title = title
                self.play_video()

        if 'PlaybackStatus' in properties:
            is_playing = self._bool_status(properties['PlaybackStatus'])
            if self.is_playing != is_playing:
                # Refreshes the metadata and pauses/plays the video
                self.is_playing = is_playing
                self.player.pause = not is_playing


def play_videos_linux(player: Union['VLCPlayer', 'MpvPlayer']) -> None:
    """
    Playing videos with the DBus API (Linux).

    Initializes the DBus API and plays the first video.
    """

    spotify = DBusAPI(player)
    msg = "Waiting for a Spotify session to be ready..."
    if not wait_for_connection(spotify.connect, msg):
        return
    spotify.play_video()
