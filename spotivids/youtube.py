import youtube_dl


class YouTube:
    def __init__(self, debug: bool = False, width: int = None, height: int = None):
        """
        YouTube class with config and function to get the direct url.
        """

        self.options = {
            'format': 'bestvideo',
            'quiet': not debug
        }
        if width is not None:
            self.options['format'] += f"[width<={config.width}]"
        if height is not None:
            self.options['format'] += f"[height<={config.height}]"

    def get_url(artist: str, title: str) -> str:
        """
        Getting the youtube direct link with youtube-dl.
        """

        name = f"ytsearch:{format_name(artist, title)} Official Video"

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(name, download=False)

        return info['entries'][0]['url']
