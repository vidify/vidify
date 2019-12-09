"""
This module combines customization options from the three different sources,
in order of priority:
    * The argument parser
    * The config file
    * The default options
"""

import os
import errno
import argparse
import configparser
from typing import Optional, Union
from dataclasses import dataclass

from appdirs import AppDirs

from spotivids.version import __version__


# Default config path in the system
dirs = AppDirs("spotivids", "marioom")
DEFAULT_PATH = os.path.join(dirs.user_config_dir, "config.ini")


@dataclass
class Option:
    """
    Dataclass to define the main properties of every object:
        * The section in the config file
        * The type of the values the variable can take
        * The default value for the option
    """

    section: str
    value_type: type
    default: any


class Options:
    """
    This class lists all the available options with their section, type
    and their default value.
    """

    # Debug flag to show useful messages when things go wrong, or for the
    # developers to code.
    debug = Option('Defaults', bool, False)
    # Showing lyrics in the terminal.
    lyrics = Option('Defaults', bool, True)
    # Starting the app fullscreen.
    fullscreen = Option('Defaults', bool, False)
    # Window that always stays on top of others.
    stay_on_top = Option('Defaults', bool, False)
    # Initial window's width.
    width = Option('Defaults', int, None)
    # Initial window's height.
    height = Option('Defaults', int, None)
    # API used. If it's None, the initial menu to choose an API will be shown
    # to the user. The option's contents should be one of the names listed in
    # `spotivids.api`'s `APIs` enumeration (the __init__.py file).
    api = Option('Defaults', str, None)
    # Player used. By default it's VLC. This option's contents should be one
    # of the names listed in `spotivids.player`'s `Players` enumeration (the
    # __init__.py file).
    player = Option('Defaults', str, "vlc")
    # Arguments and options provided for the players.
    vlc_args = Option('Defaults', str, None)
    mpv_flags = Option('Defaults', str, None)

    # Using the web API, and its credentials/data.
    client_id = Option('WebAPI', str, None)
    client_secret = Option('WebAPI', str, None)
    redirect_uri = Option('WebAPI', str, 'http://localhost:8888/callback/')
    auth_token = Option('WebAPI', str, None)
    refresh_token = Option('WebAPI', str, None)
    expiration = Option('WebAPI', int, None)


class Config:
    """
    Class containing all configuration options from both the argument parser
    and the config file.
    """

    def __init__(self) -> None:
        """
        Initializing the argument parser and the config file.
        """

        self._argparser = argparse.ArgumentParser(
            prog="spotivids",
            description="Windows and macOS users must pass --client-id"
            " and --client-secret to use the web API."
            " Read more about how to obtain them in the README at"
            " https://github.com/marioortizmanero/spotivids")
        self.add_arguments()

        self._file = configparser.ConfigParser()

    def add_arguments(self) -> None:
        """
        Initializes all the available options for the argument parser.

        The default values must be set to None, because the fallback values
        will be determined later in the __getattr__ function.
        """

        self._argparser.add_argument(
            "-v", "--version",
            action="version",
            version=f"%(prog)s {__version__}",
            help="show program's version number and exit")

        self._argparser.add_argument(
            "--debug",
            action="store_true", dest="debug", default=None,
            help="display debug messages")

        self._argparser.add_argument(
            "--config-file",
            action="store", dest="config_path", default=None,
            help=f"the config file path. Default is {DEFAULT_PATH}")

        self._argparser.add_argument(
            "-n", "--no-lyrics",
            action="store_false", dest="lyrics", default=None,
            help="do not print lyrics")

        self._argparser.add_argument(
            "-f", "--fullscreen",
            action="store_true", dest="fullscreen", default=None,
            help="play videos in fullscreen mode")

        self._argparser.add_argument(
            "--stay-on-top",
            action="store_true", dest="stay_on_top", default=None,
            help="the window will stay on top of all apps.")

        self._argparser.add_argument(
            "-p", "--player",
            action="store", dest="player", default=None,
            help="select the player to be used. Plase read the installation"
            " guide for a list with the available players. By default, it's"
            " VLC.")

        self._argparser.add_argument(
            "--width",
            action="store", dest="width", default=None,
            help="set the maximum width for the player")

        self._argparser.add_argument(
            "--height",
            action="store", dest="height", default=None,
            help="set the maximum height for the player")

        self._argparser.add_argument(
            "-a", "--api",
            action="store", dest="api", default=None,
            help="select the player to be used. Please read the installation"
            " guide for a list with the available APIs.")

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

    def read_file(self, attr: str) -> Union[bool, int, str]:
        """
        Reads the value in the config file for a specified attribute. Its type
        and section are obtained from the default options object.
        """

        option = getattr(Options, attr)

        try:
            if option.value_type == bool:
                return self._file.getboolean(option.section, attr)
            elif option.value_type == int:
                # ValueError is raised if attr is '' (empty). When this
                # happens, None should be returned instead.
                try:
                    return self._file.getint(option.section, attr)
                except ValueError:
                    return None
            else:
                return self._file.get(option.section, attr)
        except ValueError as e:
            # Showing a more detailed error than the one given by configparser
            raise ValueError(f"Error when parsing the config file: in the"
                             f" {option.section} section, {attr} doesn't"
                             f" have a valid type ({e}).") from None

    def write_file(self, section: str, name: str, value: any) -> None:
        """
        Modifies a value from the config file. If the section doesn't exist,
        it's created.
        """

        # The value's type should only be converted to a string if it's not
        # None, in which case nothing is written.
        if value is None:
            return

        if section not in self._file.sections():
            with open(self._path, 'a') as configfile:
                configfile.write(f'\n[{section}]')
            # Refreshing the config file
            self._file.read(self._path)

        self._file[section][name] = str(value)
        with open(self._path, 'w') as configfile:
            self._file.write(configfile)

    def parse(self, config_path: Optional[str] = None) -> None:
        """
        Parses the options from the arguments and config file.

        The config path can be passed as a function parameter or as an argument
        inside the program. If none of these exist, the default path will be
        used, defined at the top of this file.

        The config file will also be created if it isn't found.
        """

        self._args = self._argparser.parse_args()
        self._path = config_path or self._args.config_path or DEFAULT_PATH

        # Checking if the directory exists and creating it
        dirname = os.path.dirname(self._path)
        if not os.path.isdir(dirname) and dirname not in (None, ''):
            # Checking for a race condition (not important)
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        # Checking if the file exists and creating it
        if not os.path.exists(self._path):
            print("Creating config file at", self._path)
            with open(self._path, 'w') as f:
                # Documentation about the config file is saved in the new file
                f.write("[Defaults]\n")

        self._file.read(self._path)

    def __setattr__(self, attr: str, value: any) -> None:
        """
        The usual __setattr__ function, but it also updates the config file
        with the new value (unless it's None, because `configfile` does a
        conversion to str and saves 'None' instead of '')
        """

        # The value is still saved inside the object, so that the assigned
        # value will have priority over defaults/config file/arguments
        self.__dict__[attr] = value
        try:
            # If this is obtained correctly, it's interpreted as an option
            option = getattr(Options, attr)
        except AttributeError:
            pass
        else:
            self.write_file(option.section, attr, value)

    def __getattr__(self, attr: str) -> Union[bool, int, str]:
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
            value = self.read_file(attr)
        except (configparser.NoOptionError, configparser.NoSectionError):
            pass
        else:
            if value not in (None, ''):
                return value

        # If it wasn't in the arguments or config file, the default value is
        # returned.
        option = getattr(Options, attr)
        return option.default
