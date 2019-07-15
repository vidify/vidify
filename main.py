#! /usr/bin/pn
import os

from libs import vlc
from libs import yt
from libs import spotify


# Dictionary with previous downloads to not repeat
videos = {}


# Plays the video until a new song is found
def main(artist, title):
    name = spotify.format_name(artist, title)

    # Only downloading the video if it's not listed
    if name not in videos:
        print(">> Downloading '" + name + "'")
        filename = yt.download_video(name)
        videos[name] = filename
    else:
        print(">> '" + name + "' is already downloaded")
        filename = videos[name]

    print(">> Playing '" + name + "'")
    vlc.play_video(filename)
    spotify.get_lyrics(artist, title)

    # Waiting for the song to finish
    while True:
        artist, title = spotify.get_name()
        new_name = spotify.format_name(artist, title)
        if new_name != name:
            break
    main(artist, title)


if __name__ == '__main__':
    artist, title = spotify.get_name()
    try:
        main(artist, title)
    except KeyboardInterrupt:
        print("\n>> Removing cache...")
        os.system("rm downloads/*")
        exit()

