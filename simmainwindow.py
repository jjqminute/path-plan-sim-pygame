import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QDesktopWidget
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ui.mainwindow import Ui_MainWindow
from qimportmapimgdialog import QImportMapImgDialog


class SimMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.center()
        import_map_img_dialog = QImportMapImgDialog(self)
        self.pygameWidget.main_window = self
        self.action_import_img_map.triggered.connect(import_map_img_dialog.open)

    def center(self):
        """
        居中显示MainWindow
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def log(self, msg, x=None, y=None):
        """
        输出日志到主窗口textBrowser
        :param msg: 日志内容
        :param x: 输出为(x,y)
        :param y:
        :return:
        """
        if x is None and y is None:
            self.textBrowser.append("%s" % msg)
        else:
            self.textBrowser.append("%s(%d:%d)" % (msg, x, y))


if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    main_window = SimMainWindow()
    main_window.show()
    sys.exit(app.exec_())
