#! /usr/bin/pn
import os
import vlc
import dbus
# Asynchronous calls
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
DBusGMainLoop(set_as_default=True)

from libs import youtube
from libs import spotify


# Player with dbus and vlc properties
class Player:
    def __init__(self, session_bus, bus_name, connect = True):
        self._session_bus = session_bus
        self.bus_name = bus_name
        self._disconnecting = False
        self._connect = connect
        self.metadata = {
                'artist' : '',
                'title'  : ''
        }
        self.status = 'stopped'

        # VLC Instance
        self._instance = vlc.Instance(
                "--quiet " + # Don't print warnings to stdout
                "--no-qt-error-dialogs" # Don't print errors to stdout
        )
        self.video_player = self._instance.media_player_new()

        # DBus internal properties
        self._obj = self._session_bus.get_object(self.bus_name, '/org/mpris/MediaPlayer2')
        self._properties_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Properties")
        self._introspect_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Introspectable")
        self._media_interface      = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2')
        self._player_interface     = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2.Player')
        self._introspect = self._introspect_interface.get_dbus_method('Introspect', dbus_interface=None)
        self._signals = {}

        self.refreshStatus()
        self.refreshMetadata()
        if self._connect: connect()

    # Waits for changes in dbus properties
    def wait(self):
        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            print("\n>> Removing cache...")
            os.system("rm downloads/* &>/dev/null")
            exit()

    def connect(self):
        if self._disconnecting is False:
            introspect_xml = self._introspect(self.bus_name, '/')
            if 'TrackMetadataChanged' in introspect_xml:
                self._signals['track_metadata_changed'] = self._session_bus.add_signal_receiver(self.refreshMetadata, 'TrackMetadataChanged', self.bus_name)
            self._properties_interface.connect_to_signal('PropertiesChanged', self.onPropertiesChanged)

    def disconnect(self):
        self._disconnecting = True
        for signal_name, signal_handler in list(self._signals.items()):
            signal_handler.remove()
            del self._signals[signal_name]

    def refreshStatus(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self.status = str(self._properties_interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')).lower()
        except dbus.exceptions.DBusException as e:
            print("[ERROR]", e)
            self.disconnect()

    def refreshMetadata(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self._parseMetadata()
        except dbus.exceptions.DBusException as e:
            print("[ERROR]", e)
            self.disconnect()

    def _parseMetadata(self):
            _metadata = self._properties_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            self.metadata['artist'] = _metadata['xesam:artist'][0]
            self.metadata['title'] = _metadata['xesam:title']

    def formatName(self):
        return self.metadata['artist'] + " - " + self.metadata['title']

    def onPropertiesChanged(self, interface, properties, signature):
        if dbus.String('Metadata') in properties:
            _metadata = properties[dbus.String('Metadata')]
            if _metadata != self.metadata:
                self._parseMetadata()
        if dbus.String('PlaybackStatus') in properties:
            status = str(properties[dbus.String('PlaybackStatus')]).lower()
            if status != self.status:
                self.status = status

    def toggle_pause(self):
        if self.status == "paused":
            self.video_player.pause()
        else:
            self.video_player.play()

    def get_current_position(self):
        return self._properties_interface.Get("org.mpris.MediaPlayer2.Player", "Position")

    def start_video(self, filename):
        # Media instance
        Media = self._instance.media_new(filename)
        Media.get_mrl()
        # Player instance
        self.video_player.set_media(Media)
        self.video_player.set_time(self.get_current_position())
        if self.status == "playing":
            self.video_player.play()


# Dictionary with previous downloads to not repeat
videos = {}


# Plays the video until a new song is found
def main(player):
    name = player.formatName()
    
    # Only downloading the video if it's not listed
    if name not in videos:
        filename = youtube.download_video(name)
        videos[name] = filename
    else:
        filename = videos[name]

    player.start_video(filename)

    print("\033[4m" + name + "\033[0m")
    print("----------------------")
    print(spotify.get_lyrics(player.metadata['artist'], player.metadata['title']))

    # Waiting for the song to finish
    metadata = player.metadata
    player.wait()

    main(player)


if __name__ == '__main__':
    player = Player(
            dbus.SessionBus(),
            "org.mpris.MediaPlayer2.spotify",
            connect = False
    )
    main(player)

