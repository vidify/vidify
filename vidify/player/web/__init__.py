"""
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

PORT = 9999
ROOT_URL = 'http://localhost:{}/video'.format(PORT)
DEFAULT_VIDEO_ID = "GfKs8oNP9m8"


class WebPlayer(PlayerBase):
    DIRECT_URL = False
    flask_app = None
    current_media = None
    is_playing = True
    _LABEL_PREFIXES = {
        'url': '<b>Current URL:</b> ',
        'is_playing': '<b>Is it playing?:</b> ',

    }

    def __init__(self) -> None:
        super().__init__()
        self.flask_app = flask.Flask(
            "flask_web_server",
            template_folder="vidify/player/web/templates",
            static_folder="vidify/player/web/static"
        )
        self._add_endpoints()
        app_thread = Thread(target=self._runFlaskWebServer)
        app_thread.daemon = True
        Timer(0, open, args=[ROOT_URL]).start()
        app_thread.start()
        self._initGUI()

    def _initGUI(self) -> None:
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

    def _runFlaskWebServer(self):
        self.flask_app.run(debug=False, port=PORT)

    def _videoEndpoint(self):
        return flask.render_template('index.html')

    def _getVideoIdForCurrentSongEndpoint(self):
        youtubeId = DEFAULT_VIDEO_ID

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
        self.flask_app.add_url_rule("/video", "video", self._videoEndpoint)
        self.flask_app.add_url_rule(
            "/api/",
            "getVideoIdForCurrentSong",
            self._getVideoIdForCurrentSongEndpoint
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
            self.current_media = DEFAULT_VIDEO_ID
        else:
            self.current_media = media

        self.labels['url'].setText(
            f"{self._LABEL_PREFIXES['url']}{self.current_media}"
        )
        self.labels['is_playing'].setText(
            f"{self._LABEL_PREFIXES['is_playing']}{is_playing}"
        )
