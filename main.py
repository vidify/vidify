#! /usr/bin/pn
import os

from libs import vlc
from libs import yt
from libs import spotify


# Dictionary with previous downloads to not repeat
videos = {}


# Plays the video until a new song is found
def main(name):
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

    # Waiting for the song to finish
    while True:
        new_name = spotify.get_name()
        if new_name != name:
            break
    main(new_name)


if __name__ == '__main__':
    name = spotify.get_name()
    try:
        main(name)
    except KeyboardInterrupt:
        print("\n>> Removing cache...")
        os.system("rm downloads/*")
        exit()

