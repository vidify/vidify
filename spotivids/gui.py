from PySide2.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self, widget: QWidget, width: int = 800, height: int = 600):
        """
        Main window with whatever player is being used.
        """

        QMainWindow.__init__(self)

        self.setWindowTitle('spotivids')
        self.setStyleSheet('background-color: #282828')
        if None not in (height, width):
            self.resize(width, height)
        self.setCentralWidget(widget)
