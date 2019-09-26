import sys
import logging

import vlc
from PySide2.QtWidgets import QFrame


class VLCPlayer(QFrame):
    def __init__(self, vlc_args: str = "", fullscreen: bool = False) -> None:
        """
        This VLC player is the instance where media should play.
        """

        super().__init__()
        self._logger = logging.getLogger('spotivids')
        self._fullscreen = fullscreen

        # VLC initialization
        if vlc_args is None:
            vlc_args = ""
        if self._logger.level <= logging.INFO:
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

    def play(self) -> None:
        self._logger.info("Playing video")
        self._player.play()

    def pause(self) -> None:
        self._logger.info("Pausing video")
        self._player.pause()

    def toggle_pause(self) -> None:
        if self._player.is_playing():
            self.pause()
        else:
            self.play()

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

        self._logger.info(f"Time set to {ms} milliseconds")
        self._player.set_time(ms)

    def start_video(self, url: str, is_playing: bool = True) -> None:
        """
        Starts a new video in the VLC player. It can be directly played
        with `is_playing` to avoid extra calls.

        The fullscreen can't be set as an initial parameter so it's indicated
        when the video starts.
        """

        self._logger.info(f"Starting new video at {self.winId()}")
        if sys.platform.startswith('linux'):
            self._player.set_xwindow(self.winId())
        elif sys.platform == "win32":
            self._player.set_hwnd(self.winId())
        elif sys.platform == "darwin":
            self._player.set_nsobject(int(self.winId()))

        self.media = self._vlc.media_new(url)
        self.media.get_mrl()
        self._player.set_media(self.media)
        self._player.set_fullscreen(self._fullscreen)
        if is_playing:
            self.play()
