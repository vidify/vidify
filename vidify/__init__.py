"""
This module has utilities used in different parts of the program, like the
logger, cross-platform variables...
"""

import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from pkg_resources import DistributionNotFound, get_distribution


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
if sys.platform.startswith("linux"):
    CUR_PLATFORM = Platform.LINUX
elif sys.platform.startswith("darwin"):
    CUR_PLATFORM = Platform.MACOS
elif sys.platform.startswith("win"):
    CUR_PLATFORM = Platform.WINDOWS
elif sys.platform.find("bsd") != -1:
    CUR_PLATFORM = Platform.BSD
else:
    CUR_PLATFORM = Platform.UNKNOWN


def is_installed(*args: str) -> bool:
    for pkgname in args:
        try:
            get_distribution(pkgname)
        except DistributionNotFound:
            return False
    return True


def format_name(artist: Optional[str], title: Optional[str]) -> str:
    """
    Formatting the song name with the artist and title.

    Some songs may not have an artist name or title so the formatting has to
    use all it has.
    """

    def is_empty(s: str):
        return s in (None, "")

    if is_empty(artist) and is_empty(title):
        return ""

    if is_empty(artist):
        return title

    if is_empty(title):
        return artist

    return f"{artist} - {title}"


@dataclass(frozen=True)
class BaseModuleData:
    """
    This dataclass describes the base attributes of an API or Player inside
    vidify.api or vidify.player, respectively. These attributes are used
    to display information to the user about the modules, and to
    initialize them programatically.
    """

    name: str
    short_name: str
    description: str
    icon: str
    compatible: bool
    installed: bool
    module: str
    class_name: str


def find_module(data: Tuple[BaseModuleData], module_id: str) -> BaseModuleData:
    for element in data:
        if element.name == module_id:
            return element

    raise ValueError("Module with id {module_id} not found")
