from spotivids.gui import colors, icons, fonts

from PySide2.QtWidgets import (QHBoxLayout, QVBoxLayout, QFrame, QLabel,
                               QPushButton)
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import Qt, QPropertyAnimation, QPoint, QSize, QRect


class Drawer(QFrame):
    def __init__(self, *args, **kwargs):
        """
        The drawer is the sidebar to the left with quick actions and
        configuration tools. It has a sliding animation to appear or
        disappear from the main window.
        """

        super().__init__(*args, **kwargs)

        # Main properties
        self.setGeometry(-300, 0, 300, 500)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)

        # Setting up the elements
        self.setup_animations()
        self.setup_title()
        self.setup_github()
        self.setup_close_button()

        #  self.layout.addStretch()

    def setup_animations(self):
        self.slidein = QPropertyAnimation(self, b'pos')
        self.slidein.setDuration(400)
        self.slidein.setEndValue(QPoint(0, 0))

        self.slideout = QPropertyAnimation(self, b'pos')
        self.slideout.setDuration(400)
        self.slideout.setEndValue(QPoint(-self.width(), 0))

    def setup_close_button(self):
        label = QLabel(self)
        pixmap = QPixmap(icons.close)
        label.setPixmap(pixmap)
        label.setGeometry(self.width(), 0, 50, 50)

    def setup_title(self):
        self.title = QLabel("Spotivids")
        self.title.setFont(fonts.title)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(f"color: {colors.fg};"
                                 "padding-top: 10px;")
        self.layout.addWidget(self.title)

    def setup_github(self):
        self.github = QHBoxLayout()
        self.github.setAlignment(Qt.AlignCenter)

        img = QLabel("<a href='https://github.com' style='color:inherit;"
                     " text-decoration: none;'></a>")
        img.setToolTip("Click to open the GitHub repository")
        img.setPixmap(QPixmap(icons.github))
        img.setStyleSheet("padding: 7px")
        self.github.addWidget(img)

        # URL without the hyperlink style
        label = QLabel(f"<a href='https://github.com' style='color:inherit;"
                       " text-decoration: none;'>"
                       "<span style:'color: {colors.fg};'>GitHub</span></a>")
        label.setToolTip("Click to open the GitHub repository")
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label.setFont(fonts.link)
        self.github.addWidget(label)
        self.layout.addLayout(self.github)


class DrawerButton(QPushButton):
    def __init__(self, *args, **kwargs):
        """
        The button that opens the drawer. It fades in when the user moves
        the cursor over the window, and fades away after 3 seconds.
        """

        super().__init__('', *args, **kwargs)

        self.setIcon(QIcon(icons.menu))
        self.setIconSize(QSize(40, 40))
        self.setGeometry(10, 10, 50, 50)
        self.setFlat(True)

        #  self.fadein_btn = QPropertyAnimation(self, b'geometry')
        #  self.fadein_btn.setDuration(500)
        #  self.fadein_btn.setStartValue(QRect())
        #  self.fadein_btn.setEndValue(QSize(50, 50))
        #  self.fadein_btn.start()
