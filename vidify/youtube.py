"""
This module uses youtube-dl to obtain the actual URL of a YouTube link.
That way, the video can be played directly with a video player like VLC
or mpv.
"""

import logging
from typing import Optional

from youtube_dl import YoutubeDL
from qtpy.QtCore import QObject, Signal


def get_direct_url(data: dict) -> str:
    """
    Returns the direct video URL from the returned data by YoutubeDL, like
    https://r1---sn-vg5obxn25po-cjod.googlevideo.com/videoplayback?...
    """

    return data['entries'][0]['url']


def get_youtube_url(data: dict) -> str:
    """
    Returns the YouTube's URL from the returned data by YoutubeDL, like
    https://www.youtube.com/watch?v=dQw4w9WgXcQ
    """

    return data['entries'][0]['webpage_url']


class YouTubeDLWorker(QObject):
    """
    YouTube class with config and function to get the direct url to the video.
    It's intended to be used with QThreads, so it contains signals to
    communicate asynchronously.

    It will send a success signal with the obtained URL, or in case of error,
    a fail signal with no data will be emitted instead. The finish signal
    will also always be emitted at the end.
    """

    success = Signal(dict)
    fail = Signal()
    finish = Signal()

    def __init__(self, query: str, debug: bool = False,
                 width: Optional[int] = None, height: Optional[int] = None
                 ) -> None:
        super().__init__()

        # The query attribute contains the full search to be done on YouTube.
        self.query = query

        self.options = {
            'format': 'bestvideo',
            'quiet': not debug
        }
        if width is not None:
            self.options['format'] += f'[width<={width}]'
        if height is not None:
            self.options['format'] += f'[height<={height}]'

    def get_url(self) -> None:
        """
        Getting the youtube direct link with youtube-dl, intended to be used
        with a QThread. It's guaranteed that either a success signal or a
        fail signal will be emitted.
        """

        with YoutubeDL(self.options) as ytdl:
            try:
                data = ytdl.extract_info(self.query, download=False)
            except Exception as e:
                # Any kind of error has to be caught, so that it doesn't only
                # send the error signal when the download wasn't successful
                # (a DownloadError from youtube_dl).
                logging.info("YouTube-dl wasn't able to obtain the video: %s",
                             str(e))
                self.fail.emit()
            else:
                if len(data['entries']) == 0:
                    logging.info("YouTube-dl returned no entries")
                    self.fail.emit()
                else:
                    self.success.emit(data)
            finally:
                self.finish.emit()
