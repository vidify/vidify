#! /usr/bin/pn
import os
import vlc
import dbus
import requests
from libs import youtube
# Asynchronous calls
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
DBusGMainLoop(set_as_default=True)

debug = True

def log(msg):
    if debug:
        print("\033[92m>> " + msg + "\033[0m")

def error(msg):
    print("\033[91m[ERROR]: " + msg + "\033[0m")


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
        self.videos = {}

        # VLC Instance
        self._instance = vlc.Instance(
                "--quiet " + # Don't print warnings to stdout
                "--no-qt-error-dialogs" # Don't print errors to stdout
        )
        self.video_player = self._instance.media_player_new()

        # DBus internal properties
        try:
            self._obj = self._session_bus.get_object(self.bus_name, '/org/mpris/MediaPlayer2')
        except dbus.exceptions.DBusException as e:
            error("No spotify session running")
            exit()
        self._properties_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Properties")
        self._introspect_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Introspectable")
        self._media_interface      = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2')
        self._player_interface     = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2.Player')
        self._introspect = self._introspect_interface.get_dbus_method('Introspect', dbus_interface=None)
        self._loop = GLib.MainLoop()
        self._signals = {}

        self.refreshStatus()
        self.refreshMetadata()
        if self._connect: self.do_connect()

    def do_connect(self):
        log("Connecting")
        if self._disconnecting is False:
            introspect_xml = self._introspect(self.bus_name, '/')
            if 'TrackMetadataChanged' in introspect_xml:
                self._signals['track_metadata_changed'] = self._session_bus.add_signal_receiver(self.refreshMetadata, 'TrackMetadataChanged', self.bus_name)
            self._properties_interface.connect_to_signal('PropertiesChanged', self.onPropertiesChanged)

    def disconnect(self):
        log("Disconnecting")
        self._disconnecting = True
        for signal_name, signal_handler in list(self._signals.items()):
            signal_handler.remove()
            del self._signals[signal_name]

    # Waits for changes in dbus properties
    def wait(self):
        log("Starting loop")
        try:
            self._loop.run()
        except KeyboardInterrupt:
            log("Removing cache...")
            os.system("rm downloads/* &>/dev/null")
            exit()

    # Stops loop to start the next song
    def stop_loop(self):
        log("Stopping loop")
        self._loop.quit()

    def refreshStatus(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self.status = str(self._properties_interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')).lower()
        except dbus.exceptions.DBusException as e:
            error(e)
            self.disconnect()

    def refreshMetadata(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self._assignMetadata()
        except dbus.exceptions.DBusException as e:
            error(e)
            self.disconnect()

    # Assigns the new metadata to the class's properties
    def _assignMetadata(self):
        _metadata = self._properties_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        self.metadata = self._formatMetadata(_metadata)

    # Creates an object with raw metadata
    def _formatMetadata(self, metadata):
        return { 'artist' : metadata['xesam:artist'][0], 'title' : metadata['xesam:title'] }

    def formatName(self):
        return self.metadata['artist'] + " - " + self.metadata['title']

    def onPropertiesChanged(self, interface, properties, signature):
        # Format the new metadata. If it's different, break the loop
        if dbus.String('Metadata') in properties:
            _new_metadata = self._formatMetadata(properties[dbus.String('Metadata')])
            if _new_metadata != self.metadata:
                log("New video")
                self.metadata = _new_metadata
                self._assignMetadata()
                self.stop_loop()
        # Paused/Played
        if dbus.String('PlaybackStatus') in properties:
            status = str(properties[dbus.String('PlaybackStatus')]).lower()
            if status != self.status:
                log("Paused video")
                self.status = status
                self.toggle_pause()

    def toggle_pause(self):
        if self.status == "paused":
            self.video_player.pause()
        else:
            self.video_player.play()

    def get_current_position(self):
        return self._properties_interface.Get("org.mpris.MediaPlayer2.Player", "Position")

    def start_video(self, filename):
        log("Starting video")
        # Media instance
        Media = self._instance.media_new(filename)
        Media.get_mrl()
        # Player instance
        self.video_player.set_media(Media)
        self.video_player.set_time(self.get_current_position())
        if self.status == "playing":
            self.video_player.play()

    def get_lyrics(self):
        pageurl = "https://makeitpersonal.co/lyrics?artist=" + self.metadata['artist'] + "&title=" + self.metadata['title']
        lyrics = requests.get(pageurl).text.strip()
        return lyrics


# Plays the video until a new song is found
def main(player):
    name = player.formatName()
    
    # Only downloading the video if it's not listed
    if name not in player.videos:
        filename = youtube.download_video(name)
        player.videos[name] = filename
    else:
        filename = player.videos[name]

    print("\033[4m" + name + "\033[0m")
    print("----------------------")
    print(player.get_lyrics())
    player.start_video(filename)

    # Waiting for the song to finish
    player.wait()
    log("Finished loop")

    main(player)


if __name__ == '__main__':
    player = Player(
            dbus.SessionBus(),
            "org.mpris.MediaPlayer2.spotify"
    )
    main(player)

