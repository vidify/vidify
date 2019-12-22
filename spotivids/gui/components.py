"""
This module contains commonly used components so that their usage and
initialization is easier. (specially the Web API authentication widgets).
"""

import logging

from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit,
                               QVBoxLayout, QGridLayout, QGroupBox)
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QSize, QUrl, Signal, Slot
from PySide2.QtSvg import QSvgWidget
from PySide2.QtWebEngineWidgets import QWebEngineView

from spotivids import CURRENT_PLATFORM
from spotivids.api import APIData
from spotivids.gui import Fonts, Colors, Res


class APICard(QGroupBox):
    """
    Widget used inside APISelection to display information about the API as
    a button.
    """

    def __init__(self, api_name: str, title: str, description: str,
                 icon: str, enabled: bool = True) -> None:
        """
        A card with the API's basic info. `api_name` is the APIData's name for
        the API. `title`, `description` and `icon` are parameters inside
        APIData, and `enabled` is true if the current platform is inside the
        API's supported platforms.
        """

        super().__init__(title)

        self.api_name = api_name
        self.setFont(Fonts.smalltext)
        self.setMaximumSize(QSize(250, 350))
        self.setMinimumSize(QSize(170, 250))
        self.layout = QVBoxLayout(self)
        self.setup_icon(icon)
        self.setup_text(description)
        self.setup_button(enabled)

    def setup_icon(self, icon: str) -> None:
        icon = QSvgWidget(icon)
        self.layout.addWidget(icon)

    def setup_text(self, description: str) -> None:
        text = QLabel(description)
        text.setWordWrap(True)
        text.setFont(Fonts.smalltext)
        text.setStyleSheet(f"color: {Colors.fg};")
        text.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(text)

    def setup_button(self, enabled: bool) -> None:
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
        self.setStyleSheet(f"color: {Colors.fg};"
                           f"background-color: {Colors.bg}")

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
        Undos the red highlight applied when its contents were wrong, back to
        the default color.
        """

        self.setStyleSheet(f"background-color: {Colors.bg}")


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
        self.go_back_button.setStyleSheet(f"color: {Colors.fg};")
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
