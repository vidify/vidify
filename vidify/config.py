"""
This module combines customization options from the three different sources,
in order of priority:
    * __setattr__
    * The argument parser
    * The config file
    * The default options
"""

import os
import errno
import argparse
import configparser
from dataclasses import dataclass
from typing import Optional, Union, Tuple, Any

from appdirs import AppDirs

from vidify import Platform, CURRENT_PLATFORM
from vidify.version import __version__


# Default config path in the system
APP_DIRS = AppDirs("vidify", "vidify")
DEFAULT_PATH = os.path.join(APP_DIRS.user_config_dir, "config.ini")


@dataclass
class Option:
    # Description used in the argument parser help message.
    description: str
    # The option's type on both the argument parser and the config file.
    type: type
    # The default value that the option takes when it's not found in the
    # arguments or config file.
    default: Any


@dataclass
class Argument(Option):
    # The argparse action: 'store', 'store_true'. Will be ignored if `args`
    # is None.
    arg_action: str
    # Arguments that the option can take, like ("-p", "--player"), if it's
    # available for the argument parser. Otherwise, it's None.
    args: Tuple[str, ...]


@dataclass
class ConfigOption(Option):
    # The section in the config file, like 'Defaults'. If it's not
    # available on the config file, it's None.
    section: str


@dataclass
class FullOption(Argument, ConfigOption):
    pass


OPTIONS = {
    # Debug flag to show useful messages when things go wrong, or for the
    # developers to code.
    # Note: for the argument options with a single identifier, a comma has to
    # be used at the end to specify that it's a tuple.
    'debug': FullOption(
        description="display debug messages.",
        type=bool,
        default=False,
        args=('--debug',),
        arg_action='store_true',
        section='Defaults'),

    # Custom config file, only available for the argument parser.
    'config_file': Argument(
        description=f"the config file path.",
        type=str,
        default=DEFAULT_PATH,
        args=('--config-file',),
        arg_action='store'),

    # Showing the lyrics. For the argument parser, it's a negated option,
    # meaning that it has to be set to False in the config file to be
    # equivalent.
    'lyrics': FullOption(
        description="do not print lyrics.",
        type=bool,
        default=True,
        args=('-n', '--no-lyrics'),
        arg_action='store_false',
        section='Defaults'),

    # Starting the app fullscreen.
    'fullscreen': FullOption(
        description="open the app in fullscreen mode.",
        type=bool,
        default=False,
        args=('-f', '--fullscreen'),
        arg_action='store_true',
        section='Defaults'),

    # The dark mode
    'dark_mode': FullOption(
        description="activate the dark mode.",
        type=bool,
        default=False,
        args=('--dark-mode',),
        arg_action='store_true',
        section='Defaults'),

    # Window that always stays on top of others.
    'stay_on_top': FullOption(
        description="the window will stay on top of all apps.",
        type=bool,
        default=False,
        args=('--stay-on-top',),
        arg_action='store_true',
        section='Defaults'),

    # Initial window's width.
    'width': FullOption(
        description="set the maximum width for the player. This is helpful to"
        " download lower res videos if your connection isn't too good.",
        type=int,
        default=None,
        args=('--width',),
        arg_action='store',
        section='Defaults'),

    # Initial window's height.
    'height': FullOption(
        description="set the maximum height for the player.",
        type=int,
        default=None,
        args=('--height',),
        arg_action='store',
        section='Defaults'),

    # API used. If it's None, the initial menu to choose an API will be shown
    # to the user. The option's contents should be one of the names listed in
    # `vidify.api`'s APIData enumeration.
    'api': FullOption(
        description="select the API use. Please read the installation guide"
        " for a list with the available APIs with detailed information about"
        " them.",
        type=str,
        default=None,
        args=('-a', '--api'),
        arg_action='store',
        section='Defaults'),

    # Player used. By default it's VLC. This option's contents should be one
    # of the names listed in `vidify.player`'s PlayerData enumeration.
    'player': FullOption(
        description="select the player to be used. Plase read the installation"
        " guide for a list with the available players.",
        type=str,
        default="VLC",
        args=('-p', '--player'),
        arg_action='store',
        section='Defaults'),

    # The audio synchronization feature. It will try to automatically
    # synchronize the video playing with the system recorded audio. Currently
    # only available on Linux.
    'audiosync': FullOption(
        description="enable automatic audio synchronization. You may need to"
        " install additional dependencies. Read the installation guide for"
        " more information. Note: this feature is still in development."
        " It's recommended to use Mpv for precision.",
        type=bool,
        default=False,
        args=('--audiosync',),
        arg_action='store_true',
        section='Defaults'),

    # Option to tweak the audio synchronization extension. This delay is
    # approximately the time taken until the extension starts recording the
    # video. Usually it's about 200ms, but it depends on the hardware so
    # it's left as an option.
    'audiosync_calibration': FullOption(
        description="the audio synchronization's precision may depend on your"
        " hardware. You can calibrate the delay in milliseconds returned with"
        " this. It can be positive or negative.",
        type=int,
        default=0,
        args=('--audiosync-calibration',),
        arg_action='store',
        section='Defaults'),

    # Arguments and options provided for the players.
    'vlc_args': FullOption(
        description="custom arguments used when opening VLC.",
        type=str,
        default=None,
        args=('--vlc-args',),
        arg_action='store',
        section='Defaults'),

    'mpv_flags': FullOption(
        description="custom boolean flags used when opening mpv, with dashes"
        " and separated by spaces.",
        type=str,
        default=None,
        args=('--mpv-flags',),
        arg_action='store',
        section='Defaults'),

    # Data for the Spotify Web API
    'client_id': FullOption(
        description="your client ID key for the Spotify Web API. Check the"
        " README to learn how to obtain yours. Example:"
        " --client-id='5fe01282e44241328a84e7c5cc169165'.",
        type=str,
        default=None,
        args=('--client-id',),
        arg_action='store',
        section='SpotifyWeb'),

    'client_secret': FullOption(
        description="your client secret key for the Spotify Web API. Check the"
        " wiki to learn how to obtain yours. Example:"
        " --client-secret='2665f6d143be47c1bc9ff284e9dfb350'.",
        type=str,
        default=None,
        args=('--client-secret',),
        arg_action='store',
        section='SpotifyWeb'),

    'redirect_uri': FullOption(
        description="optional redirect uri for the Spotify Web API to get the"
        " authorization token.",
        type=str,
        default='http://localhost:8888/callback/',
        args=('--redirect-uri',),
        arg_action='store',
        section='SpotifyWeb'),

    'refresh_token': ConfigOption(
        description="Internal field to save the Spotify Web login token for"
        " future accesses.",
        type=str,
        default=None,
        section='SpotifyWeb')
}


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
            prog="vidify",
            description="Read more about the options in the README and the"
            " wiki at https://github.com/vidify/vidify")
        self.add_arguments()

        self._file = configparser.ConfigParser()
        self._args = None
        self._path = None

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

        # The used arguments are fairly simple, so they can be initialized
        # automatically.
        for name, data in OPTIONS.items():
            if not isinstance(data, Argument):
                continue

            # A text with the default value is also shown in the description.
            if data.arg_action == "store_false":
                default = not data.default
            else:
                default = data.default
            default_str = f"Default is '{default}'"
            if CURRENT_PLATFORM == Platform.WINDOWS:
                default_str = "[" + default_str + "]"
            else:
                default_str = "\033[34m" + default_str + "\033[0m"

            kwargs = {
                'action': data.arg_action,
                'dest': name,
                'default': None,
                'help': data.description + " " + default_str
            }
            # Only store arguments must specify their type.
            if data.arg_action == 'store':
                kwargs['type'] = data.type

            self._argparser.add_argument(*data.args, **kwargs)

    def read_file(self, attr: str) -> Optional[Union[bool, int, str]]:
        """
        Reads the value in the config file for a specified attribute. Its type
        and section are obtained from the default options object.

        This assumes the key's option data inherits form ConfigOption.
        """

        option = OPTIONS[attr]

        # Trying all the different types. If a conversion error happens, a
        # ValueError is raised.
        try:
            if option.type == bool:
                return self._file.getboolean(option.section, attr)

            if option.type == int:
                return self._file.getint(option.section, attr)

            return self._file.get(option.section, attr)
        except ValueError as e:
            # Showing a more detailed error than the one given by configparser
            raise ValueError(f"Error when parsing the config file: in the"
                             f" {option.section} section, {attr} doesn't"
                             f" have a valid type ({e}).")

    def write_file(self, section: str, name: str, value: any) -> None:
        """
        Modifies a value from the config file. If the section doesn't exist,
        it's created.
        """

        # The value's type should only be converted to a string if it's not
        # None, in which case nothing is written. This is because converting
        # None to str doesn't raise an error. Instead, the literal 'None'
        # is written.
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

    def parse(self, config_file: Optional[str] = None) -> None:
        """
        Parses the options from the arguments and config file.

        The config path can be passed as a function parameter or as an argument
        inside the program. If none of these exist, the default path will be
        used, defined at the top of this file.

        The config file will also be created if it isn't found.
        """

        self._args = self._argparser.parse_args()
        self._path = config_file or self.config_file

        # Checking if the directory exists and creating it
        dirname = os.path.dirname(self._path)
        if not os.path.isdir(dirname) and dirname not in (None, ''):
            # Checking for a race condition
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        # Checking if the file exists and creating it
        if not os.path.exists(self._path):
            print("Creating config file at", self._path)
            with open(self._path, 'w') as f:
                f.write("[Defaults]\n")

        self._file.read(self._path)

    def __setattr__(self, attr: str, value: any) -> None:
        """
        The usual __setattr__ function, but it also updates the config file
        with the value (unless it's None).
        """

        # The value is still saved inside the object, so that the assigned
        # value will have priority over defaults/config file/arguments
        self.__dict__[attr] = value

        # Internal attributes will also call this method when they're set,
        # so this makes sure it's a valid option when it's written into the
        # config file.
        try:
            option = OPTIONS[attr]
        except KeyError:
            pass
        else:
            if isinstance(option, ConfigOption):
                self.write_file(option.section, attr, value)

    def __getattr__(self, attr: str) -> Optional[Union[bool, int, str]]:
        """
        Return the configuration from all sources in the correct order:
            arguments > config file > defaults

        __getattr__ isn't called by definition if the attribute exists in
        the object, so any value that was set with __setattr__ previously
        will have priority.
        """

        option = OPTIONS[attr]

        if isinstance(option, Argument):
            value = getattr(self._args, attr)
            # The arguments are configured to default to None.
            if value is not None:
                return value

        # The config option might be empty, like this:
        #   [Defaults]
        #   option =
        # Or the [Defaults] section isn't declared, which raises a different
        # exception.
        if isinstance(option, ConfigOption):
            try:
                value = self.read_file(attr)
            except (configparser.NoOptionError, configparser.NoSectionError):
                pass
            else:
                if value is not None:
                    return value

        # If it wasn't in the arguments or config file, the default value is
        # returned.
        return option.default
