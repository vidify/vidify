import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QLabel


class MainWindow(QMainWindow):
    def __init__(self, widget):
        """
        Main window with whatever player is being used.
        """

        QMainWindow.__init__(self)

        self.setWindowTitle("spotivids")
        self.resize(800, 600)
        self.setCentralWidget(widget)
