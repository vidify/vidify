#! /usr/bin/pn
import youtube_dl
import vlc
import dbus
import os

# youtube-dl configuration
ydl_opts = {
    'format' : '136/135/134/133',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet' : 'true'
}
ydl = youtube_dl.YoutubeDL(ydl_opts)

# Dictionary with previous downloads to not repeat
videos = {}

# getting currently playing from spotify with dbus (only for Linux with the app installed)
def get_name():
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    return metadata['xesam:artist'][0] + " - " + metadata['xesam:title']


def download_video(name):
    # Download the video, getting the filename
    info = ydl.extract_info("ytsearch:" + name, download=True)
    # Fix for error with prepare_filename inside youtube_dl
    return "downloads/" + info['entries'][0]['id'] + ".mp4"


# playing the video on VLC
def play_video(filename):
    # VLC Instance
    Instance = vlc.Instance(
            "--play-and-exit " + # Closing after the song is finished
            "--quiet " # Don't print to stdout
    )
    # Media instance
    Media = Instance.media_new(filename)
    Media.get_mrl()
    # Player instance
    player = Instance.media_player_new()
    player.set_media(Media)
    player.play()


# Plays the video until a new song is found
def main(name):
    # Only downloading the video if it's not listed
    if name not in videos:
        print(">> Downloading '" + name + "'")
        filename = download_video(name)
        videos[name] = filename
    else:
        print(">> '" + name + "' is already downloaded")
        filename = videos[name]
    print(">> Playing '" + name + "'")
    play_video(filename)

    # Waiting for the song to finish
    while True:
        new_name = get_name()
        if new_name != name:
            break
    main(new_name)


if __name__ == '__main__':
    name = get_name()
    try:
        main(name)
    except KeyboardInterrupt:
        print("\n>> Removing cache...")
        os.system("rm downloads/*")
        exit()

