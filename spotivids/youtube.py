import logging
import youtube_dl

from spotivids import format_name


class YouTube:
    def __init__(self, debug: bool = False,
                 quality: str = 'medium') -> None:
        """
        YouTube class with config and function to get the direct url.

        The quality of the played videos can be configured by choosing
        between low, medium (default), or high. Debug messages will also
        be shown if `debug` is True.
        """

        options = {
            'low': 'worstvideo',
            'medium': 'bestvideo[height<=720]',
            'high': 'bestvideo'
        }
        if quality not in options:
            quality = 'medium'

        self.options = {
            'format': options[quality],
            'quiet': not debug
        }

    def get_url(self, artist: str, title: str) -> str:
        """
        Getting the youtube direct link with youtube-dl.
        """

        name = f"ytsearch:{format_name(artist, title)} Official Video"

        with youtube_dl.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(name, download=False)

        return info['entries'][0]['url']
