"""
The Audiosync module.

Wraps the vidify_audiosync module in a QThread so that it can be used from
the GUI on the background. It's optional, so this is only used when the user
passes --audiosync as a parameter, or indicates it in the config file.
"""

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

    def __init__(self, title: str):
        super().__init__()
        self.youtube_title = title

    def __del__(self):
        """
        This method isn't guaranteed to be called after the app is closed, but
        it will safely wait until the thread is done to finish.
        """

        self.quit()
        self.wait()

    def run(self):
        """
        The run function simply executes the C extension as fast as possible
        and emits the signal with the obtained lag afterwards.
        """

        lag = audiosync.get_lag(self.youtube_title)
        self.done.emit(lag)
