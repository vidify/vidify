"""
This module implements the MediaPlayer API to obtain metadata from any
DBus MediaPlayer supported API, like Spotify.
It's intended for Linux but it should also work on BSD and other
unix-like systems with DBus.

This implementation is based on the generic implementation of an API. Please
check out spotivids.api.generic for more details about how API modules
work. This module only contains comments specific to the API, so it may be
confusing at first glance.
"""

import logging
from typing import Tuple

import pydbus
from gi.repository import GLib

from spotivids.api import split_title, ConnectionNotReady
from spotivids.api.generic import APIBase


class DBusMediaPlayerAPI(APIBase):
    artist: str = None
    title: str = None
    is_playing: bool = None

    def __init__(self, bus_name: str, position_feature: bool = True) -> None:
        super().__init__()
        self._bus_name = bus_name
        self.artist = ""
        self.title = ""
        self.is_playing = False
        self._position_feature = position_feature

    def __del__(self) -> None:
        """
        Safely disconnects from the bus and loop.
        """

        logging.info("Disconnecting")
        try:
            self._disconnect_obj.disconnect()
        except AttributeError:
            pass

    @property
    def position(self) -> int:
        """
        This feature isn't available for some players like Spotify, so
        `NotImplementedError` is raised instead to keep consistency with the
        rest of the APIs.
        """

        if not self._position_feature:
            raise NotImplementedError
        return self._player_interface.Position

    def connect_api(self) -> None:
        """
        Connects to the DBus session. Tries to access the proxy object
        and configures the call on property changes.
        """

        self._bus = pydbus.SessionBus()
        try:
            self._obj = self._bus.get(self._bus_name,
                                      '/org/mpris/MediaPlayer2')
        except GLib.Error:
            raise ConnectionNotReady("No MediaPlayer session currently running")

        self._player_interface = self._obj['org.mpris.MediaPlayer2.Player']

        try:
            self._refresh_metadata()
        except IndexError:
            raise ConnectionNotReady("No song is currently playing")

        self._start_event_loop()

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
        """

        if 'Metadata' in properties:
            metadata = properties['Metadata']
            artist, title = self._format_metadata(metadata)
            if self.artist != artist or self.title != title:
                logging.info("New video detected")
                # Refreshes the metadata with the new data and plays the video
                self.artist = artist
                self.title = title
                self.new_song_signal.emit()

        if 'PlaybackStatus' in properties:
            is_playing = self._bool_status(properties['PlaybackStatus'])
            if self.is_playing != is_playing:
                # Refreshes the metadata and pauses/plays the video
                self.is_playing = is_playing
                self.status_signal.emit(is_playing)
