# 姓名：jujianqiang
# 2024/7/29 15:40
import re
import os
import importlib
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication, QFileDialog, QLineEdit, QLabel, QSlider, \
    QCheckBox, QButtonGroup, QRadioButton, QPushButton, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from algorithmlist import AlgorithmList

from mappygame import PygameWidget
from result import load_demo, Category_Demo, Category_Compare


# 选择算法窗口类
class ModifyMap(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('调整地图栅格化')
        self.setGeometry(100, 100, 400, 150)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

        # 创建障碍物数量标签
        self.label_sum = QLabel("栅格大小:")
        self.mainLayout.addWidget(self.label_sum)
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setPlaceholderText("请输入栅格大小")  # 设置提示文字
        self.mainLayout.addWidget(self.lineEdit1)
        self.label_notice = QLabel("")
        self.mainLayout.addWidget(self.label_notice)
        self.add_button()

    def add_button(self):
        # 创建生成障碍物按钮
        button_modify = QPushButton("调整")
        button_default = QPushButton("默认")
        self.mainLayout.addWidget(button_modify)
        self.mainLayout.addWidget(button_default)

        def on_button_click():
            obstacle_quantity = self.lineEdit1.text()
            if not obstacle_quantity:
                self.label_notice.setText("请输入地图栅格大小！")
                return
            try:
                int(obstacle_quantity)
                self.pygame_widget.modifyMap(int(obstacle_quantity))
            except (ValueError, TypeError):
                self.label_notice.setText("请输入正确的整型栅格大小！")
                return
            self.label_notice.setText("栅格大小修改成功！")

        def on_button_default():
            print("默认地图")

        # 连接按钮的点击信号
        button_modify.clicked.connect(on_button_click)
