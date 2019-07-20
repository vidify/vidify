import os
import sys
import argparse
import youtube_dl
import dbus
import player
from contextlib import contextmanager


# ARGUMENT PARSING
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", dest="debug",
        default=False, help="turn on debug mode")
args = parser.parse_args()


# VLC PLAYER
player_run = False
player = player.Player(
        dbus.SessionBus(),
        "org.mpris.MediaPlayer2.spotify",
        debug = args.debug
)


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
def hook(d):
    global player, player_run
    # Starts playing the video as soon as the download starts
    if not player_run:
        player_run = True
        player.start_video(d['filename'])

ydl_opts = {
    'format' : 'bestvideo',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'progress_hooks': [hook],
    'nopart' : True,
    'quiet'  : True
}
if args.debug: ydl_opts['quiet'] = ''


# Search a youtube video and return both the future name and the url
def prepare_video(name):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info("ytsearch:" + name, download=False)
    # Fix for prepare_filename inconsistency from youtube-dl
    return [
            "downloads/" + info['entries'][0]['id'] + ".mp4", 
            info['entries'][0]['webpage_url']
            ]


# Plays the video until a new song is found
def play_video(player):
    global player_run
    while True:
        name = player.format_name()

        # Downloading the video
#         url = prepare_video(name)
#         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(["ytsearch:" + name])

        # Waiting for the song to finish
        player.wait()
        player_run = False


# Player initialization and starting the main function
def main():
    global player
    if args.debug:
        play_video(player)
    else:
        with stderr_redirected(os.devnull):
            play_video(player)


if __name__ == '__main__':
    main()

