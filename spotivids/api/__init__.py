"""
This init module contains functions used throughout the different APIs.

It's also used to list, choose and control the APIs in a generic way, so that
they can be used the same throughout the entire module.
"""

import re
from typing import Tuple, Callable, Optional
from types import ModuleType
from enum import Enum

from spotivids import Platform


class APIs(Enum):
    """
    Simple information about the API shown to the user to choose the initial
    platform. The more detailed information about initializing the API and such
    is inside the API implementation file, because importing the module would
    cause issues with other imports inside it.
    """

    def __new__(self, value: int, description: str, icon: Optional[str],
                platforms: Tuple[Platform], module: str) -> None:
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.icon = icon
        # A tuple containing the supported platforms for this API. That way,
        # it's only shown in these.
        obj.platforms = platforms
        # The module location to import (for dependency injection).
        obj.module = module
        return obj

    SPOTIFY_LINUX = APIData(
        1,
        "Spotify for Linux",
        "The official Spotify client for Linux and BSD. Recommended.",
        None,
        (Platform.LINUX, Platform.BSD)
        "spotivids.api.linux")
    SWSPOTIFY = APIData(
        2,
        "Spotify for Windows or Mac OS",
        "The official Spotify client for Windows and Mac OS. Recommended.",
        None,
        (Platform.WINDOWS, Platform.MACOS),
        "spotivids.api.swspotify")
    SPOTIFY_WEB = APIData(
        3,
        "Spotify Web",
        "The official Spotify Web API. Please read the installation guide"
        " for more details on how to set it up.",
        None,
        [p for p in Platform],  # Supports all platforms
        "spotivids.api.web")


class ConnectionNotReady(Exception):
    """
    This exception is raised when no Spotify session is open or when
    no songs are currently playing, since it is better to catch them
    outside of the init function.
    """

    def __init__(self, msg: str = "Spotify is closed or there isn't a"
                 "  currently playing track."):
        super().__init__(msg)


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
