import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ui.mainwindow import Ui_MainWindow


class Sim(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    main_window = Sim()
    main_window.show()
    sys.exit(app.exec_())
