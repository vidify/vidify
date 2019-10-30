"""
This module implements the Qt interface.

A GUI is needed to have more control on the player: an initial size can be
set, the player won't close and open everytime a new song starts, and it's
useful for real-time configuration, like fullscreen.
"""

import types
import logging
from typing import Union, Callable

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide2.QtCore import Qt, QTimer, QCoreApplication
from PySide2.QtGui import QFontDatabase

from spotivids.api import ConnectionNotReady
from spotivids.gui import Fonts, Res


class MainWindow(QWidget):
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 width: int = 800, height: int = 600,
                 fullscreen: bool = False) -> None:
        """
        Main window with whatever player is being used.
        """

        super().__init__()
        self.setWindowTitle('spotivids')
        self.player = player

        if fullscreen:
            self.showFullScreen()
        else:
            if width is None:
                width = 800
            if height is None:
                height = 600
            self.resize(width, height)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Loading the used fonts (Inter)
        font_db = QFontDatabase()
        for font in Res.fonts:
            font_db.addApplicationFont(font)

    def setup_UI(self) -> None:
        """
        Loads the UI components, the main one being the video player.
        This is called after the connection has been established with
        `start()`
        """

        logging.info("Setting up the UI")
        self.setStyleSheet('background-color: {Colors.dark}')
        self.main_layout.addWidget(self.player)

    def start_event_loop(self, event_loop: Callable, ms: int) -> None:
        """
        Starts a "manual" event loop with a timer every `ms` milliseconds.
        This is used with the SwSpotify API and the Web API to check every
        `ms` seconds if a change has happened, like if the song was paused.
        """

        logging.info("Starting event loop")
        timer = QTimer(self)

        # Qt doesn't accept a method as the parameter so it's converted
        # to a function.
        if isinstance(event_loop, types.MethodType):
            fn = lambda: event_loop()
            timer.timeout.connect(fn)
        else:
            timer.timeout.connect(event_loop)
        timer.start(ms)

    def start(self, connect: Callable, init: Callable, *init_args: any,
              event_loop: Callable = None, event_interval: int = 1000,
              message: str = "Waiting for connection") -> None:

        """
        Waits for a Spotify session to be opened or for a song to play.
        Times out after 30 seconds to avoid infinite loops or too many
        API/process requests.

        If the connection was succesful, the `init` function will be called
        with `init_args` as arguments. Otherwise, the program is closed.

        An event loop can also be initialized by passing `event_loop` and
        `event_interval`. If the former is None, nothing will be done.
        """

        # Creating the label to wait for connection
        self.conn_label = QLabel(message)
        self.conn_label.setFont(Fonts.waitconn)
        self.conn_label.setStyleSheet("color: {Colors.fg}; padding: 30px;")
        self.conn_label.setMargin(50)
        self.conn_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.conn_label)

        # Initializing values as attributes so that they can be accessed
        # from the function called with QTimer
        self.conn_counter = 0
        self.conn_fn = connect
        self.conn_attempts = 30
        self.conn_init = init
        self.conn_init_args = init_args
        self.event_loop_fn = event_loop
        self.event_interval = event_interval

        # Creating the QTimer
        self.conn_timer = QTimer(self)
        self.conn_timer.timeout.connect(self._wait_for_connection)
        self.conn_timer.start(1000)

    def _wait_for_connection(self) -> None:
        """
        Function called by start() to check every second if the connection
        has been established.
        """

        # The APIs should raise `ConnectionNotReady` if the first attempt
        # to get metadata from Spotify was unsuccessful.
        logging.info("Connection attempt " + str(self.conn_counter))
        try:
            self.conn_fn()
        except ConnectionNotReady:
            pass
        else:
            logging.info("Succesfully connected to Spotify")
            self.conn_timer.stop()
            self.main_layout.removeWidget(self.conn_label)
            self.setup_UI()
            self.conn_init(*self.conn_init_args)
            if self.event_loop_fn is not None:
                self.start_event_loop(self.event_loop_fn, self.event_interval)

        self.conn_counter += 1

        # If the maximum amount of attempts is reached, the app is closed.
        if self.conn_counter >= self.conn_attempts:
            print("Timed out waiting for Spotify")
            self.conn_timer.stop()
            QCoreApplication.exit(1)
