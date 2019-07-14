#! /usr/bin/pn
import youtube_dl
import vlc
import dbus

# youtube-dl configuration
ydl_opts = {
    'format' : '136/135/134/133',
    'outtmpl': 'downloads/%(id)s.%(ext)s'
}

ydl = youtube_dl.YoutubeDL(ydl_opts)

# getting currently playing from spotify with dbus (only for Linux with the app installed)
def get_video():
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    return 'ytsearch:' + metadata['xesam:artist'][0] + " - " + metadata['xesam:title']


# playing the video on VLC
def play_video(url):
    # Download the video, getting the filename
    info = ydl.extract_info(url, download=True)
    # Fix for error with prepare_filename inside youtube_dl
    filename = "downloads/" + info['entries'][0]['id'] + ".mp4"

    # VLC Instance
    Instance = vlc.Instance()
    # Media instance
    Media = Instance.media_new(filename)
    Media.get_mrl()
    # Player instance
    player = Instance.media_player_new()
    player.set_media(Media)
    player.play()


# Plays the video until a new song is found
def main(url):
    play_video(url)
    while True:
        new_url = get_video()
        if new_url != url:
            break
    main(new_url)


if __name__ == '__main__':
    url = get_video()
    main(url)

