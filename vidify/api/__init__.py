"""
This init module contains functions used throughout the different APIs.

It's also used to list information about the APIs so that they can be
initialized the same programatically.
"""

import re
from dataclasses import dataclass
from typing import Tuple, Optional

from vidify import Platform, CURRENT_PLATFORM, is_installed, BaseModuleData
from vidify.gui import Res


@dataclass(frozen=True)
class APIData(BaseModuleData):
    """
    Information structure about the different APIs supported in this module,
    with a description for the user and how to initialize the API.
    """

    connect_msg: Optional[str] = None
    gui_init_fn: Optional[str] = None
    event_loop_interval: Optional[int] = None


APIS = (
    APIData(
        id="MPRIS_LINUX",
        short_name="Linux Media Players",
        description="Any MPRIS compatible media player: Spotify, Rhythmbox,"
                    " Clementine, VLC...",
        icon=Res.mpris_linux_icon,
        compatible=CURRENT_PLATFORM in (Platform.LINUX, Platform.BSD),
        installed=is_installed('pydbus'),
        module="vidify.api.mpris",
        class_name="MPRISAPI",
        connect_msg="Waiting for a song to play on any MPRIS player..."),

    APIData(
        id='SWSPOTIFY',
        short_name="Spotify for Windows and MacOS",
        description="The desktop Spotify client for Windows and MacOS.",
        icon=Res.swspotify_icon,
        compatible=CURRENT_PLATFORM in (Platform.WINDOWS, Platform.MACOS),
        installed=is_installed('swspotify'),
        module="vidify.api.spotify.swspotify",
        class_name="SwSpotifyAPI",
        connect_msg="Waiting for a Spotify song to play...",
        event_loop_interval=500),

    APIData(
        id='SPOTIFY_WEB',
        short_name="Spotify Web",
        description="The official Spotify Web API. Read"
        " <a href=\"https://vidify.org/wiki/spotify-web-api/\">the wiki</a>"
        " to learn how it works.",
        icon=Res.spotify_web_icon,
        compatible=True,
        installed=is_installed('tekore'),
        module="vidify.api.spotify.web",
        class_name="SpotifyWebAPI",
        connect_msg="Waiting for a Spotify song to play...",
        gui_init_fn="init_spotify_web_api",
        event_loop_interval=1000)
)


class ConnectionNotReady(Exception):
    """
    Exception used to notify the GUI from the API that the connection
    attempt was unsuccessful.
    """


def split_title(title: str) -> Tuple[str, str]:
    """
    Some local songs don't have an artist, so they are attempted
    to be split from the title manually with regex.

    The return is a tuple, with the order being: artist, title.

    The regex works with the following structures:
        Rick Astley - Never Gonna Give You Up
        Rick Astley: Never Gonna Give You Up
        Rick Astley : Never Gonna Give You Up
    """

    regex = r"(.+?)(?:(?:: )|(?: : )|(?: - ))(.+)"
    match = re.match(regex, title)

    if match is not None:
        if None not in (match.group(1), match.group(2)):
            return match.group(1), match.group(2)

    return '', title
