"""
This init module lists the available players for the app and how to initialize
them.
"""

import importlib
from dataclasses import dataclass
from typing import Tuple

from vidify import BaseModuleData, is_installed
from vidify.config import Config
from vidify.gui import RES
from vidify.player.generic import PlayerBase


@dataclass(frozen=True)
class PlayerData(BaseModuleData):
    """
    Information structure about the different Players supported, with a
    description for the user and how to initialize it.
    """

    flags: Tuple[str]


PLAYERS = (
    PlayerData(
        name="MPV",
        short_name="Mpv",
        description="Play the music videos locally with the mpv player.",
        icon=RES.mpv_icon,
        compatible=True,
        installed=is_installed("python-mpv"),
        module="vidify.player.mpv",
        class_name="MpvPlayer",
        flags=("mpv_flags",),
    ),
    PlayerData(
        name="EXTERNAL",
        short_name="External",
        description="Play the music videos on external devices.",
        icon=RES.external_icon,
        compatible=True,
        installed=is_installed("zeroconf"),
        module="vidify.player.external",
        class_name="ExternalPlayer",
        flags=("api",),
    ),
)


def initialize_player(player: PlayerData, config: Config) -> PlayerBase:
    """
    Choosing a player from the list and initializing an abstract player
    instance with the information inside the `player` enumeration object.
    """

    # Importing the module first
    mod = importlib.import_module(player.module)
    # Then obtaining the player class
    cls = getattr(mod, player.class_name)
    # No other arguments are needed for now, so all this does is initialize
    # the player with the config flags (if present).
    params = []
    for flag in player.flags:
        params.append(getattr(config, flag))
    obj = cls(*params)

    return obj
