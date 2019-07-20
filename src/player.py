import os
import vlc
import dbus
import lyricwikia
# Asynchronous calls to dbus loops
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
DBusGMainLoop(set_as_default=True)


# PLAYER CLASS WITH VLC AND DBUS PROPERTIES
class Player:
    def __init__(self, session_bus, bus_name, connect = True,
            debug = False, vlc_args = "", fullscreen = False):
        # Main player properties
        self.metadata = {
                'artist' : '',
                'title'  : ''
        }
        self.status = 'stopped'
        self._debug = debug
        self._fullscreen = fullscreen

        # VLC Instance
        _args = vlc_args
        if self._debug: _args += " --verbose 1"
        else: _args += " --quiet"
        try:
            self._instance = vlc.Instance(_args)
        except NameError:
            self._error("VLC is not installed")
            quit()
        self.video_player = self._instance.media_player_new()

        # DBus internal properties
        self._session_bus = session_bus
        self._bus_name = bus_name
        self._disconnecting = False
        self._connect = connect
        try:
            self._obj = self._session_bus.get_object(self._bus_name, '/org/mpris/MediaPlayer2')
        except dbus.exceptions.DBusException as e:
            self._error("No spotify session running")
            exit()
        self._properties_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Properties")
        self._introspect_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Introspectable")
        self._media_interface      = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2')
        self._player_interface     = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2.Player')
        self._introspect = self._introspect_interface.get_dbus_method('Introspect', dbus_interface=None)
        self._loop = GLib.MainLoop()
        self._signals = {}

        self._refresh_status()
        self._refresh_metadata()
        if self._connect: self.do_connect()
    
    # Connects to the dbus signals
    def do_connect(self):

        if self._disconnecting is False:
            introspect_xml = self._introspect(self._bus_name, '/')
            if 'TrackMetadataChanged' in introspect_xml:
                self._signals['track_metadata_changed'] = self._session_bus.add_signal_receiver(self._refresh_metadata, 'TrackMetadataChanged', self._bus_name)
            self._properties_interface.connect_to_signal('PropertiesChanged', self._on_properties_changed)

    # Disconnects from the dbus signals
    def do_disconnect(self):
        self._log("Disconnecting")
        self._disconnecting = True
        for signal_name, signal_handler in list(self._signals.items()):
            signal_handler.remove()
            del self._signals[signal_name]

    # Waits for changes in dbus properties
    def wait(self):
        self._log("Starting loop")
        self._loop.run()

    # Refreshes the status of the player (play/pause)
    def _refresh_status(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self.status = str(self._properties_interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')).lower()
        except dbus.exceptions.DBusException as e:
            self._error(e)
            self.do_disconnect()

    # Refreshes the metadata of the player (artist, title)
    def _refresh_metadata(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self._assign_metadata()
        except dbus.exceptions.DBusException as e:
            self._error(e)
            self.do_disconnect()

    # Assigns the new metadata to the class's properties
    def _assign_metadata(self):
        _metadata = self._properties_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        self.metadata = self._formatted_metadata(_metadata)

    # Returns a formatted object from raw metadata
    def _formatted_metadata(self, metadata):
        return { 'artist' : metadata['xesam:artist'][0], 'title' : metadata['xesam:title'] }

    # Returns a formatted name with the artist and the title 
    def format_name(self):
        return self.metadata['artist'] + " - " + self.metadata['title']

    # Function called asynchronously from dbus on property changes
    def _on_properties_changed(self, interface, properties, signature):
        # Format the new metadata. If it's different, break the loop
        if dbus.String('Metadata') in properties:
            _new_metadata = self._formatted_metadata(properties[dbus.String('Metadata')])
            if _new_metadata != self.metadata:
                self._log("New video")
                self._assign_metadata()
                self._loop.quit()

        # Paused/Played
        if dbus.String('PlaybackStatus') in properties:
            status = str(properties[dbus.String('PlaybackStatus')]).lower()
            if status != self.status:
                self._log("Paused/Played video")
                self.status = status
                self.toggle_pause()

    # Plays/Pauses the VLC player
    def toggle_pause(self):
        if self.status == "paused":
            self.video_player.pause()
        else:
            self.video_player.play()

    # Starts a new video on the VLC player
    def start_video(self, filename, offset = 0):
        self._log("Starting video with offset " + str(offset))
        # Media instance
        Media = self._instance.media_new(filename)
        Media.get_mrl()
        # Player instance
        self.video_player.set_media(Media)
        if self.status == "playing":
            self.video_player.play()
        self.video_player.set_time(offset)
        self.video_player.set_fullscreen(self._fullscreen)

    # Returns the song lyrics
    def get_lyrics(self):
        # First tries using lyricwikia
        try:
            return lyricwikia.get_lyrics(self.metadata['artist'], self.metadata['title'])
        except lyricwikia.LyricsNotFound:
            return "No lyrics found"

    # Prints formatted logs to the console
    def _log(self, msg):
        if self._debug:
            print("\033[92m>> " + msg + "\033[0m")

    # Prints formatted errors to the console
    def _error(self, msg):
        print("\033[91m[ERROR]: " + msg + "\033[0m")

