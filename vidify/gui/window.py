"""
This module implements the Qt interface and is where every other module is
put together.

The API and player modules are mixed using Qt events:
    * Position changes -> MainWindow.change_video_position(ms)
    * Status changes -> MainWindow.change_video_status(status)
    * Song changes -> MainWindow.play_video()
These events are generated inside the APIs.
"""

import time
import types
import logging
import importlib
from typing import Callable, Optional

from qtpy.QtWidgets import QWidget, QLabel, QHBoxLayout
from qtpy.QtGui import QFontDatabase
from qtpy.QtCore import Qt, QTimer, QCoreApplication, Slot

from vidify import format_name
from vidify.api import APIData, get_api_data, ConnectionNotReady
from vidify.player import initialize_player
from vidify.config import Config
from vidify.youtube import YouTubeDLWorker
from vidify.lyrics import get_lyrics
from vidify.gui import Fonts, Res, Colors
from vidify.gui.components import APISelection


class MainWindow(QWidget):
    def __init__(self, config: Config) -> None:
        """
        Main window with the GUI and whatever player is being used.
        """

        super().__init__()
        self.setWindowTitle('vidify')

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

        # Initializing the player and saving the config object in the window.
        self.player = initialize_player(config.player, config)
        logging.info("Using %s as the player", config.player)
        self.config = config

        # The audiosync feature is optional until it's more stable.
        if self.config.audiosync:
            from vidify.audiosync import AudiosyncWorker
            self.audiosync = AudiosyncWorker()
        else:
            self.audiosync = None

        # The API initialization is more complex. For more details, please
        # check the flow diagram in vidify.api. First we have to check if
        # the API is saved in the config:
        try:
            api_data = get_api_data(config.api)
        except KeyError:
            # Otherwise, the user is prompted for an API. After choosing one,
            # it will be initialized from outside this function.
            logging.info("API not found: prompting the user")
            self.API_selection = APISelection()
            self.layout.addWidget(self.API_selection)
            self.API_selection.api_chosen.connect(self.on_api_selection)
        else:
            logging.info("Using %s as the API", config.api)
            self.initialize_api(api_data)

    def on_api_selection(self, api_str: str) -> None:
        """
        Method called when the API is selected with APISelection.
        The provided api string must be an existent entry
        inside the APIData enumeration.
        """

        # Removing the widget used to obtain the API string
        self.layout.removeWidget(self.API_selection)
        self.API_selection.setParent(None)
        self.API_selection.hide()
        del self.API_selection

        # Saving the API in the config
        self.config.api = api_str

        # Starting the API initialization
        self.initialize_api(APIData[api_str])

    def initialize_api(self, api_data: APIData, do_start: bool = True) -> None:
        """
        Initializes an API with the information from APIData.
        """

        # The API may need interaction with the user to obtain credentials
        # or similar data. This function will already take care of the
        # rest of the initialization.
        if api_data.gui_init_fn is not None:
            fn = getattr(self, api_data.gui_init_fn)
            fn()
            return
        mod = importlib.import_module(api_data.module)
        cls = getattr(mod, api_data.class_name)
        self.api = cls()

        # Some custom API initializations may not want to start the API
        # inside this function.
        if do_start:
            self.start(self.api.connect_api, message=api_data.connect_msg,
                       event_loop_interval=api_data.event_loop_interval)

    def start(self, connect: Callable[[], None], message: Optional[str] = None,
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
        self.loading_label.setMargin(50)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)

        # Creating the label to wait for connection. It starts hidden, since
        # it's only shown if the first attempt to connect fails.
        self.conn_label = QLabel(message or "Waiting for connection")
        self.conn_label.hide()
        self.conn_label.setWordWrap(True)
        self.conn_label.setFont(Fonts.header)
        self.conn_label.setMargin(50)
        self.conn_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.conn_label)

        # Creating the QTimer to check for connection every second.
        self.conn_timer = QTimer(self)
        self.conn_timer.timeout.connect(self.wait_for_connection)
        self.conn_timer.start(1000)

    def wait_for_connection(self) -> None:
        """
        Function called by start() to check every second if the connection
        has been established.
        """

        # Saving the starting timestamp for the audiosync feature
        start_time = time.time()

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

            # Stopping the timer and changing the label to the loading one.
            self.conn_timer.stop()
            self.layout.removeWidget(self.conn_label)
            del self.conn_timer
            self.layout.removeWidget(self.conn_label)
            self.conn_label.hide()
            del self.conn_label
            self.layout.removeWidget(self.loading_label)
            del self.loading_label

            # Loading the player and more
            self.setStyleSheet(f"background-color:{Colors.black};")
            self.layout.addWidget(self.player)
            self.play_video(self.api.artist, self.api.title, start_time)

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
            print("Timed out waiting for the connection")
            self.conn_timer.stop()
            QCoreApplication.exit(1)

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
            timer.timeout.connect(lambda: event_loop())
        else:
            timer.timeout.connect(event_loop)
        timer.start(ms)

    @Slot(bool)
    def change_video_status(self, is_playing: bool) -> None:
        """
        Slot used for API updates of the video status.
        """

        self.player.pause = not is_playing
        # If there is an audiosync thread running, this will pause the sound
        # recording and youtube downloading.
        try:
            self.audiosync.is_running = is_playing
        except AttributeError:
            pass

    @Slot(int)
    def change_video_position(self, ms: int) -> None:
        """
        Slot used for API updates of the video position.
        """

        if not self.config.audiosync:
            self.player.position = ms

    @Slot(str, str, float)
    def play_video(self, artist: str, title: str, start_time: float) -> None:
        """
        Slot used to play a video. This is called when the API is first
        initialized from this GUI, and afterwards from the event loop handler
        whenever a new song is detected.

        If an error was detected when downloading the video, the default one
        is shown instead.
        """

        # Checking that the artist and title are valid first of all
        if self.api.artist in (None, '') and self.api.title in (None, ''):
            logging.info("The provided artist and title are empty.")
            self.on_youtubedl_fail()
            return

        # This delay is used to know the elapsed time until the video
        # actually starts playing, used in the audiosync feature.
        self.timestamp = start_time

        # Loading the audio synchronization feature before anything else
        if self.config.audiosync:
            # First trying to stop the previous audiosync thread, as only
            # one audiosync thread can be running at once. If it wasn't
            # initialized, the worker is created.
            logging.info("Stopping the previous audiosync thread")
            try:
                self.audiosync.stop()
                self.audiosync.wait()
            except AttributeError:
                from vidify.audiosync import AudiosyncWorker
                self.audiosync = AudiosyncWorker()

            logging.info("Starting the audiosync thread")
            self.audiosync.youtube_title = f"{format_name(artist, title)}" \
                " Official Video"
            self.audiosync.success.connect(self.on_audiosync_success)
            self.audiosync.failed.connect(self.on_audiosync_fail)
            self.audiosync.start()

        # Launching the thread with YouTube-DL to obtain the video URL
        # without blocking the GUI.
        logging.info("Starting the youtube-dl thread")
        self.youtubedl = YouTubeDLWorker(
            self.api.artist, self.api.title, self.config.debug,
            self.config.width, self.config.height)
        self.youtubedl.success.connect(self.on_yt_success)
        self.youtubedl.fail.connect(self.on_youtubedl_fail)
        self.youtubedl.start()

    @Slot()
    def on_youtubedl_fail(self) -> None:
        """
        If Youtube-dl for whatever reason failed to load the video, a fallback
        error video is shown, along with a message to let the user know what
        happened.
        """

        self.player.start_video(Res.default_video, self.api.is_playing)
        print("The video wasn't found, either because of an issue with your"
              " internet connection or because the provided data was invalid."
              " For more information, enable the debug mode.")

    @Slot(str)
    def on_yt_success(self, url: str) -> None:
        """
        Obtains the video URL from the Youtube-dl thread and starts playing
        the video. Also shows the lyrics if enabled. The position of the video
        isn't set if it's using audiosync, because this is done by the
        AudiosyncWorker thread.
        """

        self.player.start_video(url, self.api.is_playing)
        if not self.config.audiosync:
            try:
                self.player.position = self.api.position
            except NotImplementedError:
                self.player.position = 0
        # Finally, the lyrics are displayed. If the video wasn't found, an
        # error message is shown.
        if self.config.lyrics:
            print(get_lyrics(self.api.artist, self.api.title))

    @Slot(int)
    def on_audiosync_success(self, lag: int) -> None:
        """
        Slot used after the audiosync function has finished. It sets the
        returned lag in milliseconds on the player.

        This assumes that the song wasn't paused until this issue is fixed:
        https://github.com/vidify/audiosync/issues/12
        """

        logging.info("Audiosync module returned %d ms", lag)

        # The current API position according to what's being recorded.
        playback_delay = round((time.time() - self.timestamp) * 1000) \
            - self.player.position
        lag += playback_delay

        # The user's custom audiosync delay. This is basically the time taken
        # until the module started recording (which may depend on the user
        # hardware and other things). Thus, it will almost always be a
        # negative value.
        lag += self.config.audiosync_calibration

        logging.info("Total delay is %d ms", lag)
        if lag == 0:
            return
        elif lag > 0:
            self.player.position += lag
        else:
            # If a negative delay is larger than the current player position,
            # the player position is set to zero after the lag has passed
            # with a timer.
            if self.player.position < -lag:
                self.sync_timer = QTimer(self)
                self.sync_timer.singleShot(
                    -lag, lambda: self.change_video_position(0))
            else:
                self.player.position += lag

    @Slot()
    def on_audiosync_fail(self) -> None:
        logging.info("Audiosync module failed to return the lag")

    def init_spotify_web_api(self) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        Note: the Tekore imports are done inside the functions so that
        Tekore isn't needed for whoever doesn't plan to use the Spotify
        Web API.
        """

        from vidify.api.spotify.web import get_token
        from vidify.gui.api.spotify_web import SpotifyWebPrompt

        token = get_token(self.config.refresh_token, self.config.client_id,
                          self.config.client_secret)

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
            # The SpotifyWebPrompt handles the interaction with the user and
            # emits a `done` signal when it's done.
            self._spotify_web_prompt = SpotifyWebPrompt(
                self.config.client_id, self.config.client_secret,
                self.config.redirect_uri)
            self._spotify_web_prompt.done.connect(self.start_spotify_web_api)
            self.layout.addWidget(self._spotify_web_prompt)

    def start_spotify_web_api(self, token: 'RefreshingToken',
                              save_config: bool = True) -> None:
        """
        SPOTIFY WEB API CUSTOM FUNCTION

        Initializes the Web API, also saving them in the config for future
        usage (if `save_config` is true).
        """
        from vidify.api.spotify.web import SpotifyWebAPI

        logging.info("Initializing the Spotify Web API")

        # Initializing the web API
        self.api = SpotifyWebAPI(token)
        api_data = APIData['SPOTIFY_WEB']
        self.start(self.api.connect_api, message=api_data.connect_msg,
                   event_loop_interval=api_data.event_loop_interval)

        # The obtained credentials are saved for the future
        if save_config:
            logging.info("Saving the Spotify Web API credentials")
            self.config.client_secret = self._spotify_web_prompt.client_secret
            self.config.client_id = self._spotify_web_prompt.client_id
            self.config.refresh_token = token.refresh_token

        # The credentials prompt widget is removed after saving the data. It
        # may not exist because start_spotify_web_api was called directly,
        # so errors are taken into account.
        try:
            self.layout.removeWidget(self._spotify_web_prompt)
            self._spotify_web_prompt.hide()
            del self._spotify_web_prompt
        except AttributeError:
            pass
