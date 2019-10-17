from PySide2.QtGui import QFont


class colors:
    """
    Contains the theme colors in hexadecimal. This will be useful in the
    future when dark mode is implemented.
    """

    bg = 'white'
    fg = '#282828'
    dark = '#282828'


class icons:
    """
    Contains the paths to the icons and images used. This will be useful in
    the future when dark mode is implemented.
    """

    github = 'spotivids/gui/res/github.svg'
    menu = 'spotivids/gui/res/menu.svg'
    close = 'spotivids/gui/res/close.svg'


class fonts:
    """
    Contains the fonts for the different types of text.
    """

    title = QFont("Inter", 32, QFont.Bold)
    link = QFont("Inter", 16)
    link.setItalic(True)
    text = QFont("Inter", 12, QFont.Normal)
