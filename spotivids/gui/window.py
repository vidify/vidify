import types
from typing import Union, Callable

from PySide2.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel)
from PySide2.QtGui import QFont, QPixmap
from PySide2.QtCore import Qt, QTimer


class colors:
    """
    Contains the theme colors in hexadecimal. This will be useful in the
    future when dark mode is implemented.
    """

    bg = 'white'
    fg = '#282828'


class icons:
    """
    Contains the paths to the icons and images used. This will be useful in
    the future when dark mode is implemented.
    """

    github = 'spotivids/gui/res/github.svg'


class fonts:
    """
    Contains the fonts for the different types of text.
    """

    title = QFont("Inter", 32, QFont.Bold)
    link = QFont("Inter", 20, QFont.Cursive)
    text = QFont("Inter", 12, QFont.Normal)


class MainWindow(QWidget):
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 width: int = 800, height: int = 600,
                 fullscreen: bool = False) -> None:
        """
        Main window with whatever player is being used and the side drawer.
        """

        super().__init__()

        # Setting the window properties and size
        self.setWindowTitle('spotivids')
        self.setStyleSheet(f'background-color: {colors.bg}')
        if fullscreen:
            self.showFullScreen()
        if width is None:
            width = 800
        if height is None:
            height = 600
        self.resize(width, height)

        # First a horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # The player and drawer are fit inside the main layout
        self.drawer = Drawer()
        layout.addLayout(self.drawer, 30)
        self.player = player
        layout.addWidget(self.player, 70)
        self.setLayout(layout)

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


class Drawer(QVBoxLayout):
    def __init__(self):
        """
        Side menu to the left of the app.
        """

        super().__init__()

        # Main properties
        self.setAlignment(Qt.AlignTop)

        # Setting up the elements
        self.setup_title()
        self.setup_github()

    def setup_title(self):
        label = QLabel("Spotivids")
        label.setFont(fonts.title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"color: {colors.fg};"
                            "padding: 10px")
        self.addWidget(label)

    def setup_github(self):
        github = QHBoxLayout()
        github.setAlignment(Qt.AlignCenter)
        img = QLabel()
        img.setPixmap(QPixmap(icons.github))
        img.setStyleSheet("padding: 7px")
        github.addWidget(img)

        label = QLabel("GitHub")
        label.setFont(fonts.link)
        label.setStyleSheet(f"color: {colors.fg}")
        github.addWidget(label)
        self.addLayout(github)
