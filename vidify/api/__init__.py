"""
This init module contains functions used throughout the different APIs.

It's also used to list, choose and control the APIs in a generic way, so that
they can be used the same throughout the entire module.

Here's a flow diagram with how the API initialization is done inside the
vidify.gui.window module and this one:

                +------------------ Is the API in the config?
                |       No
                |                               |
                |                               | Yes
                v                               v
  +-------------------------+     +--------------------------+
  | initialize APISelection |     | api.initialize_api       |
  |-------------------------|     |--------------------------|
  | Prompt the user for the +---->| Initialize the API       |
  | API to be used          |     | object using the APIData |
  +-------------------------+     | entry information        |
                                  +-------------+------------+
                                                |
                                                v

                +---------------- Does it need GUI interaction?
                |      Yes            (APIData.gui_init_fn)
                |
                |                               |
                |                               | No
                v                               v
   +------------------------+     +--------------------------+
   | Call custom function   |     | gui.start                |
   | from APIData which     |     |--------------------------|
   | handles initialization +---->| Wait for the API connect |
   | inside the GUI window  |     | Run the init function    |
   | (APIData.gui_init_fn)  |     | Start event loop         |
   +------------------------+     +--------------------------+

Made with http://stable.ascii-flow.appspot.com
"""

import re
import logging
from enum import Enum
from typing import Tuple, Optional

from vidify import Platform
from vidify.gui import Res


class APIData(Enum):
    """
    Information structure about the different APIs supported in this module.
    It contains information about the API and how to initialize it, following
    the top of this module's flow diagram with dependency injection.

    Note: all API entries must have their name in uppercase.
    """

    def __new__(cls, short_name: str, description: str, icon: Optional[str],
                platforms: Tuple[Platform], module: str, class_name: str,
                connect_msg: Optional[str], gui_init_fn: Optional[str],
                event_loop_interval: Optional[int]) -> object:
        obj = object.__new__(cls)
        # The short name displayed in the GUI, its description and the icon,
        # if existent. The description can use HTML tags like <b>.
        obj.short_name = short_name
        obj.description = description
        obj.icon = icon
        # A tuple containing the supported platforms for this API. That way,
        # it's only shown in these.
        obj.platforms = platforms
        # The module location and class name to import (for dependency
        # injection).
        obj.module = module
        obj.class_name = class_name
        obj.connect_msg = connect_msg
        obj.gui_init_fn = gui_init_fn
        obj.event_loop_interval = event_loop_interval
        return obj

    MPRIS_LINUX = (
        "Linux Media Players",
        "Any MPRIS compatible media player: Spotify, Rhythmbox... for "
        "<b>Linux</b> and <b>BSD</b>. Recommended.",
        Res.mpris_linux_icon,
        (Platform.LINUX, Platform.BSD),
        "vidify.api.mpris",
        "MPRISAPI",
        "Waiting for a song to play on any MPRIS player...",
        None,
        None)
    SWSPOTIFY = (
        "Spotify for Windows and MacOS",
        "The desktop Spotify client for <b>Windows</b> and <b>Mac OS</b> using"
        " SwSpotify. Recommended.",
        Res.swspotify_icon,
        (Platform.WINDOWS, Platform.MACOS),
        "vidify.api.spotify.swspotify",
        "SwSpotifyAPI",
        "Waiting for a Spotify song to play...",
        None,
        500)
    SPOTIFY_WEB = (
        "Spotify Web",
        "The official Spotify <b>Web</b> API. Read the installation guide for"
        " more details on how to set it up.",
        Res.spotify_web_icon,
        tuple(Platform),  # Supports all platforms
        "vidify.api.spotify.web",
        "SpotifyWebAPI",
        "Waiting for a Spotify song to play...",
        "init_spotify_web_api",
        1000)


class ConnectionNotReady(Exception):
    """
    This exception is raised when no Spotify session is open or when
    no songs are currently playing, since it is better to catch them
    outside of the init function.
    """

    def __init__(self, msg: str = "Spotify is closed or there isn't a"
                 "  currently playing track."):
        super().__init__(msg)


def get_api_data(key: Optional[str]) -> APIData:
    """
    Returns an entry from the APIs from `key`. KeyError is raised if it
    isn't found.
    """

    if key is None:
        logging.info("Rejecting API initialization because it was None")
        raise KeyError

    try:
        return APIData[key.upper()]
    except KeyError:
        logging.info("Rejecting API initialization because it wasn't found"
                     " in the APIs enumeration.")
        raise


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
