"""
This module contains commonly used components so that their usage and
initialization is easier. (specially the Web API authentication widgets).
"""

from PySide2.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit,
                               QVBoxLayout)
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QSize, QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView

from spotivids.gui import Fonts, Colors, Res


class InputField(QLineEdit):
    """
    The input field is a modified QEditLine with a set styyle, a clear button
    and a highlighting functionality for whenever the contents are wrong.
    """
    def __init__(self, *args):
        super().__init__(*args)

        self.setFont(Fonts.bigtext)
        self.setStyleSheet(f"color: {Colors.fg};"
                           f"background-color: {Colors.bg}")

        # A clear button
        clear = self.addAction(QIcon(Res.cross), QLineEdit.TrailingPosition)
        clear.triggered.connect(lambda: self.setText(''))

    def highlight(self):
        """
        Method used to highlight the input field when its contents were wrong,
        for instance.
        """

        self.setStyleSheet(f"background-color: {Colors.lighterror}")

    def undo_highlight(self):
        """
        Undos the red highlight applied when its contents were wrong, back to
        the default color.
        """

        self.setStyleSheet(f"background-color: {Colors.bg}")


class WebBrowser(QWidget):
    """
    This widget contains a QWebEngineView and other simple controls.
    """
    def __init__(self) -> None:
        super().__init__()
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


class WebForm(QWidget):
    """
    This form is used to obtain the credentials needed for the authorization
    process in the Web API.
    """

    def __init__(self, client_id: str = "", client_secret: str = ""):
        """
        Loading the main components inside the form. The initial client ID
        and client secret can be passed as a parameter to have an initial
        value for them in the input fields.
        """

        super().__init__()

        # Checking that the credentials aren't None and using an empty field
        # instead.
        if client_id is None:
            client_id = ""
        if client_secret is None:
            client_secret = ""

        # The main layout will now have a widget with a vertical layout inside
        # it. This way, the widget's size can be controlled.
        self.setMaximumSize(QSize(600, 250))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Setting up all the elements inside
        self.setup_text()
        self.setup_inputs(client_id, client_secret)
        self.setup_button()
        self.setup_error_msg()

    def setup_text(self) -> None:
        """
        Setting up the text layout with the header and the description.

        It can also show error messages.
        """

        url = 'https://github.com/marioortizmanero/spotivids' \
              '#obtaining-your-client-id-and-client-secret'
        text = QLabel(
            "<h2><i>Please introduce your Spotify keys</i></h2>"
            "If you don't know how to obtain them, please read this"
            f" <a href='{url}'>quick tutorial.</a>")
        text.setWordWrap(True)
        text.setOpenExternalLinks(True)
        text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        text.setFont(Fonts.text)
        text.setStyleSheet(f"color: {Colors.fg};")
        text.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(text)

    def setup_inputs(self, client_id: str, client_secret: str) -> None:
        """
        Setting up the input fields for the client ID and client secret.
        """

        self.input_client_id = InputField(client_id)
        self.input_client_id.setPlaceholderText("Client ID...")
        self.input_client_secret = InputField(client_secret)
        self.input_client_secret.setPlaceholderText("Client secret...")
        self.layout.addWidget(self.input_client_id)
        self.layout.addWidget(self.input_client_secret)

    def setup_error_msg(self) -> None:
        """
        Creates a QLabel widget under the input fields to show error messages.
        It's hidden by default.
        """

        self.error_msg = QLabel()
        self.error_msg.setWordWrap(True)
        self.error_msg.setFont(Fonts.text)
        self.error_msg.setStyleSheet(f"color: {Colors.darkerror};")
        self.error_msg.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.error_msg)

    def setup_button(self) -> None:
        """
        Setting up the submit button.
        if the input credentials are correct.
        """

        self.button = QPushButton("SUBMIT")
        self.button.setFont(Fonts.bigbutton)
        self.button.setStyleSheet(f"color: {Colors.fg};"
                                  f"background-color: {Colors.bg};")
        self.layout.addWidget(self.button)

    @property
    def client_id(self) -> str:
        """
        Returns the client ID from the input.
        """

        return self.input_client_id.text().strip()

    @property
    def client_secret(self) -> str:
        """
        Returns the client secret from the input.
        """

        return self.input_client_secret.text().strip()

    def hide_error(self) -> None:
        """
        Hides and removes the error message under the input fields.
        """

        self.error_msg.hide()
        self.error_msg.setText()

    def show_error(self, msg: str) -> None:
        """
        Displays an error mesage under the input fields.
        """

        self.error_msg.show()
        self.error_msg.setText(msg)
