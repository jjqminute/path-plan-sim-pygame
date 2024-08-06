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
class InputStartAndEnd(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        algorithm_folder = 'algorithms'

        self.algorithm_modules = list_algorithm_modules(algorithm_folder)
        self.algorithm_classes = list_algorithm_classes(self.algorithm_modules)
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('输入起始点')
        self.setGeometry(100, 100, 400, 300)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

 # 创建起点标签
        self.label_start = QLabel("起点:")
        self.mainLayout.addWidget(self.label_start)
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setPlaceholderText("请输入起点（x，y）")  # 设置提示文字
        self.mainLayout.addWidget(self.lineEdit1)

        # 创建起点标签
        self.label_end = QLabel("终点:")
        self.mainLayout.addWidget(self.label_end)

        # 创建第一个输入框
        self.lineEdit2 = QLineEdit()
        self.lineEdit2.setPlaceholderText("请输入起点（x，y）")  # 设置提示文字
        self.mainLayout.addWidget(self.lineEdit2)



        self.abel_notice = QLabel("")
        self.mainLayout.addWidget(self.abel_notice)

        self.add_button()
    def add_button(self):
        # 创建生成起始点按钮
        button_modify = QPushButton("生成")
        self.mainLayout.addWidget(button_modify)
        def on_button_click():
            start = self.lineEdit1.text()
            end = self.lineEdit2.text()

            # TODO 起始点坐标获取以及调用方法未完成
            if not start and not end:
                self.label_notice.setText("请输入起始点坐标！")
                return

            print(start)
            pattern = r"\((\d+),(\d+)\)"  # 匹配坐标的正则表达式模式
            match = re.match(pattern, start)
            print(match)
            if match:
                keyx = int(match.group(1))  # 提取横坐标
                keyy = int(match.group(2))  # 提取纵坐标
                print("起点横坐标:", keyx)
                print("起点纵坐标:", keyy)
                self.pygame_widget.painting_ori(keyx, keyy)  # 目前执行到这里程序就结束了，应该是调用有问题
            else:
                print("坐标格式不正确")
            match_2 = re.match(pattern, end)
            if match_2:
                # global keyx_2, keyy_2
                keyx_2 = int(match_2.group(1))  # 提取横坐标
                keyy_2 = int(match_2.group(2))  # 提取纵坐标
                print("终点横坐标:", keyx_2)
                print("终点纵坐标:", keyy_2)
                self.pygame_widget.painting_end(keyx_2, keyy_2)
            else:
                print("坐标格式不正确")
            self.label_notice.setText("输入起始点生成成功！")
        # 连接按钮的点击信号
        button_modify.clicked.connect(on_button_click)

