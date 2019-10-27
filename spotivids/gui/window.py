"""
This module implements the Qt interface.

A GUI is needed to have more control on the player: an initial size can be
set, the player won't close and open everytime a new song starts, and it's
useful for real-time configuration, like fullscreen.
"""

import types
from typing import Union, Callable

from PySide2.QtWidgets import QWidget, QHBoxLayout
from PySide2.QtCore import QTimer


class MainWindow(QWidget):
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 width: int = 800, height: int = 600,
                 fullscreen: bool = False) -> None:
        """
        Main window with whatever player is being used.
        """

        super().__init__()
        self.setWindowTitle('spotivids')
        self.setStyleSheet('background-color: #282828')

        if fullscreen:
            self.showFullScreen()
        else:
            if width is None:
                width = 800
            if height is None:
                height = 600
            self.resize(width, height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(player)

    def start_event_loop(self, event_loop: Callable, ms: int) -> None:
        """
        Starts a "manual" event loop with a timer every `ms` milliseconds.
        This is used with the SwSpotify API and the Web API to check every
        `ms` seconds if a change has happened, like if the song was paused.
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
