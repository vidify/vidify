"""
This init module lists the available players for the app and how to initialize
them.
"""

from enum import Enum


class Players(Enum):
    """
    The available players enumeration.
    """

    def __new__(self, value: int, module: str, class_name: str,
                config_flags_name: str):
        obj = object.__new__(cls)
        obj._value_ = value
        # The module location to import (for dependency injection).
        obj.module = module
        # The player's class name inside its module.
        obj.class_name = class_name
        # The name of the player's option in the Config module used to provide
        # flags or additional information. The flags argument is always
        # optional.
        obj.config_flags_name = config_flags_name
        return obj

    VLC = PlayerInitData(1, 'vlc_args')
    MPV = PlayerInitData(2, 'mpv_flags')


class PlayerNotFoundError(AttributeError):
    """
    Exception raised when the player wasn't found.
    """

    def __init__(self, msg):
        super().__init__(
            "The selected player isn't available. Please check your config"
            " or specify one by using a valid `--player` argument.")
