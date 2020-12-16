"""
The WEB player plays the Youtube video in a tab in your web browser.

For more information about the player modules, please check out
vidify.player.generic. It contains the abstract base class of which any
player implementation inherits, and an explanation in detail of the methods.
"""

from webbrowser import open
from threading import Timer, Thread

try:
    import flask
except OSError:
    raise ImportError("Flask is not installed")

from vidify.player.generic import PlayerBase
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QLabel
from vidify.gui import Fonts


class WebPlayer(PlayerBase):
    PORT = 9999
    ROOT_URL = 'http://localhost:{}/video'.format(PORT)
    DEFAULT_VIDEO_ID = "GfKs8oNP9m8"
    DIRECT_URL = False
    _LABEL_PREFIXES = {
        'url': '<b>Current URL:</b> ',
        'is_playing': '<b>Is it playing?:</b> ',

    }

    def __init__(self) -> None:
        super().__init__()
        self.current_media = None
        self.is_playing = True
        self.flask_app = flask.Flask(
            "flask_web_server",
            template_folder="vidify/player/web/templates",
            static_folder="vidify/player/web/static"
        )
        self._add_endpoints()
        app_thread = Thread(target=self._run_flask_web_server)
        app_thread.daemon = True
        Timer(0, open, args=[self.ROOT_URL]).start()
        app_thread.start()
        self._init_gui()

    def _init_gui(self) -> None:
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.title = QLabel("Web player")
        self.title.setStyleSheet("padding: 30px; color: white")
        self.title.setFont(Fonts.title)
        self.sub_title = QLabel("The video is now playing in your browser.")
        self.sub_title.setStyleSheet("padding: 30px; color: white")
        self.sub_title.setFont(Fonts.bigtext)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.sub_title)
        self.log_layout = QVBoxLayout()
        self.layout.addLayout(self.log_layout)
        # There's a label for each attribute, so they are initialized
        # programatically, and will be updated later.
        self.labels = {}
        for key, prefix in self._LABEL_PREFIXES.items():
            self.labels[key] = QLabel(prefix + '-')
            self.labels[key].setStyleSheet("padding: 20px; color: white")
            self.labels[key].setWordWrap(True)
            font = Fonts.bigtext
            font.setBold(False)
            self.labels[key].setFont(font)
            self.labels[key].setAlignment(Qt.AlignHCenter)
            self.log_layout.addWidget(self.labels[key])

    def _run_flask_web_server(self):
        self.flask_app.run(debug=False, port=self.PORT)

    def _video_endpoint(self):
        return flask.render_template('index.html')

    def _get_video_id_for_current_song_endpoint(self):
        youtubeId = self.DEFAULT_VIDEO_ID

        if (self.current_media is not None and
                not ("default_video" in self.current_media)):
            youtubeId = self.current_media.replace(
                "https://www.youtube.com/watch?v=",
                ""
            )

        data = {
            "youtubeId": youtubeId,
            "isPlaying": self.is_playing
        }

        return data

    def _add_endpoints(self):
        self.flask_app.add_url_rule("/video", "video", self._video_endpoint)
        self.flask_app.add_url_rule(
            "/api/",
            "getVideoIdForCurrentSong",
            self._get_video_id_for_current_song_endpoint
        )

    @property
    def pause(self) -> bool:
        """
        Currently not supported.
        """

    @pause.setter
    def pause(self, do_pause: bool) -> None:
        if do_pause and self.is_playing:
            self.is_playing = False
        elif not do_pause and not self.is_playing:
            self.is_playing = True

        self.labels['is_playing'].setText(
            f"{self._LABEL_PREFIXES['is_playing']}{self.is_playing}"
        )

    @property
    def position(self) -> int:
        """
        Currently not supported.
        """

    def seek(self, ms: int, relative: bool = False) -> None:
        """
        Currently not supported.
        """

    def start_video(self, media: str, is_playing: bool = True) -> None:
        if "default_video" in media:
            self.current_media = self.DEFAULT_VIDEO_ID
        else:
            self.current_media = media

        self.labels['url'].setText(
            f"{self._LABEL_PREFIXES['url']}{self.current_media}"
        )
        self.labels['is_playing'].setText(
            f"{self._LABEL_PREFIXES['is_playing']}{is_playing}"
        )
