"""
Mpv is a good alternative to VLC because it's relatively lightweight and
straightforward, but it's mostly used only on Linux systems.

For more information about the player modules, please check out
spotivids.player.generic, which contains the abstract base class of which any
player implementation inherits, and an explanation in detail of the methods.
"""

import logging
from typing import Optional

# Importing locale is necessary since PySide2 stomps over the locale settings
# needed by libmpv. This needs to happen after importing PyQT before creating
# the first mpv.MPV instance.
import locale  # noqa: F401
try:
    from mpv import MPV
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'mpv'.\n"
        "To use this player, please install spotivids along with python-mpv."
        " Read the installation guide for more details.") from None

from spotivids.player.generic import PlayerBase


class MpvPlayer(PlayerBase):
    def __init__(self, flags: Optional[str] = None) -> None:
        super().__init__()

        # Converting the flags passed by parameter (str) to a tuple
        flags = flags.split() if flags not in (None, '') else []
        # The audio is always muted, which is needed because not all the
        # youtube-dl videos are silent. The keep-open flag stops mpv from
        # closing after the video is over.
        flags.extend(['mute', 'keep-open'])

        args = {}
        if logging.root.level <= logging.INFO:
            args['log_handler'] = print
            args['loglevel'] = 'info'
        args['wid'] = str(int(self.winId()))

        self._mpv = MPV(*flags, **args)

    def __del__(self) -> None:
        try:
            self._mpv.terminate()
        except AttributeError:
            pass

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
        return time if time is not None else 0

    @position.setter
    def position(self, ms: int) -> None:
        """
        Mpv will throw an error if the position is changed before the video
        starts, so this waits for 'seekable' to be set to True.
        """

        self._mpv.wait_for_property('seekable')
        logging.info("Position set to %d milliseconds", ms)
        self._mpv.seek(ms / 1000, reference='absolute')

    def start_video(self, media: str, is_playing: bool = True) -> None:
        logging.info("Started new video")
        self._mpv.play(media)
        # Mpv starts automatically playing the video
        if not is_playing:
            self.pause = True
