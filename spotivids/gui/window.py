"""
This module implements the Qt interface.

A GUI is needed to have more control on the player: an initial size can be
set, the player won't close and open everytime a new song starts, and it's
useful for real-time configuration, like fullscreen.

The Web API and SwSpotify APIs need a manual event loop to check for updates,
and they have to be obtained "asynchronously" so that Qt doesn't block. This
means that this class has to handle event loops too.

The Web API needs authorization to access to its data, so this class also
contains methods to ask the user their client ID and client secret to
obtain the authorization token.
"""

import types
import logging
from typing import Union, Callable

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide2.QtGui import QFontDatabase
from PySide2.QtCore import Qt, QTimer, QCoreApplication
from spotipy import Credentials, Scope, scopes
from spotipy.util import parse_code_from_url

from spotivids.api import ConnectionNotReady
from spotivids.api.web import WebAPI, play_videos_web
from spotivids.config import Config
from spotivids.youtube import YouTube
from spotivids.gui import Fonts, Res, Colors
from spotivids.gui.components import WebBrowser, WebForm


class MainWindow(QWidget):
    def __init__(self, player: Union['VLCPlayer', 'MpvPlayer'],
                 width: int = 800, height: int = 600,
                 fullscreen: bool = False) -> None:
        """
        Main window with the GUI and whatever player is being used.
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

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Loading the used fonts (Inter)
        font_db = QFontDatabase()
        for font in Res.fonts:
            font_db.addApplicationFont(font)

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

        # Initializing values as attributes so that they can be accessed
        # from the function called with QTimer.
        self.conn_counter = 0
        self.conn_fn = connect
        self.conn_attempts = 30
        self.conn_init = init
        self.conn_init_args = init_args
        self.event_loop_fn = event_loop
        self.event_interval = event_interval

        # Creating a label with a loading message that will be shown when the
        # connection attempt is successful.
        self.loading_label = QLabel("Loading...")
        self.loading_label.setWordWrap(True)
        self.loading_label.setFont(Fonts.title)
        self.loading_label.setStyleSheet(f"color: {Colors.fg};")
        self.loading_label.setMargin(50)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)

        # Creating the label to wait for connection. It starts hidden, since
        # it's only shown if the first attempt to connect fails.
        self.conn_label = QLabel(message)
        self.conn_label.hide()
        self.conn_label.setWordWrap(True)
        self.conn_label.setFont(Fonts.header)
        self.conn_label.setStyleSheet(f"color: {Colors.fg};")
        self.conn_label.setMargin(50)
        self.conn_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.conn_label)

        # Creating the QTimer to check for connection every second.
        self.conn_timer = QTimer(self)
        self.conn_timer.timeout.connect(self._wait_for_connection)
        self.conn_timer.start(1000)

    def _wait_for_connection(self) -> None:
        """
        Function called by start() to check every second if the connection
        has been established.
        """

        # Changing the loading message for the connection one if the first
        # connection attempt was unsuccessful.
        if self.conn_counter == 1:
            self.conn_label.show()

        # The APIs should raise `ConnectionNotReady` if the first attempt
        # to get metadata from Spotify was unsuccessful.
        logging.info("Connection attempt " + str(self.conn_counter))
        try:
            self.conn_fn()
        except ConnectionNotReady:
            pass
        else:
            logging.info("Succesfully connected to Spotify")
            self.setup_UI()
            # Stopping the timer and changing the label to the loading one.
            self.conn_timer.stop()
            self.layout.removeWidget(self.conn_label)
            self.conn_label.hide()
            self.layout.removeWidget(self.loading_label)
            self.loading_label.hide()
            self.conn_init(*self.conn_init_args)
            if self.event_loop_fn is not None:
                self.start_event_loop(self.event_loop_fn, self.event_interval)

        self.conn_counter += 1

        # If the maximum amount of attempts is reached, the app is closed.
        if self.conn_counter >= self.conn_attempts:
            print("Timed out waiting for Spotify")
            self.conn_timer.stop()
            QCoreApplication.exit(1)

    def setup_UI(self) -> None:
        """
        Loads the UI components, the main one being the video player.
        This is called after the connection has been established with
        `start()`
        """

        logging.info("Setting up the UI")
        self.layout.addWidget(self.player)

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

    def get_token(self, config: Config, youtube: YouTube) -> str:
        """
        This is called when the Web API is being used to get the credentials
        used with it.

        The parameters `config` and `youtube` are needed to initialize the
        web API when it's ready. Also, the GUI won't ask for the redirect URI.

        It's divided in 3 main steps:
            1. The user inputs the credentials.
            * (on_submit_creds is called)
            2. The user logs in.
            * (on_user_login is called)
            3. If the credentials were correct, the Web API is set up and
               started. Otherwise, go back to step 1.
            * (start_web_api is called)
        """

        # Data needed to setup the web API at the end
        self._config = config
        self._youtube = youtube

        # The web form for the user to input the credentials.
        self.web_form = WebForm(self._config.client_id,
                                self._config.client_secret)
        # on_submit_creds will be called once the credentials have been input.
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
        # Any change in the browser URL will redirect to on_user_login to
        # check if the login was succesful.
        self.browser.web_view.urlChanged.connect(self.on_user_login)
        self.layout.addWidget(self.browser)

    def on_submit_creds(self) -> None:
        """
        Checking if the submitted credentials were correct, and starting the
        logging-in step.
        """

        # Obtaining the input data
        client_id = self.web_form.client_id
        client_secret = self.web_form.client_secret
        logging.info(f"Input creds: '{client_id}' & '{client_secret}'")

        # Checking that the data isn't empty
        empty_field = False
        if client_id == '':
            self.web_form.input_client_id.highlight()
            empty_field = True
        else:
            self.web_form.input_client_id.undo_highlight()

        if client_secret == '':
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
        self.creds = Credentials(client_id, client_secret,
                                 self._config.redirect_uri)
        self.scope = Scope(scopes.user_read_currently_playing)
        url = self.creds.user_authorisation_url(self.scope)
        self.browser.url = url

    def on_user_login(self) -> None:
        """
        This function is called once the user has logged into Spotify to
        obtain the access token.

        Part of this function is a reimplementation of
        `spotipy.prompt_user_token`. It does the same thing but in a more
        automatized way, because Qt has access over the web browser too.
        """

        url = self.browser.url
        logging.info(f"Now at: {url}")

        # If the URL isn't the Spotify response URI (localhost), do nothing
        if url.find(self._config.redirect_uri) == -1:
            return

        # Trying to get the auth token from the URL with Spotipy's
        # parse_code_from_url(), which throws a KeyError if the URL doesn't
        # contain an auth token or if it contains more than one.
        try:
            code = parse_code_from_url(url)
        except KeyError as e:
            logging.info("ERROR:" + str(e))
        else:
            # Now the user token has to be requested to Spotify
            self.token = self.creds.request_user_token(code, self.scope)
            # Removing the GUI elements used to obtain the credentials
            self.layout.removeWidget(self.web_form)
            self.layout.removeWidget(self.browser)
            self.browser.hide()
            self.start_web_api()

    def start_web_api(self) -> None:
        """
        Initializes the Web API, similarly to what is done in __main__ but
        with the obtained credentials and auth token with the GUI.
        """

        logging.info(f"Initializing the Web API")

        # Initializing the web API
        spotify = WebAPI(self.player, self._youtube, self.token,
                         self._config.lyrics)
        msg = "Waiting for a Spotify song to play..."
        self.start(spotify.connect, play_videos_web, spotify, self._config,
                   message=msg, event_loop=spotify.event_loop,
                   event_interval=1000)

        # The obtained credentials are saved for the future
        self._config.client_secret = self.web_form.client_secret
        self._config.client_id = self.web_form.client_id
