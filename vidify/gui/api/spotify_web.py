"""
Custom API implementation to ask the user for the Spotify Web credentials.
"""

import logging

from qtpy.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout,
                            QVBoxLayout)
from qtpy.QtCore import Qt, QSize, Signal
from tekore.scope import scopes
from tekore.auth.refreshing import RefreshingCredentials, RefreshingToken
from tekore.util import parse_code_from_url
from tekore.auth.expiring import OAuthError

from vidify.gui import Fonts, Colors
from vidify.gui.components import InputField, WebBrowser


class SpotifyWebPrompt(QWidget):
    """
    This widget handles all the interaction with the user to obtain the
    credentials for the Spotify Web API.
    """

    done = Signal(RefreshingToken)

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str,
                 *args) -> None:
        """
        Starts the API initialization flow, which is the following:
            1. The user inputs the credentials.
            ** self.on_submit_creds is called **
            2. The user logs in.
            ** self.on_login is called **
            3. If the credentials were correct, the Web API is set up and
               started from outside this widget. Otherwise, go back to step 1.
            ** self.done is emitted **
        """

        super().__init__(*args)

        logging.info("Initializing the Spotify Web API prompt interface")
        self.redirect_uri = redirect_uri

        # Creating the layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # The web form for the user to input the credentials.
        self.web_form = SpotifyWebForm(client_id=client_id,
                                       client_secret=client_secret)
        # on_submit_spotify_web creds will be called once the credentials have
        # been input.
        self.web_form.button.clicked.connect(self.on_submit_creds)
        self.layout.addWidget(self.web_form)

        # The web browser for the user to login and grant access.
        # It's hidden at the beggining and will appear once the credentials
        # are input.
        self.browser = WebBrowser()
        self.browser.hide()
        # The initial screen with the web form will be shown if the user
        # clicks on the Go Back button.
        self.browser.go_back_button.pressed.connect(
            lambda: (self.browser.hide(), self.web_form.show()))
        # Any change in the browser URL will redirect to on__login to check if
        # the login was succesful.
        self.browser.web_view.urlChanged.connect(self.on_login)
        self.layout.addWidget(self.browser)

    @property
    def client_id(self) -> str:
        return self.web_form.client_id

    @property
    def client_secret(self) -> str:
        return self.web_form.client_secret

    def on_submit_creds(self) -> None:
        """
        Checking if the submitted credentials were correct, and starting the
        logging-in step.
        """

        # Obtaining the input data
        form_client_id = self.web_form.client_id
        form_client_secret = self.web_form.client_secret
        logging.info("Input creds: '%s' & '%s'", form_client_id,
                     form_client_secret)

        # Checking that the data isn't empty
        empty_field = False
        if form_client_id == '':
            self.web_form.input_client_id.highlight()
            empty_field = True
        else:
            self.web_form.input_client_id.undo_highlight()

        if form_client_secret == '':
            self.web_form.input_client_secret.highlight()
            empty_field = True
        else:
            self.web_form.input_client_secret.undo_highlight()

        if empty_field:
            return

        # Hiding the form and showing the web browser for the next step
        self.web_form.hide()
        self.browser.show()

        # Creating the request URL to obtain the authorization token
        self.creds = RefreshingCredentials(
            form_client_id, form_client_secret, self.redirect_uri)
        self.scope = scopes.user_read_currently_playing
        url = self.creds.user_authorisation_url(self.scope)
        self.browser.url = url

    def on_login(self) -> None:
        """
        This function is called once the user has logged into Spotify to
        obtain the access token.

        Part of this function is a reimplementation of
        `tekore.prompt_user_token`. It does the same thing but in a more
        automatized way, because Qt has access over the web browser too.
        """

        url = self.browser.url
        logging.info("Now at: %s", url)

        # If the URL isn't the Spotify response URI (localhost), do nothing
        if url.find(self.redirect_uri) == -1:
            return

        # Trying to get the auth token from the URL with Tekore's
        # parse_code_from_url(), which throws a KeyError if the URL doesn't
        # contain an auth token or if it contains more than one.
        try:
            code = parse_code_from_url(url)
        except KeyError as e:
            logging.info("ERROR: %s", str(e))
            return

        # Now the user token has to be requested to Spotify, while
        # checking for errors to make sure the credentials were correct.
        # This will only happen with the client secret because it's only
        # checked when requesting the user token.
        try:
            # A RefreshingToken is used instead of a regular Token so that
            # it's automatically refreshed before it expires. self.creds is
            # of type `RefreshingCredentials`, so it returns always a
            # RefreshingToken.
            token = self.creds.request_user_token(code)
        except OAuthError as e:
            self.browser.hide()
            self.web_form.show()
            self.web_form.show_error(str(e))
            return

        # Removing the GUI elements used to obtain the credentials
        self.layout.removeWidget(self.web_form)
        self.web_form.hide()
        self.layout.removeWidget(self.browser)
        self.browser.hide()

        # Finally starting the Web API
        self.done.emit(token)


class SpotifyWebForm(QWidget):
    """
    This form is used to obtain the credentials needed for the authorization
    process in the Web API.
    """

    def __init__(self, *args, client_id: str = "", client_secret: str = ""
                 ) -> None:
        """
        Loading the main components inside the form. The initial client ID
        and client secret can be passed as a parameter to have an initial
        value for them in the input fields.
        """

        super().__init__(*args)

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

        url = 'https://github.com/vidify/vidify/wiki/Spotify-Web-API'
        text = QLabel(
            "<h2><i>Please introduce your Spotify keys</i></h2>"
            "If you don't know how to obtain them, please read this"
            f" <a href='{url}'>quick tutorial.</a>")
        text.setWordWrap(True)
        text.setOpenExternalLinks(True)
        text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        text.setFont(Fonts.text)
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
