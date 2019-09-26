from typing import Union

from PySide2.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self, widget: Union['VLCPlayer', 'MpvPlayer'],
                 width: int = 800, height: int = 600) -> None:
        """
        Main window with whatever player is being used.
        """

        super().__init__()
        self.setWindowTitle('spotivids')
        self.setStyleSheet('background-color: #282828')
        if None not in (height, width):
            self.resize(width, height)
        self.setCentralWidget(widget)
