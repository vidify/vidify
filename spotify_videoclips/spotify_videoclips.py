import os
import sys
import argparse
import youtube_dl
import dbus
from datetime import datetime
from contextlib import contextmanager
import player


# ARGUMENT PARSING
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", dest="debug",
        default=False, help="turn on debug mode")
parser.add_argument("-n", "--no-lyrics", action="store_false", dest="lyrics",
        default=True, help="do not display lyrics")
parser.add_argument("-f", "--fullscreen", action="store_true", dest="fullscreen",
        default=False, help="play videos in fullscreen mode")
parser.add_argument("-a", "--args", action="store", dest="vlc_args",
        default="", help="other arguments used when opening VLC. Note that some like args='--fullscreen' won't work in here.")
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
    'format' : 'bestvideo',
    'quiet'  : True
}
if args.debug: ydl_opts['quiet'] = False


# Plays the video until a new song is found
def play_video(player):
    while True:
        name = player.format_name()

        # Counts seconds to add a delay and sync the start
        start_time = datetime.now()
        # Downloading the video
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("ytsearch:" + name, download=False)
        url = info['entries'][0]['url']

        offset = int((datetime.now() - start_time).total_seconds() * 1000) # In milliseconds
        player.start_video(url, offset)
        
        # Lyrics
        if args.lyrics:
            print("\033[4m" + name + "\033[0m")
            print(player.get_lyrics() + "\n")

        # Waiting for the song to finish
        player.wait()


# Player initialization and starting the main function
def main():
    p = player.dbusPlayer(
            dbus.SessionBus(),
            "org.mpris.MediaPlayer2.spotify",
            debug = args.debug,
            vlc_args = args.vlc_args
    )
    if args.debug:
        play_video(p)
    else:
        with stderr_redirected(os.devnull):
            play_video(p)


if __name__ == '__main__':
    main()

