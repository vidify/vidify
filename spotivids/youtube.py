import youtube_dl

from spotivids import format_name


class YouTube:
    def __init__(self, debug: bool = False, width: int = None,
                 height: int = None) -> None:
        """
        YouTube class with config and function to get the direct url.
        """

        self.options = {
            'format': 'bestvideo',
            'quiet': not debug
        }
        if width is not None:
            self.options['format'] += f"[width<={width}]"
        if height is not None:
            self.options['format'] += f"[height<={height}]"

    def get_url(self, artist: str, title: str) -> str:
        """
        Getting the youtube direct link with youtube-dl.
        """

        name = f"ytsearch:{format_name(artist, title)} Official Video"

        with youtube_dl.YoutubeDL(self.options) as ydl:
            info = ydl.extract_info(name, download=False)

        return info['entries'][0]['url']
