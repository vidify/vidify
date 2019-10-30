"""
This init module contains functions used throughout the different APIs.
"""

import re
from typing import Tuple


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
