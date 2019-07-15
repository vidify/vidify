import dbus
import requests

def get_lyrics(artist, title):
    pageurl = "https://makeitpersonal.co/lyrics?artist=" + artist + "&title=" + title
    lyrics = requests.get(pageurl).text.strip()
    return lyrics

