"""
This module contains the GUI's theme properties: the colors, icon paths and
fonts.

In the future, these properties could be modified if dark mode was enabled.
"""

from PySide2.QtGui import QFont


class Colors:
    """
    Contains the theme colors in hexadecimal. This will be useful in the
    future when dark mode is implemented.
    """

    bg = '#eff0eb'
    light = '#eff0eb'
    fg = '#282828'
    dark = '#282828'


class Res:
    """
    Contains the paths for all the resources used in this program.
    """

    icon = "spotivids/gui/res/icon.svg"
    fonts = ("spotivids/gui/res/Inter/Inter-Regular.otf",
             "spotivids/gui/res/Inter/Inter-Italic.otf",
             "spotivids/gui/res/Inter/Inter-Bold.otf",
             "spotivids/gui/res/Inter/Inter-BoldItalic.otf",
             "spotivids/gui/res/Inter/Inter-Medium.otf",
             "spotivids/gui/res/Inter/Inter-MediumItalic.otf")


class Fonts:
    """
    Contains the fonts for the different types of text.
    """

    text = QFont("Inter", 12, QFont.Medium)
    waitconn = QFont("Inter", 15, QFont.Bold)
    waitconn.setItalic(True)
