"""
"""

import logging
from typing import Optional
from threading import Thread
from webbrowser import open
from threading import Timer, Thread

try:
    import flask
except OSError:
    raise ImportError("Flask is not installed")

from vidify import Platform, CURRENT_PLATFORM
from PyQt5.QtCore import QObject
from vidify.player.generic import PlayerBase
import sys
import os

PORT = 9999
ROOT_URL = 'http://localhost:{}/video'.format(PORT)
DEFAULT_VIDEO_ID = "GfKs8oNP9m8"
class WebPlayer(PlayerBase, QObject):
    DIRECT_URL = False
    flask_app = None
    current_media = None
    is_playing = True
    def __init__(self) -> None:
        super().__init__()
        self.flask_app = flask.Flask("flask_web_server", template_folder="vidify/player/templates", static_folder="vidify/player/static")
        self._add_endpoints()
        app_thread = Thread(target=self._runFlaskWebServer)
        app_thread.daemon = True
        Timer(3, open, args=[ROOT_URL]).start()
        app_thread.start()
        
    def _runFlaskWebServer(self):
        self.flask_app.run(debug=False, port=PORT)

    def _videoEndpoint(self):
        return flask.render_template('index.html')

    def _getVideoIdForCurrentSongEndpoint(self):
        youtubeId = DEFAULT_VIDEO_ID

        if self.current_media != None and not ("default_video" in self.current_media):
            youtubeId = self.current_media.replace("https://www.youtube.com/watch?v=", "")

        data = {
            "youtubeId": youtubeId,
            "isPlaying": self.is_playing
        }

        return data

    def _add_endpoints(self):
        self.flask_app.add_url_rule("/video", "video", self._videoEndpoint)
        self.flask_app.add_url_rule("/api/", "getVideoIdForCurrentSong", self._getVideoIdForCurrentSongEndpoint)

    def pause(self, do_pause: bool) -> None:
        if do_pause and self.is_playing:
            self.is_playing = False
        elif not do_pause and not self.is_playing:
            self.is_playing = True

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
        self.current_media = media