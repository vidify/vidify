"""
This init module lists the available players for the app and how to initialize
them.
"""

import importlib
from enum import Enum
from typing import Optional

from vidify.config import Config
from vidify.player.generic import PlayerBase


class PlayerData(Enum):
    """
    The available players enumeration. It contains information about how to
    initialize them: the module, the class name and the possible parameters
    needed (flags from the config).

    Note: all player entries must have their name in uppercase.
    """

    def __new__(cls, module: str, class_name: str, flags_name: Optional[str]
                ) -> object:
        obj = object.__new__(cls)
        # The module location to import (for dependency injection).
        obj.module = module
        # The player's class name inside its module.
        obj.class_name = class_name
        # The name of the player's option in the Config module used to provide
        # flags or additional information. The flags argument is always
        # optional.
        obj.flags_name = flags_name
        return obj

    VLC = ('vidify.player.vlc', 'VLCPlayer', 'vlc_args')
    MPV = ('vidify.player.mpv', 'MpvPlayer', 'mpv_flags')
    EXTERNAL = ('vidify.player.external', 'ExternalPlayer', 'api')


def initialize_player(key: str, config: Config) -> PlayerBase:
    """
    Choosing a player from the list and initializing an abstract player
    instance with the information inside the `player` enumeration object.
    """

    # Finding the config player and initializing it.
    try:
        player = PlayerData[key.upper()]
    except KeyError:
        raise AttributeError(
            "The selected player isn't available. Please check your config or"
            " specify one by using a valid `--player` argument.") from None
    # Importing the module first
    mod = importlib.import_module(player.module)
    # Then obtaining the player class
    cls = getattr(mod, player.class_name)
    # No other arguments are needed for now, so all this does is initialize
    # the player with the config flags (if present).
    if player.flags_name is None:
        obj = cls()
    else:
        flags = getattr(config, player.flags_name)
        obj = cls(flags)

    return obj
