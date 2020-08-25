"""
TODO: this wrapper may be unnecessary. A better idea would be to have a QFrame
in the GUI be the player window, whose WID is passed to the player instance
from Rust. They are kept as two separate things, one for GUI-related things,
and the other to interact with the player itself.

In that case, the locale will have to be set always when the program begins,
instead of only when the Mpv player is used.
"""

import locale

from vidify.config import Config
from vidify.player.mpv import Mpv
from vidify.player.generic import PlayerBase


class MpvPlayer(PlayerBase):
    def __init__(self, config: Config) -> None:
        # Importing locale is necessary since qtpy stomps over the locale
        # settings needed by libmpv. This needs to happen after importing
        # PyQT before creating the first mpv.MPV instance, so it's in global
        # context.
        locale.setlocale(locale.LC_NUMERIC, 'C')

        super().__init__()
        self._mpv = Mpv.new(config, self.winId())

    @property
    def pause(self) -> bool:
        return self._mpv.is_paused()

    @pause.setter
    def pause(self, do_pause: bool) -> None:
        self._mpv.pause(do_pause)

    @property
    def position(self) -> int:
        return self._mpv.position()

    def seek(self, ms: int, relative: bool = False) -> None:
        self._mpv.seek(ms, relative)

    def start_video(self, media: str, is_playing: bool = True) -> None:
        self._mpv.start_video(media, is_playing)
