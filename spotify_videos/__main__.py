import time
import platform
import logging
from typing import Callable

import youtube_dl
import lyricwikia

from .web_api import WebAPI
from .dbus_api import DBusAPI
from .vlc_player import VLCPlayer
from .argparser import Parser
from .utils import stderr_redirected, ConnectionNotReady


# Argument parser initialization
parser = Parser()
args = parser.parse()

# Logger initialzation with precise milliseconds handler
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s.%(msecs)03d]"
                              "%(levelname)s: %(message)s", datefmt="%H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Youtube-dl config
ydl_opts = {
    'format': 'bestvideo',
    'quiet': True
}

if args.max_width is not None:
    ydl_opts['format'] += f"[width<={args.max_width}]"

if args.max_height is not None:
    ydl_opts['format'] += f"[height<={args.max_height}]"

# Turning on debug modes for VLC and youtube-dl if the
# debug argument was passed
if args.debug:
    logger.setLevel(logging.DEBUG)
    args.vlc_args += " --verbose 1"
    ydl_opts['quiet'] = False
else:
    logger.setLevel(logging.ERROR)
    args.vlc_args += " --quiet"


def format_name(artist: str, title: str) -> str:
    """
    Some local songs may not have an artist name so the formatting
    has to be different. Also, "Official Video" is added to the query
    to get more accurate results.
    """
    if artist is None or artist == "":
        return f"{title}"
    else:
        return f"{artist} - {title}"


def get_url(artist: str, title: str) -> str:
    """
    Getting the youtube direct link to play it directly with VLC.
    """

    name = format_name(artist, title)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:'{name} Official Video'",
                                download=False)
    return info['entries'][0]['url']


def print_lyrics(artist: str, title: str) -> None:
    """
    Using lyricwikia to get lyrics
    """

    name = format_name(artist, title)

    print(f"\033[4m{name}\033[0m")
    try:
        print(lyricwikia.get_lyrics(artist, title) + "\n")
    except (lyricwikia.LyricsNotFound, AttributeError):
        print("No lyrics found\n")


def play_videos_dbus(player: VLCPlayer, spotify: DBusAPI) -> None:
    """
    Playing videos with the DBus API (Linux).

    Spotify doesn't currently support the MPRIS property `Position`
    so the starting offset is calculated manually and may be a bit rough.

    After playing the video, the player waits for DBus events like
    pausing the video.
    """

    while True:
        start_time = time.time()

        url = get_url(spotify.artist, spotify.title)
        player.start_video(url)

        if spotify.is_playing:
            player.play()
            # Waits until VLC actually plays the video to set the offset
            while player.get_position() == 0:
                pass
            offset = int((time.time() - start_time) * 1000)
            player.set_position(offset)
            logging.debug(f"Starting offset is {offset}")

        if args.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        spotify.wait()


def play_videos_web(player: VLCPlayer, spotify: WebAPI) -> None:
    """
    Playing videos with the Web API (macOS, Windows).

    Unlike the DBus API, the position can be requested and synced easily.
    """

    while True:
        url = get_url(spotify.artist, spotify.title)
        player.start_video(url)

        if spotify.is_playing:
            player.play()
        offset = spotify.get_position()
        player.set_position(offset)

        if args.lyrics:
            print_lyrics(spotify.artist, spotify.title)

        spotify.wait()


def wait_for_connection(connect: Callable, msg: str,
                        attempts: int = 30) -> bool:
    """
    Waits for a Spotify session to be opened or for a song to play.
    Times out after <attempts> seconds to avoid infinite loops and to
    avoid too many API/process requests.

    Returns True if the connect was succesfull and False otherwise.
    """

    counter = 0
    while counter < attempts:
        try:
            connect()
        except ConnectionNotReady:
            if counter == 0:
                print(msg)
            counter += 1
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        else:
            return True
    else:
        print("Timed out")

    return False


def choose_platform() -> None:
    """
    Chooses a platform, waits for the API to be ready and starts
    playing videos. Linux will use the DBus API unless the
    --use-web-api flag was passed.
    """

    player = VLCPlayer(logger, args.vlc_args, args.fullscreen)

    if platform.system() == "Linux" and not args.use_web_api:
        dbus_spotify = DBusAPI(player, logger)

        if wait_for_connection(
                dbus_spotify.do_connect,
                "Waiting for a Spotify session to be ready..."):
            play_videos_dbus(dbus_spotify.player, dbus_spotify)
    else:
        web_spotify = WebAPI(player, logger, args.username,
                             args.client_id, args.client_secret)

        if wait_for_connection(
                web_spotify.do_connect,
                "Waiting for a Spotify song to play..."):
            play_videos_web(web_spotify.player, web_spotify)


def main() -> None:
    """
    Redirects stderr to /dev/null if debug is turned off, since
    sometimes VLC will throw non-fatal errors even when configured
    to be quiet.
    """

    if args.debug:
        choose_platform()
    else:
        with stderr_redirected():
            choose_platform()


if __name__ == '__main__':
    main()
