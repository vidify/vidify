"""
This module contains commonly used components so that their usage and
initialization is easier.
"""

import time
import logging
from typing import Callable, Optional, Tuple

from qtpy.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit,
                            QVBoxLayout, QGroupBox, QRadioButton, QHBoxLayout,
                            QButtonGroup, QScrollArea)
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtCore import Qt, QUrl, Signal, Slot, QTimer
from qtpy.QtWebEngineWidgets import QWebEngineView

from vidify import BaseModuleData
from vidify.api import APIS, ConnectionNotReady
from vidify.player import PLAYERS
from vidify.gui import Fonts, Colors, Res


class ModuleCard(QGroupBox):
    """
    Widget used inside Selection to display information about an API or Player
    as a selectable card.
    """

    def __init__(self, module: BaseModuleData, selected: bool = False) -> None:
        """
        A card with the cards's basic info.
        """

        super().__init__(module.short_name)

        self.module = module
        self.setFont(Fonts.smalltext)
        self.setMinimumHeight(270)
        self.setMaximumHeight(400)
        self.setMinimumWidth(220)
        self.setMaximumWidth(300)
        self.layout = QVBoxLayout(self)
        self.setup_icon(module.icon)
        self.setup_text(module.description)
        self.setup_button(module.installed, selected)

    def setup_icon(self, icon: str) -> None:
        self.icon = QPixmap(icon)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.icon)
        self.icon_label.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.icon_label)

    def setup_text(self, description: str) -> None:
        self.text = QLabel(description)
        self.text.setStyleSheet("padding: 10px 3px")
        self.text.setWordWrap(True)
        self.text.setFont(Fonts.smalltext)
        self.text.setAlignment(Qt.AlignHCenter)
        self.text.setTextFormat(Qt.RichText)
        self.text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.text.setOpenExternalLinks(True)
        self.layout.addWidget(self.text)

    def setup_button(self, enabled: bool, selected: bool) -> None:
        """
        The button will be disabled but still shown if `enabled` is false.
        """

        self.button = QRadioButton("USE" if enabled else "Not Installed")
        self.button.setEnabled(enabled)
        self.button.setChecked(selected)
        font = Fonts.text
        font.setItalic(True)
        self.button.setFont(font)
        self.layout.addWidget(self.button)


class SetupWidget(QWidget):
    """
    Widget used to prompt the user for what API and Player to use.
    """

    # This signal returns references of the obtained API and Player,
    # respectively.
    done = Signal(object, object)

    def __init__(self, saved_api: Optional[str] = None,
                 saved_player: Optional[str] = None, *args) -> None:
        """
        The setup widget can be initialized with the previously selected API
        and Player so that all the user has to do is press "Next".
        """

        super().__init__(*args)

        self.layout = QVBoxLayout(self)

        self.api_group = self.load_data(
            APIS, "Select your music player:", saved_api)
        self.player_group = self.load_data(
            PLAYERS, "Select where to play the videos:", saved_player)
        self.init_button()

    def init_button(self) -> None:
        """
        Adds the button to continue to the next step.
        """

        self.continue_btn = QPushButton("CONTINUE")
        self.continue_btn.setFont(Fonts.mediumbutton)
        self.continue_btn.clicked.connect(self.on_click)
        self.layout.addWidget(self.continue_btn)

    def init_scroll_layout(self) -> QHBoxLayout:
        """
        The actual cards layout is inside a wrapper, inside a scroll area.
        Also adds it to the main layout.
        """

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(340)
        scroll.setMaximumHeight(500)
        wrapper = QWidget()
        layout = QHBoxLayout()
        wrapper.setLayout(layout)
        scroll.setWidget(wrapper)
        self.layout.addWidget(scroll)

        return layout

    def init_title(self, title: str) -> None:
        """
        The instruction title for the screen. Also adds the new widget to the
        main layout.
        """

        text = QLabel(title)
        font = Fonts.bigtext
        font.setBold(True)
        text.setFont(font)
        self.layout.addWidget(text)

    def load_data(self, data: Tuple[BaseModuleData], msg: str,
                  saved_item: Optional[str] = None) -> QButtonGroup:
        """
        The provided data is converted into cards in the GUI. If the
        module isn't supported on the current OS, it's not added to avoid
        confusion. If it's not installed, it's disabled but it's still
        appended to the layout.
        """

        self.init_title(msg)
        layout = self.init_scroll_layout()

        # The cards are inside a group so that their selection is exclusive.
        group = QButtonGroup()
        # The disabled APIs will always be at the end of the layout, so
        # they're saved in a list to add them later.
        disabled = []
        for module in data:
            if not module.compatible:
                continue

            selected = saved_item is not None \
                and module.id == saved_item.upper()
            card = ModuleCard(module, selected)

            if module.installed:
                layout.addWidget(card)
            else:
                disabled.append(card)
            group.addButton(card.button)
            logging.info("Created API card: %s (enabled=%s, selected=%s)",
                         module.id, module.installed, selected)

        for card in disabled:
            layout.addWidget(card)

        return group

    @Slot()
    def on_click(self) -> None:
        """
        Redirects the click on an API button to a main signal that can be
        caught from outside this widget.
        """

        checked_api = self.api_group.checkedButton()
        checked_player = self.player_group.checkedButton()

        try:
            api = checked_api.parentWidget().module
            player = checked_player.parentWidget().module
        except AttributeError:
            return

        logging.info("Selected: api=%s, player=%s", api.id, player.id)
        self.done.emit(api, player)


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
