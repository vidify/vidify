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
        self.terminate()  # Maybe a better solution?

    def run(self):
        lag = audiosync.get_lag(self.youtube_title)
        self.done.emit(lag)
