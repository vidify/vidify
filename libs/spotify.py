import dbus
import requests

session_bus = dbus.SessionBus()

# getting currently playing from spotify with dbus (only for Linux with the app installed)
def get_name():
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    return metadata['xesam:artist'][0], metadata['xesam:title']


def format_name(artist, title):
    return artist + " - " + title


def get_lyrics(artist, title):
    pageurl = "https://makeitpersonal.co/lyrics?artist=" + artist + "&title=" + title
    lyrics = requests.get(pageurl).text.strip()
    return lyrics

