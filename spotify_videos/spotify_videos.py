import os
import sys
import time
import platform
import argparse
import lyricwikia
from contextlib import contextmanager
from .player import WebPlayer, DBusPlayer, VLCWindow


# Argument parsing
parser = argparse.ArgumentParser(
        description = "Windows and Mac users must pass --username, --client-id and --client-secret to use the web API. Read more about how to obtain them in the README (https://github.com/marioortizmanero/spotify-music-videos).",
)
parser.add_argument('-v', '--version', action='version',
        version='%(prog)s 1.4.4', help="show program's version number and exit.")
parser.add_argument("--debug", action="store_true", dest="debug",
        default=False, help="display debug messages")
parser.add_argument("-n", "--no-lyrics", action="store_false", dest="lyrics",
        default=True, help="do not print lyrics")
parser.add_argument("-f", "--fullscreen", action="store_true", dest="fullscreen",
        default=False, help="play videos in fullscreen mode")
parser.add_argument("-a", "--args", action="store", dest="vlc_args",
        default="", help="other arguments used when opening VLC. Note that some like args='--fullscreen' won't work in here")
parser.add_argument("--width", action="store", dest="max_width",
        default="", help="set the maximum width for the played videos")
parser.add_argument("--height", action="store", dest="max_height",
        default="", help="set the maximum height for the played videos")

parser.add_argument("-w", "--use-web-api", action="store_true", dest="use_web_api",
        default=False, help="forcefully use Spotify's web API")
parser.add_argument("--username", action="store", dest="username",
        default="", help="your Spotify username. Mandatory if the web API is being used. Example: --username='yourname'")
parser.add_argument("--client-id", action="store", dest="client_id",
        default="", help="your client ID. Mandatory if the web API is being used. Check the README to see how to obtain yours. Example: --client-id='5fe01282e44241328a84e7c5cc169165'")
parser.add_argument("--client-secret", action="store", dest="client_secret",
        default="", help="your client secret ID. Mandatory if the web API is being used. Check the README to see how to obtain yours. Example: --client-secret='2665f6d143be47c1bc9ff284e9dfb350'")
parser.add_argument("--redirect-uri", action="store", dest="redirect_uri",
        default="http://localhost:8888/callback/", help="the redirect URI for the web API. Not necessary as it defaults to 'http://localhost:8888/callback/'")

args = parser.parse_args()


# Hiding stderr without leaks
@contextmanager
def stderr_redirected(to: str = os.devnull) -> None:
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
if args.max_width: ydl_opts['format'] += f"[width<={args.max_width}]"
if args.max_height: ydl_opts['format'] += f"[height<={args.max_height}]"


# Prints the current song lyrics
def print_lyrics(artist: str, title: str) -> None:
    if args.lyrics:
        print(f"\033[4m{artist} - {title}\033[0m")
        try:
            print(lyricwikia.get_lyrics(artist, title) + "\n")
        except lyricwikia.LyricsNotFound:
            print("No lyrics found\n")


# Plays the videos with the DBus API (Linux)
def play_videos_dbus(player: VLCWindow, spotify: DBusPlayer) -> None:
    while True:
        start_time = time.time()

        # Downloads and plays the video with the offset
        url = player.get_url(
                f"{spotify.artist} - {spotify.title} Official Video",
                ydl_opts)
        player.start_video(url)

        if spotify.is_playing:
            player.play()
            # Waits until VLC actually plays the video to set the offset in sync
            while player.get_position() == 0:
                pass
            offset = int((time.time() - start_time) * 1000)
            player.set_position(offset)

        print_lyrics(spotify.artist, spotify.title)

        # Waiting for Spotify events
        spotify.wait()


# Plays the videos with the web API (Other OS)
def play_videos_web(player: VLCWindow, spotify: WebPlayer) -> None:
    while True:
        # Starts video at exact position
        url = player.get_url(
                f"{spotify.artist} - {spotify.title} Official Video",
                ydl_opts)
        player.start_video(url)

        if spotify.is_playing:
            player.play()
        offset = spotify.get_position()
        player.set_position(offset)
        
        print_lyrics(spotify.artist, spotify.title)

        # Waiting for the current song to change
        spotify.wait()


def choose_platform() -> None:
    player = VLCWindow(
                debug = args.debug,
                vlc_args = args.vlc_args,
                fullscreen = args.fullscreen)

    if platform.system() == "Linux" and not args.use_web_api:
        spotify = DBusPlayer(
                player,
                debug = args.debug)
        play_videos_dbus(spotify.player, spotify)
    else:
        spotify = WebPlayer(
                player,
                debug = args.debug,
                username = args.username,
                client_id = args.client_id,
                client_secret = args.client_secret,
                redirect_uri = args.redirect_uri)
        play_videos_web(spotify.player, spotify)


def main() -> None:
    if args.debug:
        choose_platform()
    else:
        with stderr_redirected(os.devnull):
            choose_platform()


if __name__ == '__main__':
    main()

