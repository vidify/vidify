import logging

from .. import LINUX, WINDOWS, MACOS

import vlc
from PySide2.QtWidgets import QFrame


class VLCPlayer(QFrame):
    def __init__(self, vlc_args: str = "") -> None:
        """
        This VLC player is the instance where media should play.
        """

        super().__init__()

        # VLC initialization
        if vlc_args is None:
            vlc_args = ""
        if logging.root.level <= logging.INFO:
            vlc_args += " --verbose 1"
        else:
            vlc_args += " --quiet"
        vlc_args += " --no-audio"

        try:
            self._vlc = vlc.Instance(vlc_args)
        except NameError:
            raise Exception("VLC is not installed")

        if self._vlc is None:
            raise AttributeError("VLC couldn't load. This is almost always"
                                 " caused by an unexistent parameter passed"
                                 " with --vlc-args")

        self._player = self._vlc.media_player_new()

    @property
    def pause(self) -> bool:
        return not self._player.is_playing()

    @pause.setter
    def pause(self, do_pause: bool) -> None:
        """
        The video will be played if `do_pause` is true, or it will be paused
        if it's false. If it's already in the requested status, nothing
        is done.
        """

        # Saved in variable to not call self._player.is_playing() twice
        is_paused = self.pause
        logging.info("Playing/Pausing video")
        if do_pause and not is_paused:
            self._player.pause()
        elif not do_pause and is_paused:
            self._player.play()

    @property
    def position(self) -> int:
        """
        Getting the position of the VLC player in milliseconds
        """

        return self._player.get_time()

    @position.setter
    def position(self, ms: int) -> None:
        """
        Setting the position in milliseconds
        """

        logging.info(f"Time set to {ms} milliseconds")
        self._player.set_time(ms)

    def start_video(self, url: str, is_playing: bool = True) -> None:
        """
        Starts a new video in the VLC player. It can be directly played
        with `is_playing` to avoid extra calls.
        """

        logging.info(f"Starting new video")
        if LINUX:
            self._player.set_xwindow(self.winId())
        elif WINDOWS:
            self._player.set_hwnd(self.winId())
        elif MACOS:
            self._player.set_nsobject(int(self.winId()))

        self.media = self._vlc.media_new(url)
        self.media.get_mrl()
        self._player.set_media(self.media)
        # VLC starts paused
        if is_playing:
            self.pause = False
