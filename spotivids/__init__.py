"""
This module has utilities used in different parts of the program, like the
logger, cross-platform variables...
"""

import sys
from enum import Enum


class Platform(Enum):
    """
    Listing the supported platforms.
    """

    LINUX = 1
    BSD = 2
    MACOS = 3
    WINDOWS = 4
    UNKNOWN = 5


# Getting the current platform as a global variable
if sys.platform.startswith('linux'):
    CURRENT_PLATFORM = Platform.LINUX
elif sys.platform.startswith('darwin'):
    CURRENT_PLATFORM = Platform.MACOS
elif sys.platform.startswith('win'):
    CURRENT_PLATFORM = Platform.WINDOWS
elif sys.platform.find('bsd') != -1:
    CURRENT_PLATFORM = Platform.BSD
else:
    CURRENT_PLATFORM = Platform.UNKNOWN


def format_name(artist: str, title: str) -> str:
    """
    Formatting the song name with the artist and title.

    Some local songs may not have an artist name so the formatting
    has to be different.
    """

    return title if artist in (None, '') else f"{artist} - {title}"
