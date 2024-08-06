# 姓名：jujianqiang
# 2024/7/30 14:56
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
class RandomOb(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('随机障碍物')
        self.setGeometry(100, 100, 400, 300)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
        self.add_button()

    def add_button(self):
        # 创建一个水平布局管理器
        label_sum = QLabel("障碍物数量:")
        self.mainLayout.addWidget(label_sum)
        lineEdit1 = QLineEdit()
        lineEdit1.setPlaceholderText("请输入障碍物的数量")
        self.mainLayout.addWidget(lineEdit1)
        button_generate_obstacle = QPushButton("生成障碍物")

        self.mainLayout.addWidget(button_generate_obstacle)
        label_notice = QLabel("")
        self.mainLayout.addWidget(label_notice)
        pygame_widget1 = self.pygame_widget

        def on_button_click():
            obstacle_quantity = lineEdit1.text()
            if not obstacle_quantity:
                label_notice.setText("请输入障碍物数量！")
                return
            pygame_widget1.random_graph_new(int(obstacle_quantity))
            label_notice.setText("障碍物生成成功！")

        # 连接按钮的点击信号
        button_generate_obstacle.clicked.connect(on_button_click)
