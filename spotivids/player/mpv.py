import logging

from mpv import MPV
from PySide2.QtWidgets import QFrame


class MpvPlayer(QFrame):
    def __init__(self, flags: str = None) -> None:
        """
        This MPV player is the instance where media should play optionally,
        since the default is VLC. It may be initialized with extra arguments
        with the --mpv-args option. It doesn't inherit mpv.MPV directly
        because of naming issues.

        The audio is muted, which is needed because not all the youtube-dl
        videos are silent.
        """

        super().__init__()
        self._logger = logging.getLogger('spotivids')

        # mpv initialization
        flags = flags.split() if flags not in (None, '') else []
        flags.extend(['mute', 'keep-open'])
        args = {}
        if self._logger.level <= logging.INFO:
            args['log_handler'] = print
            args['loglevel'] = 'info'
        args['wid'] = str(int(self.winId()))
        args['vo'] = 'x11'  # May not be necessary

        self._mpv = MPV(*flags, **args)

    def __del__(self) -> None:
        try:
            self._mpv.terminate()
        except AttributeError:
            pass

    def play(self) -> None:
        self._logger.info("Playing video")
        self._mpv.pause = False

    def pause(self) -> None:
        self._logger.info("Pausing video")
        self._mpv.pause = True

    def toggle_pause(self) -> None:
        if self._mpv.pause:
            self.play()
        else:
            self.pause()

    @property
    def position(self) -> int:
        """
        Getting the position of the VLC player in milliseconds
        """

        time = self._mpv.playback_time
        return time if time is not None else 0

    @position.setter
    def position(self, ms: int) -> None:
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
