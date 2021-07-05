"""
Mpv is a good alternative to VLC because it's relatively lightweight and
straightforward, but it's mostly used only on Linux systems.

For more information about the player modules, please check out
vidify.player.generic, which contains the abstract base class of which any
player implementation inherits, and an explanation in detail of the methods.
"""

import json
import locale
import logging

from mpv import MPV

from vidify.config import Config
from vidify.player.generic import PlayerBase

# Importing locale is necessary since qtpy stomps over the locale settings
# needed by libmpv. This needs to happen after importing PyQT before creating
# the first mpv.MPV instance, so it's in global context.
locale.setlocale(locale.LC_NUMERIC, "C")


class Mpv(PlayerBase):
    # The audio is always muted, which is needed because not all the
    # youtube-dl videos are silent. The keep-open flag stops mpv from closing
    # after the video is over.
    DEFAULT_PROPERTIES = {
        "mute": True,
        "vo": "gpu,libmpv,x11",
        "config": False,
        "keep-open": "always",
    }

    def __init__(self, config: Config) -> None:
        # Importing locale is necessary since qtpy stomps over the locale
        # settings needed by libmpv. This needs to happen after importing PyQT
        # before creating the first mpv.MPV instance, so it's in global
        # context.
        locale.setlocale(locale.LC_NUMERIC, "C")

        super().__init__()

        args = self.DEFAULT_PROPERTIES
        args["wid"] = str(int(self.winId()))  # conversions: sip.voidptr -> int -> str
        if config.debug:
            args["log_handler"] = print
            args["loglevel"] = "info"
        args.update(json.loads(config.mpv_properties))

        self._mpv = MPV(**args)

    @property
    def pause(self) -> bool:
        return self._mpv.pause

    @pause.setter
    def pause(self, do_pause: bool) -> None:
        logging.info("Playing/Pausing video")
        self._mpv.pause = do_pause

    @property
    def position(self) -> int:
        time = self._mpv.playback_time
        return round(time * 1000) if time is not None else 0

    def seek(self, ms: int, relative: bool = False) -> None:
        """
        Mpv will throw an error if the position is changed before the video
        starts, so this waits for 'seekable' to be set to True.
        """

        self._mpv.wait_for_property("seekable")
        logging.info("Position set to %d milliseconds", ms)
        self._mpv.seek(
            round(ms / 1000, 2), reference="relative" if relative else "absolute"
        )

    def start_video(self, media: str, is_playing: bool = True) -> None:
        logging.info("Started new video")
        self._mpv.play(media)
        # Mpv starts automatically playing the video
        if not is_playing:
            self.pause = True
