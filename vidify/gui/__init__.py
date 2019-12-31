"""
This module contains the GUI's theme properties: the colors, icon paths and
fonts.

In the future, these properties could be modified if dark mode was enabled.
"""

from qtpy.QtGui import QFont

from vidify import Platform, CURRENT_PLATFORM


class Colors:
    """
    Contains the theme colors in hexadecimal. This will be useful in the
    future when dark mode is implemented.
    """

    bg = '#eff0eb'
    light = '#eff0eb'
    fg = '#282828'
    dark = '#282828'
    black = '#000000'
    lighterror = '#fc9086'
    darkerror = '#e33120'


class Res:
    """
    Contains the paths for all the resources used in this program.
    """

    icon = "vidify/gui/res/icon16x16.ico" \
        if CURRENT_PLATFORM == Platform.WINDOWS \
        else "vidify/gui/res/icon.svg"
    cross = "vidify/gui/res/cross.svg"
    fonts = ("vidify/gui/res/Inter/Inter-Regular.otf",
             "vidify/gui/res/Inter/Inter-Italic.otf",
             "vidify/gui/res/Inter/Inter-Bold.otf",
             "vidify/gui/res/Inter/Inter-BoldItalic.otf",
             "vidify/gui/res/Inter/Inter-Medium.otf",
             "vidify/gui/res/Inter/Inter-MediumItalic.otf")
    default_api_icon = "vidify/gui/res/api_icons/default.svg"
    default_video = "vidify/gui/res/default_video.mp4"


class Fonts:
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
