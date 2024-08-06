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


def list_algorithm_modules(folder_path):
    algorithm_modules = []
    files = os.listdir(folder_path)
    for file in files:
        module_path = os.path.join(folder_path, file)
        if os.path.isdir(module_path) and '__init__.py' in os.listdir(module_path):
            algorithm_name = os.path.basename(module_path)
            algorithm_modules.append(algorithm_name)
    return algorithm_modules


def load_main_algorithm(module_path):
    module_name = os.path.basename(module_path)
    module = importlib.import_module(f'algorithms.{module_name}.main_algorithm')
    return module.Main


def list_algorithm_classes(algorithm_modules):
    algorithm_classes = []
    for module in algorithm_modules:
        algorithm_class = load_main_algorithm(module)
        algorithm_classes.append(algorithm_class)
    return algorithm_classes


# 选择算法窗口类
class GraphOb(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        algorithm_folder = 'algorithms'

        self.algorithm_modules = list_algorithm_modules(algorithm_folder)
        self.algorithm_classes = list_algorithm_classes(self.algorithm_modules)
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('图形障碍物')
        self.setGeometry(100, 100, 400, 150)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
        # 创建起点标签
        self.label_graph = QLabel("障碍物类型:")
        self.mainLayout.addWidget(self.label_graph)
        # 创建下拉列表
        self.combo_box = QComboBox()
        self.combo_box.addItem("矩形")
        self.combo_box.addItem("圆形")
        self.combo_box.addItem("三角形")
        self.combo_box.addItem("椭圆形")
        self.combo_box.addItem("菱形")
        self.combo_box.addItem("五角形")
        self.mainLayout.addWidget(self.combo_box)
        self.label_notice = QLabel("")
        self.mainLayout.addWidget(self.label_notice)

        self.add_button()

    def add_button(self):
        # 创建生成障碍物按钮
        button_modify = QPushButton("生成")
        self.mainLayout.addWidget(button_modify)
        # 按钮点击事件处理函数
        def on_button_click():
            selected_index = self.combo_box.currentIndex()
            self.pygame_widget.paint_random_one(selected_index + 1)
            self.label_notice.setText("障碍物生成成功！")

        # 连接按钮的点击信号到处理函数
        button_modify.clicked.connect(on_button_click)