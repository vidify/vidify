"""
This module contains the GUI's theme properties: the colors, icon paths and
fonts.

In the future, these properties could be modified if dark mode was enabled.
"""

import os

from qtpy.QtGui import QFont

from vidify import Platform, CURRENT_PLATFORM


# The vidify installation path's resources folder, having in account that this
# module is vidify.gui and that the resources folder is vidify.gui.res.
RESOURCES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'res')


class ColorsBase:
    """
    Contains the theme colors in hexadecimal. This will be useful in the
    future when dark mode is implemented.
    """

    light = '#eff0eb'
    dark = '#282828'
    black = '#000000'
    lighterror = '#fc9086'
    darkerror = '#e33120'


def res_path(rel_path: str) -> str:
    """
    Converts a path relative to the vidify module to an absolute path in
    respect to the user's installation. That way, the module can be launched
    from directories other than the main one.
    """

    return os.path.join(RESOURCES_PATH, rel_path)


def res_font(name: str) -> str:
    """
    Utility function to select a font depending on the user's system.
    The `name` parameter shouldn't include the extension, since that's
    what this function selects.
    """

    extension = ".ttf" if CURRENT_PLATFORM == Platform.WINDOWS \
        else ".otf"

    return res_path(name) + extension


class ResBase:
    """
    Contains the paths for all the resources used in this program.
    """

    fonts = (res_font("Inter/Inter-Regular"),
             res_font("Inter/Inter-Italic"),
             res_font("Inter/Inter-Bold"),
             res_font("Inter/Inter-BoldItalic"),
             res_font("Inter/Inter-Medium"),
             res_font("Inter/Inter-MediumItalic"))

    default_video = res_path("default_video.mp4")

    icon = res_path("icon16x16.ico") \
        if CURRENT_PLATFORM == Platform.WINDOWS \
        else res_path("icon.svg")
    cross = res_path("cross.svg")

    default_api_icon = res_path("api_icons/default.svg")
    mpris_linux_icon = res_path("api_icons/mpris.svg")
    swspotify_icon = res_path("api_icons/spotify/swspotify.svg")
    spotify_web_icon = res_path("api_icons/spotify/web.svg")

    def set_dark_mode(self) -> None:
        """
        If this function is called, all resources dependent on light mode
        will change to dark mode.
        """

        self.cross = res_path("dark_mode_cross.svg")


class FontsBase:
    """
    Contains the fonts for the different types of text.
    """

    smalltext = QFont("Inter", 10, QFont.Medium)
    text = QFont("Inter", 12, QFont.Medium)
    bigtext = QFont("Inter", 14, QFont.Medium)
    title = QFont("Inter", 24, QFont.Bold)
    title.setItalic(True)
    header = QFont("Inter", 20, QFont.Bold)
    header.setItalic(True)

    mediumbutton = QFont("Inter", 15, QFont.Bold)
    bigbutton = QFont("Inter", 18, QFont.Bold)


# The classes are initialized so that they can be dynamically modified from
# other modules acting as global variables, and other utilities like dark
# mode.
Res = ResBase()
Colors = ColorsBase()
Fonts = FontsBase()


def set_dark_mode() -> None:
    """
    This function will set the dark mode for all properties listed in this
    module.
    """

    Res.set_dark_mode()
