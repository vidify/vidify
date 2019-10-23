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
