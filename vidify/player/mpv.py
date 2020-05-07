"""
Mpv is a good alternative to VLC because it's relatively lightweight and
straightforward, but it's mostly used only on Linux systems.

For more information about the player modules, please check out
vidify.player.generic, which contains the abstract base class of which any
player implementation inherits, and an explanation in detail of the methods.
"""

import locale
import logging
from typing import Optional

try:
    from mpv import MPV
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "No module named 'mpv'.\n"
        "To use this player, please install vidify along with python-mpv."
        " Read the installation guide for more details.") from None

from vidify.player.generic import PlayerBase


# Importing locale is necessary since qtpy stomps over the locale settings
# needed by libmpv. This needs to happen after importing PyQT before creating
# the first mpv.MPV instance, so it's in global context.
locale.setlocale(locale.LC_NUMERIC, 'C')


class MpvPlayer(PlayerBase):
    # The audio is always muted, which is needed because not all the
    # youtube-dl videos are silent. The keep-open flag stops mpv from closing
    # after the video is over.
    DEFAULT_FLAGS = ['mute']
    DEFAULT_ARGS = {
        'vo': 'gpu,libmpv,x11',
        'config': False,
        'keep-open': 'always'
    }

    def __init__(self, flags: Optional[str] = None) -> None:
        super().__init__()

        # Converting the flags passed by parameter (str) to a tuple
        flags = flags.split() if flags not in (None, '') else []
        flags.extend(self.DEFAULT_FLAGS)

        args = {}
        if logging.root.level <= logging.INFO:
            args['log_handler'] = print
            args['loglevel'] = 'info'
        args['wid'] = str(int(self.winId()))  # sip.voidptr -> int -> str
        args.update(self.DEFAULT_ARGS)

        self._mpv = MPV(*flags, **args)

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

        self._mpv.wait_for_property('seekable')
        logging.info("Position set to %d milliseconds", ms)
        self._mpv.seek(round(ms / 1000, 2),
                       reference='relative' if relative else 'absolute')

    def start_video(self, media: str, is_playing: bool = True) -> None:
        logging.info("Started new video")
        self._mpv.play(media)
        # Mpv starts automatically playing the video
        if not is_playing:
            self.pause = True
