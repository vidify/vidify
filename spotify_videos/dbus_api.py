import sys
from typing import Tuple

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from .vlc_player import VLCPlayer
from .utils import split_title, ConnectionNotReady


class DBusAPI:
    """
    The DBus API class contains all information obtained from the DBus API.

    The logger is an instance from the logging module, configured
    to show debug or error messages.

    It includes `player`, the VLC window, so that some actions can
    be controlled from the API more intuitively, like automatic
    pausing/playing when the API detects it.
    """

    def __init__(self, player: VLCPlayer, logger: 'logging.Logger') -> None:
        """
        The parameters are saved inside the object and the DBus main loop
        is configured to be ran later.
        """

        self._logger = logger
        self.player = player

        self.artist = ""
        self.title = ""
        self.is_playing = False

        DBusGMainLoop(set_as_default=True)

    def __del__(self) -> None:
        """
        Safely disconnects from the bus and removes all signals
        """

        try:
            self._loop.quit()
        except AttributeError:
            pass

        self._logger.info("Disconnecting")
        self._disconnecting = True
        try:
            for signal_name, signal_handler in list(self._signals.items()):
                signal_handler.remove()
                del self._signals[signal_name]
        except AttributeError:
            pass

    def do_connect(self) -> None:
        """
        Connects to the DBus session bus and loads different interfaces
        to later get signals from it like the status of the media
        (playing/paused) or the song attributes.

        A `ConnectionNotReady` exception is thrown if no Spotify bus
        exists or if no song is playing.
        """

        self._session_bus = dbus.SessionBus()
        self._bus_name = "org.mpris.MediaPlayer2.spotify"
        self._disconnecting = False

        try:
            self._obj = self._session_bus.get_object(
                self._bus_name,
                '/org/mpris/MediaPlayer2')
        except dbus.exceptions.DBusException:
            raise ConnectionNotReady("No Spotify session currently running")

        self._properties_interface = dbus.Interface(
            self._obj,
            dbus_interface="org.freedesktop.DBus.Properties")
        self._introspect_interface = dbus.Interface(
            self._obj,
            dbus_interface="org.freedesktop.DBus.Introspectable")
        self._media_interface = dbus.Interface(
            self._obj,
            dbus_interface='org.mpris.MediaPlayer2')
        self._player_interface = dbus.Interface(
            self._obj,
            dbus_interface='org.mpris.MediaPlayer2.Player')
        self._introspect = self._introspect_interface.get_dbus_method(
            'Introspect',
            dbus_interface=None)
        self._loop = GLib.MainLoop()
        self._signals = {}
        self._logger.info("Connecting")

        if not self._disconnecting:
            introspect_xml = self._introspect(self._bus_name, '/')
            if 'TrackMetadataChanged' in introspect_xml:
                key = 'track_metadata_changed'
                self._signals[key] = self._session_bus.add_signal_receiver(
                    self._refresh_metadata,
                    'TrackMetadataChanged',
                    self._bus_name)
            self._properties_interface.connect_to_signal(
                'PropertiesChanged',
                self._on_properties_changed)

        try:
            self._refresh_metadata()
        except IndexError:
            raise ConnectionNotReady("No song is currently playing")

    def wait(self) -> None:
        """
        Waits for events in the DBus main loop until KeyboardInterupt
        is detected or a new song starts
        """

        self._logger.info("Starting loop")
        try:
            self._loop.run()
        except KeyboardInterrupt:
            self._logger.info("Quitting main loop")
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

        first_msg = True
        metadata = self._properties_interface.Get(
            "org.mpris.MediaPlayer2.Player",
            "Metadata")
        self.artist, self.title = self._formatted_metadata(metadata)

        status = str(self._properties_interface.Get(
            'org.mpris.MediaPlayer2.Player',
            'PlaybackStatus'))
        self.is_playing = self._bool_status(status)

    def _bool_status(self, status: str) -> bool:
        """
        Converts a status string from DBus to a bool, both to keep
        consistency with the web API status variable and because using
        booleans is easier and less confusing.
        """

        if status.lower() in ('stopped', 'paused'):
            return False
        else:
            return True

    def _on_properties_changed(
            self, interface: dbus.String,
            properties: dbus.Dictionary, signature: dbus.Array) -> None:
        """
        Function called from DBus on events from the main loop.

        If the song was changed, the loop is broken to finish the song.
        If the playback status changed it directly plays/pauses
        the VLC player.
        """

        if dbus.String('Metadata') in properties:
            metadata = properties[dbus.String('Metadata')]
            artist, title = self._formatted_metadata(metadata)
            if artist != self.artist or title != self.title:
                self.artist = artist
                self.title = title
                self._logger.info("New video detected")
                self._loop.quit()

        if dbus.String('PlaybackStatus') in properties:
            status = str(properties[dbus.String('PlaybackStatus')])
            status = self._bool_status(status)
            if status != self.is_playing:
                self._logger.info("Paused/Played video")
                self.is_playing = status
                self.player.toggle_pause()
