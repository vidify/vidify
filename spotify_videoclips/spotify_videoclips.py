import os
import sys
import platform
import argparse
import lyricwikia
from datetime import datetime
from contextlib import contextmanager
from .player import VLCWindow


# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", action="store_true", dest="debug",
        default=False, help="turn on debug mode")
parser.add_argument("-n", "--no-lyrics", action="store_false", dest="lyrics",
        default=True, help="do not display lyrics")
parser.add_argument("-f", "--fullscreen", action="store_true", dest="fullscreen",
        default=False, help="play videos in fullscreen mode")
parser.add_argument("-a", "--args", action="store", dest="vlc_args",
        default="", help="other arguments used when opening VLC. Note that some like args='--fullscreen' won't work in here")

parser.add_argument("-w", "--use-web-api", action="store_true", dest="use_web_api",
        default=False, help="use Spotify's web API (only Linux doesn't use it by default)")
parser.add_argument("--username", action="store", dest="username",
        default="", help="your Spotify username. Mandatory if the web API is being used")
parser.add_argument("--client-id", action="store", dest="client_id",
        default="", help="your client ID. Mandatory if the web API is being used. Check the README to see how to obtain yours")
parser.add_argument("--client-secret", action="store", dest="client_secret",
        default="", help="your client secret ID. Mandatory if the web API is being used. Check the README to see how to obtain yours")
parser.add_argument("--redirect-uri", action="store", dest="redirect_uri",
        default="http://localhost:8888/callback/", help="the redirect URI. Not necessary as it defaults to 'http://localhost:8888/callback/'")

args = parser.parse_args()


# Hiding stderr without leaks
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


# youtube-dl config
ydl_opts = {
    'format' : 'bestvideo',
    'quiet'  : True
}
if args.debug: ydl_opts['quiet'] = False


# Returns a formatted name with the artist and the title
def format_name(spotify):
    return spotify.artist + " - " + spotify.title


# Prints the current song lyrics
def print_lyrics(spotify):
    if args.lyrics:
        print("\033[4m" + format_name(spotify) + "\033[0m")
        try:
            print(lyricwikia.get_lyrics(spotify.artist, spotify.title) + "\n")
        except lyricwikia.LyricsNotFound:
            print("No lyrics found" + "\n")


# Plays the videos with the dbus API (Linux)
def play_videos_dbus(player, spotify):
    while True:
        name = format_name(spotify)

        # Counts milliseconds to add a delay and sync the start
        start_time = datetime.now()
        url = player.get_url(name, ydl_opts)
        player.start_video(url)
        offset = int((datetime.now() - start_time).total_seconds() * 1000)
        player.set_position(offset)
        if spotify.is_playing:
            player.play()

        print_lyrics(spotify)

        # Waiting for the current song to change
        spotify.wait()


# Plays the videos with the web API (Other OS)
def play_videos_web(player, spotify):
    while True:
        name = format_name(spotify)

        # Starts video at exact position
        url = player.get_url(name, ydl_opts)
        player.start_video(url)
        offset = spotify.get_position()
        player.set_position(offset)
        if spotify.is_playing:
            player.play()
        
        print_lyrics(spotify)

        # Waiting for the current song to change
        spotify.wait()


def choose_platform():
    if platform.system() == "Linux" and not args.use_web_api:
        from .player import DbusPlayer
        spotify = DbusPlayer(
                debug = args.debug,
                vlc_args = args.vlc_args,
                fullscreen = args.fullscreen
        )
        play_videos_dbus(spotify.player, spotify)
    else:
        from .player import WebPlayer
        spotify = WebPlayer(
                debug = args.debug,
                username = args.username,
                client_id = args.client_id,
                client_secret = args.client_secret,
                redirect_uri = args.redirect_uri,
                vlc_args = args.vlc_args,
                fullscreen = args.fullscreen
        )
        play_videos_web(spotify.player, spotify)


def main():
    if args.debug:
        choose_platform()
    else:
        with stderr_redirected(os.devnull):
            choose_platform()


if __name__ == '__main__':
    main()

