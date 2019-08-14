import sys
from typing import Tuple

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from .vlc import VLCWindow
from .utils import split_title


class DBusPlayer:
    """
    The DBus API class contains all information obtained from the DBus API.

    The logger is an instance from the logging module, configured
    to show debug or error messages.

    It includes `player`, the VLC window, so that some actions can
    be controlled from the API more intuitively, like automatic
    pausing/playing when the API detects it.
    """

    def __init__(self, player: VLCWindow, logger: 'logging.Logger') -> None:
        
        self._logger = logger

        # Configuring loop
        DBusGMainLoop(set_as_default=True)

        # Main player properties
        self.artist = ""
        self.title = ""
        self.is_playing = False
        self.player = player

        # DBus internal properties
        self._session_bus = dbus.SessionBus()
        self._bus_name = "org.mpris.MediaPlayer2.spotify"
        self._disconnecting = False

        # Waiting for the user to open Spotify
        first_msg = True
        while True:
            try:
                self._obj = self._session_bus.get_object(
                        self._bus_name,
                        '/org/mpris/MediaPlayer2')
                break
            except dbus.exceptions.DBusException:
                if first_msg:
                    print("Waiting for the Spotify session to start...")
                    first_msg = False

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

        self.do_connect()

        # Waiting for a song to start
        first_msg = True
        while True:
            try:
                self._refresh_metadata()
                break
            except:
                if first_msg:
                    print("Waiting for a Spotify song to play...")
                    first_msg = False

    # Proper disconnect when the program ends
    def __del__(self) -> None:
        self._loop.quit()
        self.do_disconnect()
    
    # Connects to the DBus signals
    def do_connect(self) -> None:
        self._logger.info("Connecting")
        if not self._disconnecting:
            introspect_xml = self._introspect(self._bus_name, '/')
            if 'TrackMetadataChanged' in introspect_xml:
                self._signals['track_metadata_changed'] = self._session_bus.add_signal_receiver(
                        self._refresh_metadata,
                        'TrackMetadataChanged',
                        self._bus_name)
            self._properties_interface.connect_to_signal(
                    'PropertiesChanged',
                    self._on_properties_changed)

    # Disconnects from the DBus signals
    def do_disconnect(self) -> None:
        self._logger.info("Disconnecting")
        self._disconnecting = True
        try:
            for signal_name, signal_handler in list(self._signals.items()):
                signal_handler.remove()
                del self._signals[signal_name]
        except AttributeError:
            pass

    # Waits for changes in DBus properties, exits with Ctrl+C
    def wait(self) -> None:
        self._logger.info("Starting loop")
        try:
            self._loop.run()
        except KeyboardInterrupt:
            self._logger.info("Quitting main loop")
            sys.exit(0)

    # Returns the artist and title out of a raw metadata object
    def _formatted_metadata(self, metadata: dict) -> Tuple[str,str]:
        artist = metadata['xesam:artist'][0]
        title = metadata['xesam:title']
        
        # Some local songs have both the artist and the title inside
        if artist == '':
            artist, title = split_title(title)

        return artist, title

    # Refreshes the metadata and status of the player (artist, title)
    def _refresh_metadata(self) -> None:
        first_msg = True
        while True:
            metadata = self._properties_interface.Get(
                    "org.mpris.MediaPlayer2.Player",
                    "Metadata")
            if metadata is not None:
                break
            if first_msg:
                print("No song currently playing.")
                first_msg = False
        self.artist, self.title = self._formatted_metadata(metadata)

        status = str(self._properties_interface.Get(
            'org.mpris.MediaPlayer2.Player',
            'PlaybackStatus'))
        self.is_playing = self._bool_status(status)

    # Consistency with the web API status variable and ease of use using booleans
    def _bool_status(self, status: str) -> bool:
        if status.lower() in ('stopped', 'paused'):
            return False
        else:
            return True

    # Function called from DBus on property changes
    def _on_properties_changed(self, interface: dbus.String,
            properties: dbus.Dictionary, signature: dbus.Array) -> None:
        # If the song is different, break the loop
        if dbus.String('Metadata') in properties:
            metadata = properties[dbus.String('Metadata')]
            artist, title = self._formatted_metadata(metadata)
            if artist != self.artist or title != self.title:
                self.artist = artist
                self.title = title
                self._logger.info("New video detected")
                self._loop.quit()

        # The song was Paused/Played
        if dbus.String('PlaybackStatus') in properties:
            status = str(properties[dbus.String('PlaybackStatus')])
            status = self._bool_status(status)
            if status != self.is_playing:
                self._logger.info("Paused/Played video")
                self.is_playing = status
                self.player.toggle_pause()

