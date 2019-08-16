import argparse
from .version import __version__


class Parser:
    def __init__(self) -> None:
        """
        Initializing the parser with info about the program
        """

        self._parser = argparse.ArgumentParser(
            prog="spotify-videos",
            description="Windows and macOS users must pass --username,"
            " --client-id and --client-secret to use the web API."
            " Read more about how to obtain them in the README"
            " (https://github.com/marioortizmanero/spotify-music-videos).")
        self._add_arguments()

    def _add_arguments(self) -> None:
        """
        Adding all the arguments. The version is single sourced from the
        version.py file.
        """

        self._parser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}',
            help="show program's version number and exit")

        self._parser.add_argument(
            "--debug",
            action="store_true", dest="debug", default=False,
            help="display debug messages")

        self._parser.add_argument(
            "-n", "--no-lyrics",
            action="store_false", dest="lyrics", default=True,
            help="do not print lyrics")

        self._parser.add_argument(
            "-f", "--fullscreen",
            action="store_true", dest="fullscreen", default=False,
            help="play videos in fullscreen mode")

        self._parser.add_argument(
            "-a", "--args",
            action="store", dest="vlc_args", default="",
            help="other arguments used when opening VLC."
            " Note that some like args='--fullscreen' won't work in here")

        self._parser.add_argument(
            "--width",
            action="store", dest="max_width", default=None,
            help="set the maximum width for the played videos")

        self._parser.add_argument(
            "--height",
            action="store", dest="max_height", default=None,
            help="set the maximum height for the played videos")

        self._parser.add_argument(
            "-w", "--use-web-api",
            action="store_true", dest="use_web_api", default=False,
            help="forcefully use Spotify's web API")

        self._parser.add_argument(
            "--username",
            action="store", dest="username", default=None,
            help="your Spotify username."
            " Mandatory if the web API is being used."
            " Example: --username='yourname'")

        self._parser.add_argument(
            "--client-id",
            action="store", dest="client_id", default=None,
            help="your client ID. Mandatory if the web API is being used."
            " Check the README to see how to obtain yours."
            " Example: --client-id='5fe01282e44241328a84e7c5cc169165'")

        self._parser.add_argument(
            "--client-secret",
            action="store", dest="client_secret", default=None,
            help="your client secret ID."
            " Mandatory if the web API is being used."
            " Check the README to see how to obtain yours."
            " Example: --client-secret='2665f6d143be47c1bc9ff284e9dfb350'")

    def parse(self) -> dict:
        return self._parser.parse_args()
