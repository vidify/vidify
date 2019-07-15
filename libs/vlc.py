import vlc
import dbus

# VLC Instance
Instance = vlc.Instance(
        "--quiet " + # Don't print warnings to stdout
        "--no-qt-error-dialogs" # Don't print errors to stdout
)
player = Instance.media_player_new()

# playing the video on VLC
def start_video(filename, offset):
    # Media instance
    Media = Instance.media_new(filename)
    Media.get_mrl()
    # Player instance
    player.set_media(Media)
    player.set_time(get_current_position())
    if get_audio_status() == "Playing":
        player.play()


session_bus = dbus.SessionBus()
proxy = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
device_prop = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
# Returns the status of the dbus stream (Paused/Playing)
def get_audio_status():
    return device_prop.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")

# Returns the current position of the dbus stream in milliseconds
def get_current_position():
    return device_prop.Get("org.mpris.MediaPlayer2.Player", "Position")

def toggle_pause(status):
    if status == "Paused":
        player.pause()
    else:
        player.play()
    

