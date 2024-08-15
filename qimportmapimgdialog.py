import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QDialog, QFileDialog
from ui.importmapimgdialog import Ui_ImportMapImgDialog


class QImportMapImgDialog(QDialog, Ui_ImportMapImgDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.select_file_button.clicked.connect(self.open_file)

    def open_file(self):
        """
        打开选择文件对话框
        """
        file_name, file_type = QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(), "Images (*.png *.jpg)")
        self.file_dir_line.setText(file_name)
        print(file_name)
        # print(file_type)


if __name__ == "__main__":
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    import_map_img_dialog = QImportMapImgDialog()
    import_map_img_dialog.show()
    sys.exit(app.exec_())
