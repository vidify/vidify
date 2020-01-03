"""
The Audiosync module.

Wraps the vidify_audiosync module in a QThread so that it can be used from
the GUI on the background. It's optional, so this is only used when the user
passes --audiosync as a parameter, or indicates it in the config file.
"""

import time
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
    done = Signal(int)

    def __init__(self, title: str, start: Optional[float] = None) -> None:
        """
        A start timestamp can be passed to calculate the delay that passed
        until the module actually starts recording when run() is called.
        """

        super().__init__()
        self.youtube_title = title
        self.start_time = start

    def __del__(self) -> None:
        """
        This method isn't guaranteed to be called after the app is closed, but
        it will safely wait until the thread is done to finish.
        """

        self.quit()

    def run(self) -> None:
        """
        The run function simply executes the C extension and emits the signal
        with the obtained lag afterwards.
        """

        if self.start_time not in (None, 0):
            # The delay is calculated in milliseconds too.
            thread_delay = round((time.time() - self.start_time) * 1000)
        else:
            thread_delay = 0
        lag = audiosync.get_lag(self.youtube_title)
        # The delay is only added when the returned value is different than
        # zero.
        self.done.emit(lag if lag == 0 else lag + thread_delay)
        logging.info("Returned the lag with a delay of %d ms", thread_delay)
