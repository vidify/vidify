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
from vidify.player.generic import PlayerBase
from PyQt5.QtCore import QObject
import sys
import os

PORT = 9999
ROOT_URL = 'http://localhost:{}/video'.format(PORT)
DEFAULT_VIDEO_ID = "GfKs8oNP9m8"
class WebPlayer(PlayerBase, QObject):
    DIRECT_URL = False
    app = None
    currentMedia = ""
    isPlaying = True
    def __init__(self, vlc_args: Optional[str] = None) -> None:
        super().__init__()
        print(__name__)
        self.app = flask.Flask("flask_web_server", template_folder="vidify/player/templates", static_folder="vidify/player/static")
        self.__add_endpoints()
        app_thread = Thread(target=self.__runFlaskWebServer)
        app_thread.daemon = True
        Timer(3, open, args=[ROOT_URL]).start()
        app_thread.start()
        
    def __runFlaskWebServer(self):
        self.app.run(debug=False, port=PORT)

    def __video(self):
        return flask.render_template('index.html')

    def __getVideoIdForCurrentSong(self):
        youtubeId = DEFAULT_VIDEO_ID
        isPlaying = True
        if self.currentMedia != "" and not "default_video" in self.currentMedia:
            youtubeId = self.currentMedia.replace("https://www.youtube.com/watch?v=", "")

        if not self.isPlaying:
            isPlaying = False

        data = {
            "youtubeId": youtubeId,
            "isPlaying": isPlaying
        }

        return data

    def __add_endpoints(self):
        self.app.add_url_rule("/video", "video", self.__video)
        self.app.add_url_rule("/api/", "getVideoIdForCurrentSong", self.__getVideoIdForCurrentSong)

    def pause(self, do_pause: bool) -> None:
        if do_pause and self.isPlaying:
            self.isPlaying = False
        elif not do_pause and not self.isPlaying:
            self.isPlaying = True

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
        self.currentMedia = media