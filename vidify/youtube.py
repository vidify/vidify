"""
This module uses youtube-dl to obtain the actual URL of a YouTube link.
That way, the video can be played directly with a video player like VLC
or mpv.

It also works with Qt asynchronously, sending a signal once it's done
calling youtube-dl.
"""

import logging
from typing import Optional

from youtube_dl import YoutubeDL, DownloadError
from qtpy.QtCore import QThread, Signal

from vidify import format_name


class YouTubeDLWorker(QThread):
    success = Signal(str)
    fail = Signal()

    def __init__(self, artist: str, title: str, debug: bool = False,
                 width: Optional[int] = None, height: Optional[int] = None
                 ) -> None:
        """
        YouTube class with config and function to get the direct url to
        the video.
        """

        super().__init__()

        self.query = f"ytsearch:{format_name(artist, title)} Official Video"

        self.options = {
            'format': 'bestvideo',
            'quiet': not debug
        }
        if width is not None:
            self.options['format'] += f'[width<={width}]'
        if height is not None:
            self.options['format'] += f'[height<={height}]'

    def __del__(self) -> None:
        """
        Avoids a segmentation fault when the app is closed while this thread
        is in execution. It simply waits for this to finish and closes itself
        afterwards.

        The problem is that Python doesn't guarantee that __del__ is called
        when the interpreter exits:
        https://docs.python.org/3.8/reference/datamodel.html#object.__del__
        so sometimes this message still may appear:
            QThread: Destroyed while thread is still running
            zsh: abort (core dumped)  python -m vidify --debug
        """

        try:
            self.exit()
            self.wait()
        except RuntimeError:
            pass

    def run(self) -> None:
        """
        Getting the youtube direct link with youtube-dl asynchronously.
        """

        with YoutubeDL(self.options) as ytdl:
            try:
                info = ytdl.extract_info(self.query, download=False)
            except DownloadError as e:
                logging.info("YouTube-dl wasn't able to obtain the video: %s",
                             str(e))
                self.fail.emit()
            else:
                self.success.emit(info['entries'][0]['url'])
