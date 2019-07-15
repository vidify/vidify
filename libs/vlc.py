import vlc
import dbus

# VLC Instance
Instance = vlc.Instance(
        "--quiet " + # Don't print warnings to stdout
        "--no-qt-error-dialogs" # Don't print errors to stdout
)
player = Instance.media_player_new()

# playing the video on VLC
def start_video(filename):
    # Media instance
    Media = Instance.media_new(filename)
    Media.get_mrl()
    # Player instance
    player.set_media(Media)
    player.set_time(get_current_position())
    print(get_current_position())
    if get_audio_status() == "Playing":
        player.play()


# Accessing properties from dbus
session_bus = dbus.SessionBus()
def get_audio_status():
    proxy = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    device_prop = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
    return device_prop.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
def get_current_position():
    proxy = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    device_prop = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
    return device_prop.Get("org.mpris.MediaPlayer2.Player", "Position")

def toggle_pause(status):
    if status == "Paused" or status == "paused":
        player.pause()
    else:
        player.play()
    
