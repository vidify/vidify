"""
Wraps the vidify_audiosync module in a QThread so that it can be used from
the GUI on the background. It's optional, so this is only used when the user
passes --audiosync as a parameter, or indicates it in the config file.

Check out the README.md and see the official repo for more information:
https://github.com/vidify/audiosync
"""

import logging
from typing import Optional

try:
    import vidify_audiosync as audiosync
except ImportError:
    raise ImportError(
        "No module named 'vidify_audiosync'.\n"
        "To use audio synchronization, please install vidify_audiosync and"
        " its dependencies. Read more about it in the installation guide.")
from qtpy.QtCore import QThread, Signal


class AudiosyncWorker(QThread):
    success = Signal(int)
    failed = Signal()

    def __init__(self, title: Optional[str] = None) -> None:
        """
        The vidify-audiosync call automatically obtains the YouTube audio
        track.
        """

        super().__init__()
        self.youtube_title = title
        self._is_running = False

    def __del__(self) -> None:
        """
        This method isn't guaranteed to be called after the app is closed, but
        it will safely wait until the thread is done to finish.
        """

        self.abort()

    def abort(self) -> None:
        """
        This function will abort the audiosync thread. If it wasn't running,
        nothing is done.
        """

        audiosync.abort()
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @is_running.setter
    def is_running(self, do_run: bool) -> None:
        """
        This function will pause or resume the ffmpeg recording and
        downloader. If start() wasn't called before this function is called,
        nothing is done.
        """

        logging.info("Setting audiosync is_running to %r", do_run)
        if do_run:
            audiosync.resume()
        else:
            audiosync.pause()
        self._is_running = do_run

    def run(self) -> None:
        """
        The run function simply executes the C extension and emits the signal
        with the obtained lag afterwards.
        """

        self._is_running = True
        lag, success = audiosync.run(self.youtube_title)
        if success:
            self.success.emit(lag)
        else:
            self.failed.emit()
        self._is_running = False
