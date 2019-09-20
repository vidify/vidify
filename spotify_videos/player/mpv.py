import logging

from mpv import MPV


class MpvPlayer:
    def __init__(self, logger: logging.Logger, flags: str,
                 fullscreen: bool = False) -> None:
        """
        This MPV player is the instance where media should play optionally,
        since the default is VLC. It may be initialized with extra arguments
        with the --mpv-args option. It doesn't inherit mpv.MPV directly
        because of naming issues.

        The logger is an instance from the logging module, configured
        to show debug or error messages.

        The audio is muted, which is needed because not all the youtube-dl
        videos are silent. The fullscreen is also set.
        """

        self._logger = logger

        flags = flags.split() if flags not in (None, '') else []
        flags.extend(['mute', 'keep-open'])
        if fullscreen:
            flags.append('fullscreen')

        if self._logger.level <= logging.INFO:
            self._mpv = MPV(*flags, log_handler=print, loglevel='info')
        else:
            self._mpv = MPV(*flags)

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
        """

        self._logger.info(f"Started new video")
        self._mpv.play(url)
        if not is_playing:
            self.pause()
