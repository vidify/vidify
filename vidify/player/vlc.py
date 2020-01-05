"""
VLC is the most popular cross-platform video player. It contains all the
codecs needed to easily play videos and can play a video from an URL,
in comparison to the Qt player.

For more information about the player modules, please check out
vidify.player.generic, which contains the abstract base class of which any
player implementation inherits, and an explanation in detail of the methods.
"""

import logging
from typing import Optional

import vlc

from vidify import Platform, CURRENT_PLATFORM
from vidify.player.generic import PlayerBase


class VLCPlayer(PlayerBase):
    def __init__(self, vlc_args: Optional[str] = None) -> None:
        super().__init__()

        if vlc_args is None:
            vlc_args = ""
        if logging.root.level <= logging.INFO:
            vlc_args += " --verbose 1"
        else:
            vlc_args += " --quiet"
        # The audio is always muted, which is needed because not all the
        # youtube-dl videos are silent.
        # Needed for the audiosync feature: set the Group of Pictures size to
        # one, so that seeking is more precise.
        vlc_args += " --no-audio --sout-x264-min-keyint 1"

        try:
            self._vlc = vlc.Instance(vlc_args)
        except NameError:
            raise ImportError("VLC is not installed") from None

        if self._vlc is None:
            raise AttributeError(
                "VLC couldn't load. This may have been caused by an incorrect"
                " installation or because an nonexistent parameter was passed"
                " with --vlc-args") from None

        self._player = self._vlc.media_player_new()

    @property
    def pause(self) -> bool:
        return not self._player.is_playing()

    @pause.setter
    def pause(self, do_pause: bool) -> None:
        # Saved in variable to not call self._player.is_playing() twice
        is_paused = self.pause
        logging.info("Playing/Pausing video")
        if do_pause and not is_paused:
            self._player.pause()
        elif not do_pause and is_paused:
            self._player.play()

    @property
    def position(self) -> int:
        return self._player.get_time()

    @position.setter
    def position(self, ms: int) -> None:
        logging.info("Position set to %d milliseconds", ms)
        self._player.set_time(ms)

    def start_video(self, media: str, is_playing: bool = True) -> None:
        logging.info("Starting new video")
        if CURRENT_PLATFORM in (Platform.LINUX, Platform.BSD):
            self._player.set_xwindow(self.winId())
        elif CURRENT_PLATFORM == Platform.WINDOWS:
            self._player.set_hwnd(self.winId())
        elif CURRENT_PLATFORM == Platform.MACOS:
            self._player.set_nsobject(int(self.winId()))

        self._media = self._vlc.media_new(media)
        self._media.get_mrl()
        self._player.set_media(self._media)
        # VLC starts paused
        if is_playing:
            self.pause = False
