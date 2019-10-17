import types
import logging
from typing import Union, Callable

from spotivids.gui.drawer import Drawer, DrawerButton

from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout,
                               QLabel, QPushButton, QSizePolicy)
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import QTimer, QSize, QPropertyAnimation, QPoint, QRect


class MainWindow(QWidget):
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 fullscreen: bool = False) -> None:
        """
        Main window with whatever player is being used and the side drawer.
        """

        super().__init__()

        # Setting the window properties and size
        self.setWindowTitle('spotivids')
        #  self.setAttribute(Qt.WA_PaintOnScreen)  # No flicker on resize
        if fullscreen:
            self.showFullScreen()

        # First a layout for the player
        layout = QHBoxLayout(self)
        # For some reason this doesn't work with 0
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)

        #  The player and drawer are fit inside the main layout
        self.player = player
        #  self.player.setStyleSheet(f'background-color: {colors.dark}')
        layout.addWidget(self.player)

        self.button = DrawerButton(self)
        self.button.clicked.connect(self.show_drawer)

        self.drawer = Drawer(self)
        #  self.drawer.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.drawer.setMinimumWidth(300)

    def hide_drawer(self):
        """
        Starts the drawer's sliding out animation and changes the next one
        to sliding in.
        """

        logging.info("Opening the drawer")
        self.drawer.slideout.start()
        self.button.show()
        self.button.clicked.disconnect()
        self.button.clicked.connect(self.show_drawer)

    def show_drawer(self):
        """
        Starts the drawer's sliding in animation and changes the next one
        to sliding out.
        """

        logging.info("Hiding the drawer")
        self.drawer.slidein.start()
        self.button.hide()
        self.button.clicked.disconnect()
        self.button.clicked.connect(self.hide_drawer)

    def start_event_loop(self, event_loop: Callable, ms: int) -> None:
        """
        Starts a "manual" event loop with a timer every `ms` milliseconds.
        """

        timer = QTimer(self)

        # Qt doesn't accept a method as the parameter so it's converted
        # to a function.
        if isinstance(event_loop, types.MethodType):
            fn = lambda: event_loop()
            timer.timeout.connect(fn)
        else:
            timer.timeout.connect(event_loop)
        timer.start(ms)
