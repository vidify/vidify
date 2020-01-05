"""
This module contains commonly used components so that their usage and
initialization is easier. (specially the Web API authentication widgets).
"""

import logging
from typing import Optional

from qtpy.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit,
                            QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
                            QFrame)
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtCore import (Qt, QSize, QUrl, Signal, Slot, QPropertyAnimation,
                         QPoint)
from qtpy.QtSvg import QSvgWidget
from qtpy.QtWebEngineWidgets import QWebEngineView

from vidify import CURRENT_PLATFORM
from vidify.api import APIData
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
        self.setMaximumSize(QSize(250, 350))
        self.setMinimumSize(QSize(170, 250))
        self.layout = QVBoxLayout(self)

        icon = QSvgWidget(icon or Res.default_api_icon)
        self.layout.addWidget(icon)

        text = QLabel(description)
        text.setStyleSheet("padding: 10px")
        text.setWordWrap(True)
        text.setFont(Fonts.smalltext)
        text.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(text)

        # The button will be disabled but still shown if `enabled` is false.
        # This is used when the current platform isn't in the API's supported
        # platforms.
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

        # The web view controls for now are just a button to go back.
        self.go_back_button = QPushButton("← Go back")
        self.go_back_button.setFont(Fonts.mediumbutton)
        self.layout.addWidget(self.go_back_button)

        # The web view itself, with a fixed size.
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)

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


class Drawer(QFrame):
    def __init__(self, *args, **kwargs) -> None:
        """
        A wrapper for the drawer, containing both the drawer itself and
        the button to open/close it. That way, the drawer logic can be
        isolated from the main window.
        """

        super().__init__(*args, **kwargs)

        logging.info("Setting up the drawer")
        self.setGeometry(0, 0, 300, 500)

        # The drawer
        self.drawer = DrawerBox(self)
        self.drawer.setGeometry(-300, 0, 300, 500)
        self.drawer.show()

        # The button
        self.button = DrawerButton(self)
        self.button.setGeometry(10, 10, 50, 50)
        self.button.clicked.connect(self.show_drawer)
        self.button.show()

    def hide_drawer(self) -> None:
        """
        Starts the drawer's sliding out animation and changes the next one
        to sliding in.
        """

        logging.info("Opening the drawer")
        self.drawer.slideout.start()
        self.button.show()
        self.button.clicked.disconnect()
        self.button.clicked.connect(self.show_drawer)

    def show_drawer(self) -> None:
        """
        Starts the drawer's sliding in animation and changes the next one
        to sliding out.
        """

        logging.info("Hiding the drawer")
        self.drawer.slidein.start()
        self.button.hide()
        self.button.clicked.disconnect()
        self.button.clicked.connect(self.hide_drawer)


class DrawerBox(QFrame):
    def __init__(self, *args, **kwargs) -> None:
        """
        The drawer is the sidebar to the left with quick actions and
        configuration tools.
        """

        super().__init__(*args, **kwargs)

        # Main properties
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)

        # The animations
        self.slidein = QPropertyAnimation(self, b'pos')
        self.slidein.setDuration(400)
        self.slidein.setEndValue(QPoint(0, 0))
        self.slideout = QPropertyAnimation(self, b'pos')
        self.slideout.setDuration(400)
        self.slideout.setEndValue(QPoint(-self.width(), 0))

        # The close icon
        label = QLabel(self)
        pixmap = QPixmap(Res.cross)
        label.setPixmap(pixmap)
        label.setGeometry(self.width(), 0, 50, 50)

        # The title
        self.title = QLabel("Vidify")
        self.title.setFont(Fonts.title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("padding-top: 10px;")
        self.layout.addWidget(self.title)

        # The GitHub link
        self.github = QHBoxLayout()
        self.github.setAlignment(Qt.AlignCenter)

        img = QLabel("<a href='https://github.com' style='color:inherit;"
                     " text-decoration: none;'></a>")
        img.setToolTip("Click to open the GitHub repository")
        img.setPixmap(QPixmap(Res.github))
        img.setStyleSheet("padding: 7px")
        self.github.addWidget(img)

        # URL without the hyperlink style
        label = QLabel(f"<a href='https://github.com' style='color:inherit;"
                       " text-decoration: none;'><span>GitHub</span></a>")
        label.setToolTip("Click to open the GitHub repository")
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label.setFont(Fonts.link)
        self.github.addWidget(label)
        self.layout.addLayout(self.github)


class DrawerButton(QPushButton):
    def __init__(self, *args, **kwargs) -> None:
        """
        The button that opens the drawer. It fades in when the user moves
        the cursor over the window, and fades away after 3 seconds.
        """

        super().__init__('', *args, **kwargs)

        self.setIcon(QIcon(Res.menu))
        self.setIconSize(QSize(40, 40))
        self.setFlat(True)

        #  self.fadein_btn = QPropertyAnimation(self, b'geometry')
        #  self.fadein_btn.setDuration(500)
        #  self.fadein_btn.setStartValue(QRect())
        #  self.fadein_btn.setEndValue(QSize(50, 50))
        #  self.fadein_btn.start()
