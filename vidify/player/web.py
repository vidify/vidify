"""
"""

import logging
from typing import Optional
from threading import Thread

try:
    import flask
except OSError:
    raise ImportError("Flask is not installed")

from vidify import Platform, CURRENT_PLATFORM
from vidify.player.generic import PlayerBase
from PyQt5.QtCore import QObject


class WebPlayer(PlayerBase, QObject):
    app = None
    currentMedia = ""
    def __init__(self, vlc_args: Optional[str] = None) -> None:
        super().__init__()
        print(__name__)
        self.app = flask.Flask(__name__)
        self.add_endpoints()
        app_thread = Thread(target=self.runFlaskWebServer)
        app_thread.daemon = True
        app_thread.start()
        
    def runFlaskWebServer(self):
        self.app.run(debug=False)

    def hello(self):
        return flask.render_template('index.html')

    def getLatestSpotify(self):
        return self.currentMedia

    def add_endpoints(self):
        self.app.add_url_rule("/hello", "hello", self.hello)
        self.app.add_url_rule("/api/", "getLatestSpotify", self.getLatestSpotify)
    
    @property
    def pause(self) -> bool:
        logging.info("Playing/Pausing video")

    @pause.setter
    def pause(self, do_pause: bool) -> None:
        # Saved in variable to not call self._player.is_playing() twice
        # is_paused = self.pause
        logging.info("Playing/Pausing video")

    @property
    def position(self) -> int:
        logging.info("Return video play time")

    def seek(self, ms: int, relative: bool = False) -> None:
        logging.info("Go to time in video")

    def start_video(self, media: str, is_playing: bool = True) -> None:
        self.currentMedia = media
        print(self.currentMedia)
        logging.info("Start playing new video")