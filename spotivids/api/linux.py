import sys
import time
import logging
from typing import Tuple, Union

import pydbus
from gi.repository import GLib

from spotivids.api import split_title, ConnectionNotReady, wait_for_connection
from spotivids.lyrics import print_lyrics
from spotivids.youtube import YouTube


class DBusAPI:
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer']) -> None:
        """
        It includes `player`, the VLC or mpv window, so that some actions can
        be controlled from the API more intuitively, like automatic
        pausing/playing when the API detects it.
        """

        self._logger = logging.getLogger('spotivids')
        self.player = player
        self.artist = ""
        self.title = ""
        self.is_playing = False

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

        player_interface = self._obj['org.mpris.MediaPlayer2.Player']
        metadata = player_interface.Metadata
        self.artist, self.title = self._format_metadata(metadata)

        status = str(player_interface.PlaybackStatus)
        self.is_playing = self._bool_status(status)

    def _bool_status(self, status: str) -> bool:
        """
        Converts a status string from DBus to a bool, both to keep
        consistency with the other API status variables and because using
        booleans is easier and less confusing.
        """

        return status.lower() == 'playing'

    def _on_properties_changed(self, interface: str, properties: dict,
                               signature: list) -> None:
        """
        Function called from DBus on events from the main loop.

        If the song was changed, the loop is broken to finish the song.
        If the playback status changed it directly plays/pauses
        the VLC player.
        """

        if 'Metadata' in properties:
            metadata = properties['Metadata']
            artist, title = self._format_metadata(metadata)
            if artist != self.artist or title != self.title:
                self._logger.info("New video detected")
                self.artist = artist
                self.title = title
                self._loop.quit()

        if 'PlaybackStatus' in properties:
            status = self._bool_status(properties['PlaybackStatus'])
            if status != self.is_playing:
                self._logger.info("Paused/Played video")
                self.is_playing = status
                self.player.toggle_pause()


def play_videos_linux(player: Union['VLCPlayer', 'MpvPlayer']) -> None:
    """
    Playing videos with the DBus API (Linux).

    Spotify doesn't currently support the MPRIS property `Position`
    so the starting offset is calculated manually and may be a bit rough.

    After playing the video, the player waits for DBus events like
    pausing the video.
    """

    from spotivids import config
    youtube = YouTube(config.debug, config.width, config.height)
    spotify = DBusAPI(player)
    msg = "Waiting for a Spotify session to be ready..."
    if not wait_for_connection(spotify.connect, msg):
        return

    while True:
        start_time = time.time_ns()
        url = youtube.get_url(spotify.artist, spotify.title)
        is_playing = spotify.is_playing
        player.start_video(url, is_playing)

        # Waits until the player starts the video to set the offset
        if is_playing:
            while player.position == 0:
                pass
            player.position = int((time.time_ns() - start_time) / 10**9)

        if config.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        spotify.wait()
