"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import logging
import sys

import qdarkstyle
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication

from vidify.config import Config
from vidify.gui import RES, set_dark_mode
from vidify.gui.window import MainWindow


def start_gui(config: Config) -> None:
    """
    Initializing the Qt application. MainWindow takes care of initializing
    the player and the API, and acts as the "main function" where everything
    is put together.
    """

    app = QApplication(["vidify"])
    # Setting dark mode if enabled
    if config.dark_mode:
        logging.info("Enabling dark mode")
        app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())
        set_dark_mode()
    app.setWindowIcon(QIcon(RES.icon))
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())


def check_deprecated(config: Config) -> None:
    if config.audiosync:
        print(
            "WARNING: Audiosync is disabled until a new implementation is"
            " worked on. Stay updated with vidify.org."
        )
        config.audiosync = False


def main() -> None:
    # Initialization and parsing of the config from arguments and config file
    config = Config()
    config.parse()
    check_deprecated(config)

    # Logger initialzation with precise milliseconds handler.
    logging.basicConfig(
        level=logging.DEBUG if config.debug else logging.ERROR,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s:" " %(message)s",
        datefmt="%H:%M:%S",
    )

    start_gui(config)


if __name__ == "__main__":
    main()
