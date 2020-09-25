"""
This init module lists the available players for the app and how to initialize
them.
"""

import importlib
from dataclasses import dataclass

from vidify import BaseModuleData, is_installed
from vidify.config import Config
from vidify.gui import RES
from vidify.player.generic import PlayerBase


@dataclass(frozen=True)
class PlayerData(BaseModuleData):
    pass


PLAYERS = (
    PlayerData(
        name="Mpv",
        short_name="Mpv",
        description="Play the music videos locally with the mpv player.",
        icon=RES.mpv_icon,
        compatible=True,
        installed=is_installed("python-mpv"),
        module="vidify.player.mpv",
    ),
    PlayerData(
        name="External",
        short_name="External",
        description="Play the music videos on external devices.",
        icon=RES.external_icon,
        compatible=True,
        installed=is_installed("zeroconf"),
        module="vidify.player.external",
    ),
)


def initialize_player(player: PlayerData, config: Config) -> PlayerBase:
    """
    Choosing a player from the list and initializing an abstract player
    instance with the information inside the `player` enumeration object.
    """

    # Importing the module first
    mod = importlib.import_module(player.module)
    # Obtaining the player class and creating an instance with the config
    cls = getattr(mod, player.name)
    obj = cls(config)

    return obj
