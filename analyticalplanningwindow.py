# # 姓名：jujianqiang
# # 2024/7/29 14:19
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
class AnalyticalPlanningWindow(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        algorithm_folder = 'algorithms'

        self.algorithm_modules = list_algorithm_modules(algorithm_folder)
        self.algorithm_classes = list_algorithm_classes(self.algorithm_modules)
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('分析规划')
        self.setGeometry(100, 100, 400, 300)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
        self.add_button()

    def add_button(self):
        button1 = QPushButton('单次路径结果比较分析')
        button1.clicked.connect(self.on_single_click())
        self.mainLayout.addWidget(button1)
        button2 = QPushButton('多次路径比较分析')
        # button.clicked.connect(self.run_algorithm)
        self.mainLayout.addWidget(button2)
        button3 = QPushButton('不同算法性能比较')
        # button.clicked.connect(self.run_algorithm)
        self.mainLayout.addWidget(button3)

    # 单次路径结果比较分析方法
    def on_single_click(self):
        files, _ = QFileDialog.getOpenFileNames(self, '打开结果文件', '', '结果文件 (*.txt)')
        for index, f in enumerate(files):  # 循环选中的所有文件
            self.open_result_single(index, f)


