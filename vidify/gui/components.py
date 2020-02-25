"""
This module contains commonly used components so that their usage and
initialization is easier. (specially the Web API authentication widgets).
"""

import time
import logging
from typing import Callable, Optional

from qtpy.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit,
                            QVBoxLayout, QGridLayout, QGroupBox)
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtCore import Qt, QSize, QUrl, Signal, Slot, QTimer
from qtpy.QtWebEngineWidgets import QWebEngineView

from vidify import CURRENT_PLATFORM
from vidify.api import APIData, ConnectionNotReady
from vidify.gui import Fonts, Colors, Res


class APICard(QGroupBox):
    """
    Widget used inside APISelection to display information about the API as
    a button.
    """

    def __init__(self, api_name: str, title: str, description: str,
                 icon: Optional[str], enabled: bool = True) -> None:
        """
        A card with the API's basic info. `api_name` is the APIData's name for
        the API. `title`, `description` and `icon` are parameters inside
        APIData, and `enabled` is true if the current platform is inside the
        API's supported platforms.
        """

        super().__init__(title)

        self.api_name = api_name
        self.setFont(Fonts.smalltext)
        self.setFixedSize(QSize(250, 350))
        self.layout = QVBoxLayout(self)
        self.setup_icon(icon)
        self.setup_text(description)
        self.setup_button(enabled)

    def setup_icon(self, icon: Optional[str]) -> None:
        self.icon = QPixmap(icon or Res.default_api_icon)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.icon.scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.icon_label)

    def setup_text(self, description: str) -> None:
        self.text = QLabel(description)
        self.text.setStyleSheet("padding: 10px")
        self.text.setWordWrap(True)
        self.text.setFont(Fonts.smalltext)
        self.text.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.text)

    def setup_button(self, enabled: bool) -> None:
        """
        The button will be disabled but still shown if `enabled` is false.
        This is used when the current platform isn't in the API's supported
        platforms.
        """

        self.button = QPushButton("USE" if enabled else "Not available")
        self.button.setEnabled(enabled)
        self.button.setFont(Fonts.text)
        self.layout.addWidget(self.button)


class APISelection(QWidget):
    """
    Widget used to prompt the user for what API to use.
    """

    api_chosen = Signal(str)

    def __init__(self, *args) -> None:
        super().__init__(*args)

        logging.info("Initializing the API selection widget")
        self.layout = QVBoxLayout(self)
        group = QGroupBox("Please choose a media player:")
        group.setFont(Fonts.bigtext)
        self.layout.addWidget(group)
        layout = QGridLayout(group)

        self.max_cols = 5
        self.cards = []
        for num, api in enumerate(APIData):
            enabled = CURRENT_PLATFORM in api.platforms
            card = APICard(api.name, api.short_name, api.description,
                           api.icon, enabled)
            card.button.clicked.connect(self.on_click)
            self.cards.append(card)
            # Inserting the cards in the widget, with a maximum of `max_cols`
            # columns and starting at the first row.
            logging.info("Adding API card: %s (enabled=%s)", api.name, enabled)
            layout.addWidget(card, (num // self.max_cols), num % self.max_cols)

    @Slot()
    def on_click(self) -> None:
        """
        Redirects the click on an API button to a main signal that can be
        caught from outside this widget.
        """

        self.api_chosen.emit(self.sender().parentWidget().api_name)


class InputField(QLineEdit):
    """
    The input field is a modified QEditLine with a set style, a clear button
    and a highlighting functionality for whenever the contents are wrong.
    """

    def __init__(self, *args) -> None:
        super().__init__(*args)

        self.setFont(Fonts.bigtext)

        # A clear button
        clear = self.addAction(QIcon(Res.cross), QLineEdit.TrailingPosition)
        clear.triggered.connect(lambda: self.setText(''))

    def highlight(self) -> None:
        """
        Method used to highlight the input field when its contents were wrong,
        for instance.
        """

        self.setStyleSheet(f"background-color: {Colors.lighterror}")

    def undo_highlight(self) -> None:
        """
        Undo the red highlight applied when its contents were wrong, back to
        the default color.
        """

        self.setStyleSheet("")


class WebBrowser(QWidget):
    """
    This widget contains a QWebEngineView and other simple controls.
    """

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.layout = QVBoxLayout(self)
        self.setup_controls()
        self.setup_web_view()

    def setup_web_view(self) -> None:
        """
        The web view itself, with a fixed size.
        """

        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

    def setup_controls(self) -> None:
        """
        The web view controls for now are just a button to go back.
        """

        self.go_back_button = QPushButton("← Go back")
        self.go_back_button.setFont(Fonts.mediumbutton)
        self.layout.addWidget(self.go_back_button)

    @property
    def url(self) -> str:
        """
        Returns the web view's browser as a string. The first url() returns
        a QUrl and the second the string with the URL.
        """

        return self.web_view.url().url()

    @url.setter
    def url(self, url: str) -> None:
        """
        Sets the web view's URL to `url`.
        """

        self.web_view.setUrl(QUrl(url))


class APIConnecter(QLabel):
    """
    Wrapper to wait for the API session to be start or for a song to play.
    Times out after MAX_ATTEMPTS attempts to avoid infinite loops or
    too many requests. A custom message will be shown meanwhile.

    The widget itself is a QLabel, because it will display its current
    status.
    """

    INTERVAL = 1000  # 1 second in ms
    MAX_ATTEMPTS = 300  # 5 minutes, at 1 connection attempt/second
    success = Signal(float)
    fail = Signal()

    def __init__(self, connect_api: Callable[[], None], wait_msg: str) -> None:
        super().__init__("Loading...")
        self.wait_msg = wait_msg
        self.connect_api = connect_api

        self.setWordWrap(True)
        self.setFont(Fonts.title)
        self.setMargin(50)
        self.setAlignment(Qt.AlignCenter)

    def start(self) -> None:
        """
        Creating the QTimer to check for connection every second, and
        starting it.
        """

        self.attempts = self.MAX_ATTEMPTS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.try_connection)
        self.timer.start(self.INTERVAL)

    @Slot()
    def try_connection(self) -> None:
        """
        Function called every second to check if the connection can be
        established, so that the program can start.
        """

        # Saving the starting timestamp for the audiosync feature
        start_time = time.time()

        # Changing the loading message for the connection one if the first
        # connection attempt was unsuccessful.
        if self.attempts == self.MAX_ATTEMPTS - 1:
            self.setText(self.wait_msg)
            self.setFont(Fonts.header)

        # The APIs will raise `ConnectionNotReady` if the connection attempt
        # was unsuccessful.
        try:
            self.connect_api()
        except ConnectionNotReady:
            self.attempts -= 1
            logging.info("Connection attempts left: %d", self.attempts)

            # If the maximum amount of attempts is reached, the app is closed.
            if self.attempts == 0:
                self.timer.stop()
                self.fail.emit()
        else:
            self.timer.stop()
            self.success.emit(start_time)
