import sys
import logging
from typing import Tuple, Union

import pydbus
from gi.repository import GLib

from ..utils import split_title, ConnectionNotReady


class DBusAPI(object):
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
        """
        The logger is an instance from the logging module, configured
        to show info or error messages.

        It includes `player`, the VLC or mpv window, so that some actions can
        be controlled from the API more intuitively, like automatic
        pausing/playing when the API detects it.
        """

         logger: logging.Logger) -> None:

        self._logger = logger
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

    def _formatted_metadata(self, metadata: dict) -> Tuple[str, str]:
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
        self.artist, self.title = self._formatted_metadata(metadata)

        status = str(player_interface.PlaybackStatus)
        self.is_playing = self._bool_status(status)

    def _bool_status(self, status: str) -> bool:
        """
        Converts a status string from DBus to a bool, both to keep
        consistency with the other API status variables and because using
        booleans is easier and less confusing.
        """

        return False if status.lower() in ('stopped', 'paused') else True

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
            artist, title = self._formatted_metadata(metadata)
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
