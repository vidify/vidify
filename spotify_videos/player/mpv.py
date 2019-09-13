import logging

import mpv


# TODO: Review inheritance with MpvPlayer(MPV)


class MpvPlayer(object):
    def __init__(self, logger: logging.Logger,
                 fullscreen: bool = False) -> None:
        """
        This MPV player is the instance where media should play optionally,
        since the default is VLC.

        The logger is an instance from the logging module, configured
        to show debug or error messages.
        """

        self._logger = logger
        self._fullscreen = fullscreen

        self._instance = mpv.MPV(log_handler=print, loglevel="info")

    def __del__(self):
        try:
            self._instance.terminate()
        except AttributeError:
            pass

    def play(self):
        self._instance.pause = False

    def pause(self):
        self._instance.pause = True

    def toggle_pause(self):
        if self._instance.pause:
            self.play()
        else:
            self.pause()

    @property
    def position(self):
        """
        Getting the position of the VLC player in milliseconds
        """

        print(self._instance.playback_time)  # TODO

    @position.setter
    def position(self, ms: int):
        """
        Setting the position in milliseconds
        """

        self._instance.seek(ms / 1000, reference='absolute')

    def start_video(self, url: str) -> None:
        """
        Starts a new video in the mpv player. It should start paused in case
        the song isn't playing at the moment.
        """

        self._instance.play(url)
        self._instance.fullscreen = self._fullscreen
        self.pause()
