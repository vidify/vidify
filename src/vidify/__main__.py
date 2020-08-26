"""
This module chooses the player and platform and starts them. The Qt GUI is
also initialized here.
"""

import sys
import logging

from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QIcon
import qdarkstyle

from vidify.config import Config, init_config, init_logging
from vidify.gui import set_dark_mode, Res
from vidify.gui.window import MainWindow


def start_gui(config: Config) -> None:
    """
    Initializing the Qt application. MainWindow takes care of initializing
    the player and the API, and acts as the "main function" where everything
    is put together.
    """

    app = QApplication(['vidify'])
    # Setting dark mode if enabled
    if config.dark_mode:
        logging.info("Enabling dark mode")
        app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())
        set_dark_mode()
    app.setWindowIcon(QIcon(Res.icon))
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())


def main() -> None:
    config = init_config(sys.argv)
    init_logging(config)
    start_gui(config)


if __name__ == '__main__':
    main()
