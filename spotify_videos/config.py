import os
import argparse
import configparser
from dataclasses import dataclass

from .version import __version__


# Default config path in the system
default_path = os.path.expanduser('~/.spotify_videos_config')


# TODO: Consider the 'attrs' module instead of dataclasses
@dataclass
class Option:
    section: str
    value_type: type
    default: any

    def __init__(self, section, value_type, default) -> None:
        self.section = section
        self.value_type = value_type
        self.default = default


@dataclass
class Options(object):
    def __init__(self):
        """
        Listing all options with their section, type and default value.
        """

        self.debug = Option('Defaults', bool, False)
        self.lyrics = Option('Defaults', bool, True)
        self.fullscreen = Option('Defaults', bool, False)
        self.max_width = Option('Defaults', str, None)
        self.max_height = Option('Defaults', str, None)
        self.use_mpv = Option('Defaults', bool, False)
        self.vlc_args = Option('Defaults', str, None)
        self.mpv_flags = Option('Defaults', str, None)

        self.use_web_api = Option('WebAPI', bool, False)
        self.client_id = Option('WebAPI', str, None)
        self.client_secret = Option('WebAPI', str, None)
        self.redirect_uri = Option('WebAPI', str,
                                   'http://localhost:8888/callback/')
        self.auth_token = Option('WebAPI', str, None)
        self.expiration = Option('WebAPI', int, None)


class Config:
    """
    Object containing all configuration options from both the argument parser
    and the config file.
    """

    def __init__(self) -> None:
        """
        Parses the arguments and tries to open the config file.

        Also loads a list with the default values for the parameters.
        """

        self._options = Options()

        self._argparser = argparse.ArgumentParser(
            prog="spotify-videos",
            description="Windows and macOS users must pass --client-id"
            " and --client-secret to use the web API."
            " Read more about how to obtain them in the README at"
            " https://github.com/marioortizmanero/spotify-music-videos")
        self.add_arguments()

        self._file = configparser.ConfigParser()

    def add_arguments(self) -> None:
        """
        Adding all the arguments. The version is single sourced from the
        version.py file.
        """

        self._argparser.add_argument(
            '-v', '--version',
            action='version',
            version=f'%(prog)s {__version__}',
            help="show program's version number and exit")

        self._argparser.add_argument(
            "--debug",
            action="store_true", dest="debug", default=None,
            help="display debug messages")

        self._argparser.add_argument(
            "--config-file",
            action="store", dest="config_path", default=None,
            help=f"the config file path. Default is {default_path}")

        self._argparser.add_argument(
            "-n", "--no-lyrics",
            action="store_false", dest="lyrics", default=None,
            help="do not print lyrics")

        self._argparser.add_argument(
            "-f", "--fullscreen",
            action="store_true", dest="fullscreen", default=None,
            help="play videos in fullscreen mode")

        self._argparser.add_argument(
            "--use-mpv",
            action="store_true", dest="use_mpv", default=None,
            help="use mpv as the video player")

        self._argparser.add_argument(
            "--max-width",
            action="store", dest="max_width", default=None,
            help="set the maximum width for the played videos")

        self._argparser.add_argument(
            "--max-height",
            action="store", dest="max_height", default=None,
            help="set the maximum height for the played videos")

        self._argparser.add_argument(
            "-w", "--use-web-api",
            action="store_true", dest="use_web_api", default=None,
            help="forcefully use Spotify's web API")

        self._argparser.add_argument(
            "--client-id",
            action="store", dest="client_id", default=None,
            help="your client ID. Mandatory if the web API is being used."
            " Check the README to learn how to obtain yours."
            " Example: --client-id='5fe01282e44241328a84e7c5cc169165'")

        self._argparser.add_argument(
            "--client-secret",
            action="store", dest="client_secret", default=None,
            help="your client secret ID."
            " Mandatory if the web API is being used."
            " Check the README to learn how to obtain yours."
            " Example: --client-secret='2665f6d143be47c1bc9ff284e9dfb350'")

        self._argparser.add_argument(
            "--redirect-uri",
            action="store", dest="redirect_uri", default=None,
            help="optional redirect uri to get the authorization token."
            " The default is http://localhost:8888/callback/")

        self._argparser.add_argument(
            "--vlc-args",
            action="store", dest="vlc_args", default=None,
            help="custom arguments used when opening VLC."
            " --vlc-args='--video-on-top' is very helpful, for example.")

        self._argparser.add_argument(
            "--mpv-flags",
            action="store", dest="mpv_flags", default=None,
            help="custom boolean flags used when opening mpv, with dashes"
            " and separated by spaces.")

    def read_config_file(self, attr: str):
        """
        Reads the config file data with the corresponding type.
        """

        option = getattr(self._options, attr)

        if option.value_type == bool:
            return self._file.getboolean(option.section, attr)
        elif option.value_type == int:
            return self._file.getint(option.section, attr)
        else:
            return self._file.get(option.section, attr)

    def write_config_file(self, section: str, name: str, value: str):
        """
        Modify a value from the config file. If the section doesn't exist,
        create it.
        """

        if section not in self._file.sections():
            with open(self._path, 'a') as configfile:
                configfile.write(f'\n[{section}]')
            self._file.read(self._path)

        self._file[section][name] = str(value)

        with open(self._path, 'w') as configfile:
            self._file.write(configfile)

    def parse(self, config_path: str = None, custom_args: list = None):
        """
        Get the config file sources data.

        The config path can be passed as a function parameter or as an argument
        inside the program. If none of these exist, the default path will be
        used, defined at the top of this module.

        A config file will also be created if none is found. This means that
        all sections of self._options have to be written.
        """

        self._args = self._argparser.parse_args(custom_args)
        self._path = config_path or self._args.config_path or default_path

        if not os.path.exists(self._path):
            print('Creating config file at', self._path)
            with open(self._path, 'w') as f:
                f.write('[Defaults]')

        self._file.read(self._path)

    def __getattr__(self, attr):
        """
        Return the configuration from all sources in the correct order
        (arguments > config file > defaults)
        """

        # Arguments
        try:
            value = getattr(self._args, attr)
        except AttributeError:
            pass
        else:
            if value not in (None, ''):
                return value

        # Config file
        try:
            value = self.read_config_file(attr)
        except (configparser.NoOptionError, configparser.NoSectionError):
            pass
        else:
            if value not in (None, ''):
                return value

        # Default values
        option = getattr(self._options, attr)
        return option.default
