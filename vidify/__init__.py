"""
This module has utilities used in different parts of the program, like the
logger, cross-platform variables...
"""

import sys
from enum import Enum
from typing import Optional


class Platform(Enum):
    """
    Listing the supported platforms in an enumeration.
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


def format_name(artist: Optional[str], title: Optional[str]) -> str:
    """
    Formatting the song name with the artist and title.

    Some songs may not have an artist name or title so the formatting has to
    use all it has.
    """

    is_empty = lambda x: x in (None, '')

    if is_empty(artist) and is_empty(title):
        return ''
    elif is_empty(artist):
        return title
    elif is_empty(title):
        return artist
    else:
        return f"{artist} - {title}"
