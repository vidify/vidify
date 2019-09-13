from os import path
import argparse
import configparser

from .version import __version__


# Default config path in the system
default_path = path.expanduser('~/.spotify_videos_config')


class ArgParser(object):
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(
            prog="spotify-videos",
            description="Windows and macOS users must pass --client-id"
            " and --client-secret to use the web API."
            " Read more about how to obtain them in the README at"
            " https://github.com/marioortizmanero/spotify-music-videos")
        self.add_arguments()
        self.data = self._parser.parse_args()

    def add_arguments(self) -> None:
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
            action="store_true", dest="debug",
            help="display debug messages")

        self._parser.add_argument(
            "--config-file",
            action="store", dest="config_path",
            help=f"the config file path. Default is {default_path}")

        self._parser.add_argument(
            "-n", "--no-lyrics",
            action="store_false", dest="lyrics",
            help="do not print lyrics")

        self._parser.add_argument(
            "-f", "--fullscreen",
            action="store_true", dest="fullscreen",
            help="play videos in fullscreen mode")

        self._parser.add_argument(
            "--vlc-args",
            action="store", dest="vlc_args",
            help="custom arguments used when opening VLC."
            " Note that some like args='--fullscreen' won't work in here")

        self._parser.add_argument(
            "--use-mpv",
            action="store_true", dest="use_mpv",
            help="use mpv as the video player")

        self._parser.add_argument(
            "--width",
            action="store", dest="max_width",
            help="set the maximum width for the played videos")

        self._parser.add_argument(
            "--height",
            action="store", dest="max_height",
            help="set the maximum height for the played videos")

        self._parser.add_argument(
            "-w", "--use-web-api",
            action="store_true", dest="use_web_api",
            help="forcefully use Spotify's web API")

        self._parser.add_argument(
            "--client-id",
            action="store", dest="client_id",
            help="your client ID. Mandatory if the web API is being used."
            " Check the README to learn how to obtain yours."
            " Example: --client-id='5fe01282e44241328a84e7c5cc169165'")

        self._parser.add_argument(
            "--client-secret",
            action="store", dest="client_secret",
            help="your client secret ID."
            " Mandatory if the web API is being used."
            " Check the README to learn how to obtain yours."
            " Example: --client-secret='2665f6d143be47c1bc9ff284e9dfb350'")

        self._parser.add_argument(
            "--redirect-uri",
            action="store", dest="redirect_uri",
            help="optional redirect uri to get the access token."
            " The default is http://localhost:8888/callback/"
            " Check the README to learn how to obtain yours."
            " Example: --client-id='5fe01282e44241328a84e7c5cc169165'")


class Config(object):
    """
    Object containing all configuration options from both the argument parser
    and the config file.
    """

    def __init__(self) -> None:
        """
        Parses the arguments and tries to open the config file.

        Also loads a list with the default values for the parameters.
        """

        self._args = ArgParser()
        self._path = self._args.data.config_path or default_path

        self._file = configparser.ConfigParser()
        self._file.read(self._path)

        self._defaults = {
            'debug': False,
            'use_mpv': False,
            'vlc_args': '',
            'fullscreen': False,
            'max_width': None,
            'max_height': None,

            'use_web_api': False,
            'client_id': None,
            'client_secret': None,
            'redirect_uri': 'http://localhost:8888/callback/',
            'access_key': None
        }

    def __setattr__(self, name: str, value: str):
        """
        Modify a value from the config file.
        """

        self._file['Defaults'][name] = value
        with open(self._file._path, 'w') as configfile:
            self._file.write(configfile)

    def __getattr__(self, attr):
        """
        Get the configuration from all sources in the correct order
        (arguments > config file > defaults)
        """

        try:
            a = getattr(self._args.data, attr)
            if a is not None:
                return a
        except AttributeError:
            pass

        try:
            a = self._file['Defaults'][attr]
            if a is not None:
                return a
        except AttributeError:
            return self._defaults[attr]
