import os
import sys
import vlc
import argparse
import youtube_dl
import dbus
import lyricwikia
from datetime import datetime
from contextlib import contextmanager
# Asynchronous calls to dbus loops
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
DBusGMainLoop(set_as_default=True)


# DEBUGGING OPTIONS
def log(msg):
    if args.debug:
        print("\033[92m>> " + msg + "\033[0m")

def error(msg):
    print("\033[91m[ERROR]: " + msg + "\033[0m")


# ARGUMENT PARSING
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", dest="debug",
        default=False, help="turn on debug mode")
args = parser.parse_args()


# HIDING STDERR WITHOUT LEAKS
@contextmanager
def stderr_redirected(to=os.devnull):
    fd = sys.stderr.fileno()

    def _redirect_stderr(to):
        sys.stderr.close() # + implicit flush()
        os.dup2(to.fileno(), fd) # fd writes to 'to' file
        sys.stderr = os.fdopen(fd, 'w') # Python writes to fd

    with os.fdopen(os.dup(fd), 'w') as old_stderr:
        with open(to, 'w') as file:
            _redirect_stderr(to=file)
        try:
            yield # Allow code to be run with the redirected stderr
        finally:
            _redirect_stderr(to=old_stderr) # Restore stderr. Some flags may change


# YOUTUBE-DL CONFIGURATION
ydl_opts = {
    'format' : '136/135/134/133',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet'  : 'true'
}
if args.debug: ydl_opts['quiet'] = ''
ydl = youtube_dl.YoutubeDL(ydl_opts)


# PLAYER CLASS WITH VLC AND DBUS PROPERTIES
class Player:
    def __init__(self, session_bus, bus_name, connect = True):
        # Main player properties
        self.metadata = {
                'artist' : '',
                'title'  : ''
        }
        self.status = 'stopped'
        self.videos = {}

        # VLC Instance
        if args.debug: _args = ""
        else: _args = "--quiet"
        try:
            self._instance = vlc.Instance(_args)
        except NameError:
            error("VLC is not installed")
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
            error("No spotify session running")
            exit()
        self._properties_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Properties")
        self._introspect_interface = dbus.Interface(self._obj, dbus_interface="org.freedesktop.DBus.Introspectable")
        self._media_interface      = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2')
        self._player_interface     = dbus.Interface(self._obj, dbus_interface='org.mpris.MediaPlayer2.Player')
        self._introspect = self._introspect_interface.get_dbus_method('Introspect', dbus_interface=None)
        self._loop = GLib.MainLoop()
        self._signals = {}

        self.refresh_status()
        self.refresh_metadata()
        if self._connect: self.do_connect()
    
    # Connects to the dbus signals
    def do_connect(self):
        log("Connecting")
        if self._disconnecting is False:
            introspect_xml = self._introspect(self._bus_name, '/')
            if 'TrackMetadataChanged' in introspect_xml:
                self._signals['track_metadata_changed'] = self._session_bus.add_signal_receiver(self.refresh_metadata, 'TrackMetadataChanged', self._bus_name)
            self._properties_interface.connect_to_signal('PropertiesChanged', self.on_properties_changed)

    # Disconnects from the dbus signals
    def do_disconnect(self):
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

    # Refreshes the status of the player (play/pause)
    def refresh_status(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self.status = str(self._properties_interface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')).lower()
        except dbus.exceptions.DBusException as e:
            error(e)
            self.do_disconnect()

    # Refreshes the metadata of the player (artist, title)
    def refresh_metadata(self):
        # Some clients (VLC) will momentarily create a new player before removing it again
        # so we can't be sure the interface still exists
        try:
            self._assign_metadata()
        except dbus.exceptions.DBusException as e:
            error(e)
            self.do_disconnect()

    # Assigns the new metadata to the class's properties
    def _assign_metadata(self):
        _metadata = self._properties_interface.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        self.metadata = self._format_metadata(_metadata)

    # Returns a formatted object from raw metadata
    def _format_metadata(self, metadata):
        return { 'artist' : metadata['xesam:artist'][0], 'title' : metadata['xesam:title'] }

    # Returns a formatted name with the artist and the title 
    def format_name(self):
        return self.metadata['artist'] + " - " + self.metadata['title']

    # Function called asynchronously from dbus on property changes
    def on_properties_changed(self, interface, properties, signature):
        # Format the new metadata. If it's different, break the loop
        if dbus.String('Metadata') in properties:
            _new_metadata = self._format_metadata(properties[dbus.String('Metadata')])
            if _new_metadata != self.metadata:
                log("New video")
                self.metadata = _new_metadata
                self._assign_metadata()
                self.stop_loop()
        # Paused/Played
        if dbus.String('PlaybackStatus') in properties:
            status = str(properties[dbus.String('PlaybackStatus')]).lower()
            if status != self.status:
                log("Paused video")
                self.status = status
                self.toggle_pause()

    # Plays/Pauses the VLC player
    def toggle_pause(self):
        if self.status == "paused":
            self.video_player.pause()
        else:
            self.video_player.play()

    # Starts a new video on the VLC player
    def start_video(self, filename, offset):
        log("Starting video with offset " + str(offset))
        # Media instance
        Media = self._instance.media_new(filename)
        Media.get_mrl()
        # Player instance
        self.video_player.set_media(Media)
        if self.status == "playing":
            self.video_player.play()
        self.video_player.set_time(offset)

    # Returns the song lyrics
    def get_lyrics(self):
        # First tries using lyricwikia
        try:
            return lyricwikia.get_lyrics(self.metadata['artist'], self.metadata['title'])
        except lyricwikia.LyricsNotFound:
            return "No lyrics found"


# Download the video with youtube-dl and return the filename
def download_video(name):
    info = ydl.extract_info("ytsearch:" + name, download=True)
    # Fix for prepare_filename inconsistency from youtube-dl
    return "downloads/" + info['entries'][0]['id'] + ".mp4"


# Plays the video until a new song is found
def play_video(player):
    while True:
        name = player.format_name()

        # Counts seconds to add a delay and sync the start
        start_time = datetime.now()
        # Only downloading the video if it's not listed
        if name not in player.videos:
            filename = download_video(name)
            player.videos[name] = filename
        else:
            filename = player.videos[name]

        print("\033[4m" + name + "\033[0m")
        print(player.get_lyrics() + "\n")

        offset = int((datetime.now() - start_time).total_seconds() * 1000) # In milliseconds
        player.start_video(filename, offset)

        # Waiting for the song to finish
        player.wait()


# Player initialization and starting the main function
def main():
    player = Player(
            dbus.SessionBus(),
            "org.mpris.MediaPlayer2.spotify"
    )
    if args.debug:
        play_video(player)
    else:
        with stderr_redirected(os.devnull):
            play_video(player)


if __name__ == '__main__':
    main()

