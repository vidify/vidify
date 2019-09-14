import logging

from mpv import MPV


class MpvPlayer(object):
    def __init__(self, logger: logging.Logger,
                 fullscreen: bool = False) -> None:
        """
        This MPV player is the instance where media should play optionally,
        since the default is VLC. It may be initialized with extra arguments
        with the --mpv-args option.

        The logger is an instance from the logging module, configured
        to show debug or error messages.

        It doesn't inherit mpv.MPV directly because of naming issues.
        """

        self._logger = logger
        self._fullscreen = fullscreen

        if self._logger.level <= logging.INFO:
            self._mpv = MPV(log_handler=print, loglevel='info')
        else:
            self._mpv = MPV()

    def __del__(self):
        try:
            self._mpv.terminate()
        except AttributeError:
            pass

    def play(self):
        self._logger.info("Playing video")
        self._mpv.pause = False

    def pause(self):
        self._logger.info("Pausing video")
        self._mpv.pause = True

    def toggle_pause(self):
        if self._mpv.pause:
            self.play()
        else:
            self.pause()

    @property
    def position(self):
        """
        Getting the position of the VLC player in milliseconds
        """

        time = self._mpv.playback_time
        return time if time is not None else 0

    @position.setter
    def position(self, ms: int):
        """
        Setting the position in milliseconds. Unlike VLC, mpv will throw an
        error if the position is changed before the video starts, so
        this waits for 'seekable' to be set to True.
        """

        self._mpv.wait_for_property('seekable')
        self._logger.info(f"Time set to {ms} milliseconds")
        self._mpv.seek(ms / 1000, reference='absolute')

    def start_video(self, url: str, is_playing: bool = True) -> None:
        """
        Starts a new video in the mpv player. It can be directly played from
        here to avoid extra calls.

        The audio is muted, which is needed because not all the youtube-dl
        videos are silent. The fullscreen is also set.
        """

        self._mpv.play(url)
        self._mpv.mute = True
        self._mpv.fullscreen = self._fullscreen
        if not is_playing:
            self.pause()
