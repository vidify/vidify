import time
import platform
import logging

import youtube_dl
import lyricwikia

from .web_player import WebPlayer
from .dbus_player import DBusPlayer
from .vlc import VLCWindow
from .argparser import Parser
from .utils import stderr_redirected


# Argument parser initialization
parser = Parser()
args = parser.parse()


# Youtube-dl config
ydl_opts = {
    'format' : 'bestvideo',
    'quiet'  : True
}

if args.max_width is not None:
    ydl_opts['format'] += f"[width<={args.max_width}]"

if args.max_height is not None:
    ydl_opts['format'] += f"[height<={args.max_height}]"

def get_url(name: str) -> str:
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info("ytsearch:" + name, download=False)
    return info['entries'][0]['url']


# Logger initialzation with precise handler
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

if args.debug:
    logger.setLevel(logging.DEBUG)
    args.vlc_args += " --verbose 1"
    ydl_opts['quiet'] = False
else:
    logger.setLevel(logging.ERROR)
    args.vlc_args += " --quiet"


# Using lyricwikia to get the song's lyrics
def print_lyrics(artist: str, title: str) -> None:
    print(f"\033[4m{artist} - {title}\033[0m")
    try:
        print(lyricwikia.get_lyrics(artist, title) + "\n")
    except (lyricwikia.LyricsNotFound, AttributeError):
        print("No lyrics found\n")


def format_name(artist: str, title: str):
    # Some local files don't have artist names
    if artist is None:
        return f"{title} Official Video"
    else:
        return f"{artist} - {title} Official Video"


# Plays the videos with the DBus API (Linux)
def play_videos_dbus(player: VLCWindow, spotify: DBusPlayer) -> None:
    while True:
        start_time = time.time()

        # Downloads and plays the video with the offset
        name = format_name(spotify.artist, spotify.title)
        url = get_url(name)
        player.start_video(url)

        if spotify.is_playing:
            player.play()
            # Waits until VLC actually plays the video to set the offset in sync
            while player.get_position() == 0:
                pass
            offset = int((time.time() - start_time) * 1000)
            player.set_position(offset)
            logging.debug(f"Starting offset is {offset}")

        if args.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        # Waiting for Spotify events
        spotify.wait()


# Plays the videos with the web API (other OS)
def play_videos_web(player: VLCWindow, spotify: WebPlayer) -> None:
    while True:
        # Starts video at exact position
        name = format_name(spotify.artist, spotify.title)
        url = get_url(name)
        player.start_video(url)

        if spotify.is_playing:
            player.play()
        offset = spotify.get_position()
        player.set_position(offset)

        if args.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        # Waiting for the current song to change
        spotify.wait()


def choose_platform() -> None:
    player = VLCWindow(
                logger,
                vlc_args = args.vlc_args,
                fullscreen = args.fullscreen)

    if platform.system() == "Linux" and not args.use_web_api:
        spotify = DBusPlayer(
                player,
                logger)
        play_videos_dbus(spotify.player, spotify)
    else:
        spotify = WebPlayer(
                player,
                logger,
                username = args.username,
                client_id = args.client_id,
                client_secret = args.client_secret)
        play_videos_web(spotify.player, spotify)


def main() -> None:
    if args.debug:
        choose_platform()
    else:
        with stderr_redirected():
            choose_platform()


if __name__ == '__main__':
    main()

