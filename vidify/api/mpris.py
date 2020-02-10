"""
This module implements the MediaPlayer API to obtain metadata from any DBus
MPRIS supported API, like Spotify or Rhythmbox.
It's intended for Linux but it should also work on BSD and other unix-like
systems with DBus.

This implementation is based on the generic implementation of an API. Please
check out vidify.api.generic for more details about how API modules
work. This module only contains comments specific to the API, so it may be
confusing at first glance.
"""

import time
import logging
from typing import Tuple

import pydbus
from gi.repository import GLib

from vidify.api import split_title, ConnectionNotReady
from vidify.api.generic import APIBase


class MPRISAPI(APIBase):
    artist: str = None
    title: str = None
    is_playing: bool = None

    def __init__(self) -> None:
        super().__init__()
        self.artist = ""
        self.title = ""
        self.is_playing = False

    def __del__(self) -> None:
        """
        Safely disconnects from the bus and loop.
        """

        logging.info("Disconnecting")
        try:
            self._disconnect_obj.disconnect()
        except (AttributeError, RuntimeError):
            pass

    @property
    def position(self) -> int:
        """
        Returns the position in milliseconds. The MPRIS specification states
        that the provided position should be in microseconds, so it's divided
        by 1000.

        This feature isn't available for some players like Spotify, so
        `NotImplementedError` is raised instead to keep consistency with the
        rest of the APIs.
        """

        if self._no_position:
            raise NotImplementedError
        return self._player_interface.Position // 1000

    def connect_api(self) -> None:
        """
        Connects to the DBus session. Tries to access the proxy object
        and configures the call on property changes.
        """

        self._bus = pydbus.SessionBus()
        self._bus_name, self._obj = self._get_player()

        # Some MPRIS players don't support the position feature, so this
        # checks if it's in the blacklist to act accordingly when the
        # position is requested.
        position_blacklist = ('org.mpris.MediaPlayer2.spotify',)
        self._no_position = self._bus_name in position_blacklist
        self._player_interface = self._obj['org.mpris.MediaPlayer2.Player']

        try:
            self._refresh_metadata()
        except IndexError:
            raise ConnectionNotReady("No song is currently playing")

        self._start_event_loop()

    def _get_player(self) -> Tuple[str, 'CompositeObject']:
        """
        Method used to find the available players in the DBus bus. It returns
        the bus' name and object if it was found, or raises ConnectionNotReady
        otherwise.
        """

        logging.info("Looking for players")

        # Iterating through every bus name and checking that it's valid.
        for bus_name in self._bus.get(".DBus", "DBus").ListNames():
            # It must be from MediaPlayer2
            if bus_name.startswith('org.mpris.MediaPlayer2'):
                # Trying to obtain the bus object
                try:
                    obj = self._bus.get(bus_name, '/org/mpris/MediaPlayer2')
                except GLib.Error as e:
                    logging.info("Skipping %s because of error: %s",
                                 bus_name, str(e))
                    continue

                # And making sure that it's playing at the moment (otherwise
                # only the first player found would be returned, but it could
                # not be the one actually being used).
                if not self._bool_status(obj.PlaybackStatus):
                    logging.info("Skipping %s because it's not playing at"
                                 " the moment", bus_name)
                    continue

                logging.info("Using %s", bus_name)
                return bus_name, obj

        # ConnectionNotReady is raised at the end, in case that no valid
        # players were found.
        raise ConnectionNotReady("No players found")

    def _start_event_loop(self) -> None:
        """
        Starts the asynchronous GLib event loop.
        """

        self._disconnect_obj = self._obj.PropertiesChanged.connect(
            self._on_properties_changed)

    def event_loop(self) -> None:
        """
        The DBus event loop is handled by GLib, so a manual function to check
        for updates isn't needed. This raises `NotImplementedError` instead
        to keep consistency with the rest of the APIs.
        """

        raise NotImplementedError

    @staticmethod
    def _format_metadata(metadata: dict) -> Tuple[str, str]:
        """
        Returns the artist and title out of a raw metadata object
        as a tuple, first the artist and then the title.

        If the MPRIS player can't obtain the title and artist fields, an
        empty string is used instead. It will be handled correctly in the main
        window.

        Some local songs don't have an artist name, so it has to be
        obtained with `split_title` from the title.
        """

        try:
            title = metadata['xesam:title']
        except KeyError:
            title = ''

        try:
            artist = metadata['xesam:artist'][0]
        except KeyError:
            artist = ''

        # Some players use `Unknown` when the artist or title metadata
        # is empty.
        if artist in ('', 'Unknown'):
            artist, title = split_title(title)

        return artist, title

    def _refresh_metadata(self) -> None:
        """
        Refreshes the metadata and status of the player as a tuple.
        """

        metadata = self._player_interface.Metadata
        self.artist, self.title = self._format_metadata(metadata)

        status = str(self._player_interface.PlaybackStatus)
        self.is_playing = self._bool_status(status)

    @staticmethod
    def _bool_status(status: str) -> bool:
        """
        Converts a status string from DBus to a bool, to keep consistency
        with the other API status variables.
        """

        return status.lower() == 'playing'

    def _on_properties_changed(self, interface: str, properties: dict,
                               signature: list) -> None:
        """
        Function called from DBus on event changes like the song or if it
        has been paused.

        The MPRIS standard indicates that the PropertiesChanged signal is not
        emitted when the position changes, so it won't be taken into account
        below.
        """

        # The time when this function started is saved for the audiosync
        # feature.
        start_time = time.time()

        if 'Metadata' in properties:
            metadata = properties['Metadata']
            artist, title = self._format_metadata(metadata)
            if self.artist != artist or self.title != title:
                # Refreshes the metadata with the new data and sends the
                # signal to play the next video.
                logging.info("New video detected")
                self.artist = artist
                self.title = title
                self.new_song_signal.emit(artist, title, start_time)

        if 'PlaybackStatus' in properties:
            is_playing = self._bool_status(properties['PlaybackStatus'])
            if self.is_playing != is_playing:
                # Refreshes the metadata and pauses/plays the video
                logging.info("Status change detected")
                self.status_signal.emit(is_playing)
                self.is_playing = is_playing
