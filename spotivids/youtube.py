"""
This module uses youtube-dl to obtain the actual URL of a YouTube link.
That way, the video can be played directly with a video player like VLC
or mpv.
"""

import logging
from typing import Optional

from youtube_dl import YoutubeDL, DownloadError

from spotivids import format_name


class VideoNotFoundError(Exception):
    """
    Exception raised when the video wasn't found because of any reason.
    """

    def __init__(self, msg: str = "The requested video was not found, either"
                                  " because the provided metadata wasn't"
                                  " valid"):
        super().__init__(msg)


class YouTube:
    def __init__(self, debug: bool = False, width: Optional[int] = None,
                 height: Optional[int] = None) -> None:
        """
        YouTube class with config and function to get the direct url.
        """

        self.options = {
            'format': 'bestvideo',
            'quiet': not debug
        }
        if width is not None:
            self.options['format'] += f'[width<={width}]'
        if height is not None:
            self.options['format'] += f'[height<={height}]'

        self._youtube = YoutubeDL(self.options)

    def get_url(self, artist: str, title: str) -> str:
        """
        Getting the youtube direct link with youtube-dl.
        """

        # Checking that the artist and title are valid
        if artist in (None, '') and title in (None, ''):
            logging.info("Raising VideoNotFoundError because the provided"
                         " artist and title are empty.")
            raise VideoNotFoundError

        name = f"ytsearch:{format_name(artist, title)} Official Video"

        try:
            info = self._youtube.extract_info(name, download=False)
        except DownloadError as e:
            logging.info("Raising VideoNotFoundError because YouTube-dl"
                         " wasn't able to obtain the video: %s", str(e))
            raise VideoNotFoundError

        return info['entries'][0]['url']
