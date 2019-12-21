"""
This module implements the Qt interface and is where every other module is
put together.

The API and player modules are mixed using Qt events:
    * Position changes -> player.position (property)
    * Status changes -> player.is_playing (property)
    * Song changes -> MainWindow.play_video() (method)
These events are generated inside the APIs.

The Spotify Web API needs authorization to access to its data, so this class
also contains methods to ask the user their client ID and client secret to
obtain the authorization token.
"""

import types
import logging
import importlib
from typing import Callable, Optional

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide2.QtGui import QFontDatabase
from PySide2.QtCore import Qt, QTimer, QCoreApplication, Slot

from spotivids.api import APIData, get_api_data, ConnectionNotReady
from spotivids.player import initialize_player
from spotivids.config import Config
from spotivids.youtube import YouTube
from spotivids.lyrics import get_lyrics
from spotivids.gui import Fonts, Res, Colors
from spotivids.gui.components import WebBrowser, WebForm


class MainWindow(QWidget):
    def __init__(self, config: Config) -> None:
        """
        Main window with the GUI and whatever player is being used.
        """

        super().__init__()
        self.setWindowTitle('spotivids')

        # Setting the window to stay on top
        if config.stay_on_top:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Setting the fullscreen and window size
        if config.fullscreen:
            self.showFullScreen()
        else:
            self.resize(config.width or 800, config.height or 600)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Loading the used fonts (Inter)
        font_db = QFontDatabase()
        for font in Res.fonts:
            font_db.addApplicationFont(font)

        # Initializing the player and the youtube module directly.
        self.player = initialize_player(config.player, config)
        self.youtube = YouTube(config.debug, config.width, config.height)
        self.config = config

        # The API initialization is more complex. For more details, please
        # check the flow diagram in spotivids.api. First we have to check if
        # the API is saved in the config:
        try:
            self.api_data = get_api_data(config.api)
        except KeyError:
            # Otherwise, the user is prompted for an API. After choosing one,
            # it will be initialized from outside this function.
            self.prompt_api()
        else:
            # The API may need interaction with the user to obtain credentials
            # or similar data. This function will already take care of the
            # rest of the initialization.
            if self.api_data.gui_init_fn is not None:
                fn = getattr(self, self.api_data.gui_init_fn)
                fn()
            else:
                self.initialize_api()

    def prompt_api(self) -> None:
        """
        Initializing the widget to prompt the user for their API of choice.
        This will also save the selected API in the config file for future
        usage.
        """

    def initialize_api(self) -> None:
        """
        Initializes an API with the information from APIData.
        """

        mod = importlib.import_module(self.api_data.module)
        cls = getattr(mod, self.api_data.class_name)
        self.api = cls()
        self.start(self.api.connect_api, message=self.api_data.connect_msg,
                   event_loop_interval=self.api_data.event_loop_interval)

    def start(self, connect: Callable[[], None], message: Optional[str],
              event_loop_interval: int = 1000) -> None:
        """
        Waits for a Spotify session to be opened or for a song to play.
        Times out after 30 seconds to avoid infinite loops or too many
        API/process requests. A custom message will be shown meanwhile.

        If a `connect` call was succesful, the `init` function will be called
        with `init_args` as arguments. Otherwise, the program is closed.

        An event loop can also be initialized by passing `event_loop` and
        `event_interval`. If the former is None, nothing will be done.
        """

        # Initializing values as attributes so that they can be accessed
        # from the function called with QTimer.
        self.conn_counter = 0
        self.conn_fn = connect
        self.conn_attempts = 120  # 2 minutes, at 1 connection attempt/second
        self.event_loop_interval = event_loop_interval

        # Creating a label with a loading message that will be shown when the
        # connection attempt is successful.
        self.loading_label = QLabel("Loading...")
        self.loading_label.setFont(Fonts.title)
        self.loading_label.setStyleSheet(f"color: {Colors.fg};")
        self.loading_label.setMargin(50)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)

        # Creating the label to wait for connection. It starts hidden, since
        # it's only shown if the first attempt to connect fails.
        self.conn_label = QLabel(message or "Waiting for connection")
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
            self.layout.removeWidget(self.loading_label)
            self.loading_label.hide()
            self.conn_label.show()

        # The APIs should raise `ConnectionNotReady` if the first attempt
        # to get metadata from Spotify was unsuccessful.
        logging.info("Connection attempt %d", self.conn_counter + 1)
        try:
            self.conn_fn()
        except ConnectionNotReady:
            pass
        else:
            logging.info("Succesfully connected to the API")

            self.setup_UI()

            # Stopping the timer and changing the label to the loading one.
            self.conn_timer.stop()
            self.layout.removeWidget(self.conn_label)
            del self.conn_timer
            self.conn_label.hide()
            del self.conn_label
            self.layout.removeWidget(self.loading_label)
            self.loading_label.hide()
            del self.loading_label

            # Starting the first video
            self.play_video()

            # Connecting to the signals generated by the API
            self.api.new_song_signal.connect(self.play_video)
            self.api.position_signal.connect(self.change_video_position)
            self.api.status_signal.connect(self.change_video_status)

            # Starting the event loop if it was initially passed as
            # a parameter.
            if self.event_loop_interval is not None:
                self.start_event_loop(self.api.event_loop,
                                      self.event_loop_interval)

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

    def start_event_loop(self, event_loop: Callable[[], None],
                         ms: int) -> None:
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

    @Slot(bool)
    def change_video_status(self, is_playing: bool) -> None:
        self.player.pause = not is_playing

    @Slot(int)
    def change_video_position(self, ms: int) -> None:
        self.player.position = ms

    @Slot()
    def play_video(self) -> None:
        """
        Plays a video using the current API's data. This is called when the
        API is first initialized from this GUI, and afterwards from the event
        loop handler whenever a new song is detected.
        """

        logging.info("Starting new video")
        url = self.youtube.get_url(self.api.artist, self.api.title)
        self.player.start_video(url, self.api.is_playing)
        try:
            self.player.position = self.api.position
        except NotImplementedError:
            self.player.position = 0

        if self.config.lyrics:
            print(get_lyrics(self.api.artist, self.api.title))

    def init_spotify_web_api(self) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        Starts the API initialization flow, which is the following:
            0. If the credentials are already found in the config, simply
               initialize the API using them (skipping to the last step).
               Otherwise, continue the flow.
            ** self.prompt_spotify_web_token is called **
            1. The user inputs the credentials.
            ** self.on_submit_spotify_web_creds is called **
            2. The user logs in.
            ** self.on_spotify_web_login is called **
            3. If the credentials were correct, the Web API is set up and
               started. Otherwise, go back to step 1.
            ** self.start_spotify_web_api is called **

        Note: the Spotipy imports are done inside the functions so that
        Spotipy isn't needed for whoever doesn't plan to use it.
        """

        try:
            from spotivids.api.spotify.web import get_token
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "No module named 'spotipy'.\n"
                "To use the Spotify Web API, please install spotipy. Read"
                " more about this in the Installation Guide.")

        token = get_token(self.config.auth_token, self.config.refresh_token,
                          self.config.expiration, self.config.client_id,
                          self.config.client_secret, self.config.redirect_uri)

        if token is not None:
            # If the previous token was valid, the API can already start.
            logging.info("Reusing a previously generated token")
            self.start_spotify_web_api(token, save_config=False)
        else:
            # Otherwise, the credentials are obtained with the GUI. When
            # a valid auth token is ready, the GUI will initialize the API
            # automatically exactly like above. The GUI won't ask for a
            # redirect URI for now.
            logging.info("Asking the user for credentials")
            self.prompt_spotify_web_token()

    def prompt_spotify_web_token(self) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        This is called when the Web API is being used to get the credentials
        used with it.
        """

        # The web form for the user to input the credentials.
        self.web_form = WebForm(self.config.client_id,
                                self.config.client_secret)
        # on_submit_spotify_web creds will be called once the credentials have
        # been input.
        self.web_form.button.clicked.connect(
            self.on_submit_spotify_web_creds)
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
        # Any change in the browser URL will redirect to on_spotify_web_login
        # to check if the login was succesful.
        self.browser.web_view.urlChanged.connect(self.on_spotify_web_login)
        self.layout.addWidget(self.browser)

    def on_submit_spotify_web_creds(self) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        Checking if the submitted credentials were correct, and starting the
        logging-in step.
        """

        from spotipy.scope import scopes
        from spotipy.util import RefreshingCredentials

        # Obtaining the input data
        client_id = self.web_form.client_id
        client_secret = self.web_form.client_secret
        logging.info("Input creds: '%s' & '%s'", client_id, client_secret)

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
        self.creds = RefreshingCredentials(client_id, client_secret,
                                           self.config.redirect_uri)
        self.scope = scopes.user_read_currently_playing
        url = self.creds.user_authorisation_url(self.scope)
        self.browser.url = url

    def on_spotify_web_login(self) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        This function is called once the user has logged into Spotify to
        obtain the access token.

        Part of this function is a reimplementation of
        `spotipy.prompt_user_token`. It does the same thing but in a more
        automatized way, because Qt has access over the web browser too.
        """

        from spotipy.util import parse_code_from_url
        from spotipy.auth import OAuthError

        url = self.browser.url
        logging.info("Now at: %s", url)

        # If the URL isn't the Spotify response URI (localhost), do nothing
        if url.find(self.config.redirect_uri) == -1:
            return

        # Trying to get the auth token from the URL with Spotipy's
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
            token = self.creds.request_user_token(code, self.scope)
        except OAuthError as e:
            self.browser.hide()
            self.web_form.show()
            self.web_form.show_error(str(e))
            return

        # Removing the GUI elements used to obtain the credentials
        self.layout.removeWidget(self.web_form)
        self.layout.removeWidget(self.browser)
        self.browser.hide()
        # Finally starting the Web API
        self.start_spotify_web_api(token)

    def start_spotify_web_api(self, token: 'RefreshingToken',
                      save_config: bool = True) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        Initializes the Web API, similarly to what is done in
        initialize_web_api when the credentials are already available, but
        with the newly obtained ones, also saving them in the config for
        future usage (if `save_config` is true)
        """
        from spotivids.api.spotify.web import SpotifyWebAPI

        logging.info("Initializing the Spotify Web API")

        # Initializing the web API
        self.api = SpotifyWebAPI(token)
        api_data = APIData['SPOTIFY_WEB']
        self.start(self.api.connect_api, message=api_data.connect_msg,
                   event_loop_interval=api_data.event_loop_interval)

        # The obtained credentials are saved for the future
        if save_config:
            logging.info("Saving the Spotify Web API credentials")
            self.config.client_secret = self.web_form.client_secret
            self.config.client_id = self.web_form.client_id
            self.config.auth_token = token.access_token
            self.config.refresh_token = token.refresh_token
            self.config.expiration = token._token.expires_at
