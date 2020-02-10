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
from enum import Enum
from typing import Optional, Union, Tuple

from appdirs import AppDirs

from vidify.version import __version__


# Default config path in the system
APP_DIRS = AppDirs("vidify", "vidify")
DEFAULT_PATH = os.path.join(APP_DIRS.user_config_dir, "config.ini")


class Options(Enum):
    """
    Enumeration to define the main properties of every option, so that the
    config file options and the arguments can be mixed together inside Config.
    """

    def __new__(cls, description: str, args: Optional[Tuple[str]],
                arg_action: str, section: Optional[str], value_type: type,
                default: any) -> object:
        obj = object.__new__(cls)

        # Description used in the argument parser help message.
        obj.description = description
        # Arguments that the option can take, like ("-p", "--player"), if it's
        # available for the argument parser. Otherwise, it's None.
        obj.args = args
        # The argparse action: 'store', 'store_true'. Will be ignored if `args`
        # is None.
        obj.arg_action = arg_action
        # The section in the config file, like 'Defaults'. If it's not
        # available on the config file, it's None.
        obj.section = section
        # The option's type on both the argument parser and the config file.
        obj.type = value_type
        # The default value that the option takes when it's not found in the
        # arguments or config file.
        obj.default = default

        return obj

    # Debug flag to show useful messages when things go wrong, or for the
    # developers to code.
    # Note: for the argument options with a single identifier, a comma has to
    # be used at the end to specify that it's a tuple.
    debug = (
        "display debug messages",
        ('--debug',),
        'store_true',
        'Defaults',
        bool,
        False)

    # Custom config file, only available for the argument parser.
    config_file = (
        f"the config file path. Default is {DEFAULT_PATH}",
        ('--config-file',),
        'store',
        None,
        str,
        None)

    # Showing the lyrics. For the argument parser, it's a negated option,
    # meaning that it has to be set to False in the config file to be
    # equivalent.
    lyrics = (
        "do not print lyrics",
        ('-n', '--no-lyrics'),
        'store_false',
        'Defaults',
        bool,
        True)

    # Starting the app fullscreen.
    fullscreen = (
        "open the app in fullscreen mode",
        ('-f', '--fullscreen'),
        'store_true',
        'Defaults',
        bool,
        False)

    # The dark mode
    dark_mode = (
        "activate the dark mode",
        ('--dark-mode',),
        'store_true',
        'Defaults',
        bool,
        False)

    # Window that always stays on top of others.
    stay_on_top = (
        "the window will stay on top of all apps.",
        ('--stay-on-top',),
        'store_true',
        'Defaults',
        bool,
        False)

    # Initial window's width.
    width = (
        "set the maximum width for the player. This is helpful to download"
        " lower res videos if your connection isn't too good.",
        ('--width',),
        'store',
        'Defaults',
        int,
        None)

    # Initial window's height.
    height = (
        "set the maximum height for the player",
        ('--height',),
        'store',
        'Defaults',
        int,
        None)

    # API used. If it's None, the initial menu to choose an API will be shown
    # to the user. The option's contents should be one of the names listed in
    # `vidify.api`'s APIData enumeration.
    api = (
        "select the API use. Please read the installation guide for a list"
        "with the available APIs with detailed information about them.",
        ('-a', '--api'),
        'store',
        'Defaults',
        str,
        None)

    # Player used. By default it's VLC. This option's contents should be one
    # of the names listed in `vidify.player`'s PlayerData enumeration.
    player = (
        "select the player to be used. Plase read the installation guide for"
        " a list with the available players. By default, it's VLC.",
        ('-p', '--player'),
        'store',
        'Defaults',
        str,
        "vlc")

    # The audio synchronization feature. It will try to automatically
    # synchronize the video playing with the system recorded audio. Currently
    # only available on Linux.
    audiosync = (
        "enable automatic audio synchronization. You may need to install"
        " additional dependencies. Read the installation guide for more"
        " information. Note: this feature is still in the alpha stage."
        " It's recommended to use Mpv for precision.",
        ('--audiosync',),
        'store_true',
        'Defaults',
        bool,
        False)

    # Option to tweak the audio synchronization extension. This delay is
    # approximately the time taken until the extension starts recording the
    # video. Usually it's about 200ms, but it depends on the hardware so
    # it's left as an option.
    audiosync_calibration = (
        "the audio synchronization's precision may depend on your hardware."
        " You can calibrate the delay in milliseconds returned with this."
        " It can be positive or negative. The default is -800.",
        ('--audiosync-calibration',),
        'store',
        'Defaults',
        int,
        -800)

    # Arguments and options provided for the players.
    vlc_args = (
        "custom arguments used when opening VLC.",
        ('--vlc-args',),
        'store',
        'Defaults',
        str,
        None)

    mpv_flags = (
        "custom boolean flags used when opening mpv, with dashes and"
        " separated by spaces.",
        ('--mpv-flags',),
        'store',
        'Defaults',
        str,
        None)

    # Data for the Spotify Web API
    client_id = (
        "your client ID key for the Spotify Web API. Check the README to"
        " learn how to obtain yours. Example:"
        " --client-id='5fe01282e44241328a84e7c5cc169165'",
        ('--client-id',),
        'store',
        'SpotifyWeb',
        str,
        None)
    client_secret = (
        "your client secret key for the Spotify Web API. Check the wiki to"
        " learn how to obtain yours. Example:"
        " --client-secret='2665f6d143be47c1bc9ff284e9dfb350'",
        ('--client-secret',),
        'store',
        'SpotifyWeb',
        str,
        None)
    redirect_uri = (
        "optional redirect uri for the Spotify Web API to get the"
        " authorization token. The default is http://localhost:8888/callback/",
        ('--redirect-uri',),
        'store',
        'SpotifyWeb',
        str,
        'http://localhost:8888/callback/')
    refresh_token = (
        None,
        None,
        None,
        'SpotifyWeb',
        str,
        None)


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

        for opt in Options:
            if opt.args is None:
                continue

            # Creating a dictionary with the keyword arguments for
            # ArgumentParser.add_argument.
            kwargs = {'action': opt.arg_action, 'dest': opt.name,
                      'default': None, 'help': opt.description}
            # The type mustn't be specified if the action already implies it's
            # a boolean.
            if opt.arg_action not in ('store_false', 'store_true'):
                kwargs['type'] = opt.type

            self._argparser.add_argument(*opt.args, **kwargs)

    def read_file(self, attr: str) -> Optional[Union[bool, int, str]]:
        """
        Reads the value in the config file for a specified attribute. Its type
        and section are obtained from the default options object.
        """

        option = getattr(Options, attr)

        # Checking that it's an option available in the config file.
        if option.section in (None, ''):
            return None

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
                             f" have a valid type ({e}).") from None

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
        self._path = config_file or self._args.config_file or DEFAULT_PATH

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

        # If this doesn't raise AttributeError, it's interpreted as an option,
        # otherwise it's an argument and it shouldn't be written.
        try:
            option = getattr(Options, attr)
        except AttributeError:
            pass
        else:
            self.write_file(option.section, attr, value)

    def __getattr__(self, attr: str) -> Optional[Union[bool, int, str]]:
        """
        Return the configuration from all sources in the correct order:
            arguments > config file > defaults

        __getattr__ isn't called by definition if the attribute exists in
        the object, so any value that was set with __setattr__ previously
        will have priority.
        """

        # Arguments
        try:
            value = getattr(self._args, attr)
        except AttributeError:
            pass
        else:
            if value is not None:
                return value

        # Config file
        try:
            value = self.read_file(attr)
        except (configparser.NoOptionError, configparser.NoSectionError):
            pass
        else:
            if value is not None:
                return value

        # If it wasn't in the arguments or config file, the default value is
        # returned.
        option = getattr(Options, attr)
        return option.default
