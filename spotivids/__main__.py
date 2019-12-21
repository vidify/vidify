"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import os
import sys
import logging
from contextlib import redirect_stderr

from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

from spotivids.config import Config
from spotivids.api.generic import APIBase
from spotivids.gui import Res
from spotivids.gui.window import MainWindow


def start_gui(config: Config) -> None:
    """
    Initializing the Qt application. MainWindow takes care of initializing
    the player and the API, and acts as the "main function" where everything
    is put together.
    """

    app = QApplication()
    app.setWindowIcon(QIcon(Res.icon))
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())


def main() -> None:
    # Initialization and parsing of the config from arguments and config file
    config = Config()
    config.parse()

    # Logger initialzation with precise milliseconds handler.
    logging.basicConfig(level=logging.DEBUG if config.debug else logging.ERROR,
                        format="[%(asctime)s.%(msecs)03d] %(levelname)s:"
                        " %(message)s", datefmt="%H:%M:%S")

    # Redirects stderr to /dev/null if debug is turned off, since sometimes
    # VLC will print non-fatal errors even when configured to be quiet.
    # This could be redirected to a log file in the future, along with any
    # other output from the logging module.
    if config.debug:
        start_gui(config)
    else:
        with redirect_stderr(os.devnull):
            start_gui(config)


if __name__ == '__main__':
    main()
