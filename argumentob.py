# 姓名：jujianqiang
# 2024/7/30 15:41
# 参数障碍物窗口 根据用户选择生成相同大小障碍物
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
class ArgumentOb(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        algorithm_folder = 'algorithms'

        self.algorithm_modules = list_algorithm_modules(algorithm_folder)
        self.algorithm_classes = list_algorithm_classes(self.algorithm_modules)
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('参数障碍物')
        self.setGeometry(100, 100, 400, 300)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

        self.label_sum = QLabel("障碍物数量:")
        self.mainLayout.addWidget(self.label_sum)
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setPlaceholderText("请输入障碍物的数量")  # 设置提示文字
        self.mainLayout.addWidget(self.lineEdit1)

        self.label_size = QLabel("障碍物大小:")
        self.mainLayout.addWidget(self.label_size)

        self.slider = QSlider()
        self.slider.setMinimum(5)  # 设置最小值
        self.slider.setMaximum(200)  # 设置最大值
        self.slider.setOrientation(Qt.Horizontal)  # 设置水平方向
        self.mainLayout.addWidget(self.slider)
        # 创建标签用于显示滑块的值
        self.label_slider_value = QLabel("5")
        self.mainLayout.addWidget(self.label_slider_value)
        # 连接滑块数值改变的信号和槽
        self.slider.valueChanged.connect(lambda value: self.label_slider_value.setText(str(value)))
        self.label_type = QLabel("障碍物类型:")
        self.mainLayout.addWidget(self.label_type)
        # 创建多选框
        self.checkbox1 = QCheckBox("圆形")
        self.mainLayout.addWidget(self.checkbox1)

        self.checkbox2 = QCheckBox("正方形")
        self.mainLayout.addWidget(self.checkbox2)

        self.checkbox3 = QCheckBox("椭圆")
        self.mainLayout.addWidget(self.checkbox3)

        self.checkbox4 = QCheckBox("菱形")
        self.mainLayout.addWidget(self.checkbox4)

        self.checkbox5 = QCheckBox("矩形")
        self.mainLayout.addWidget(self.checkbox5)
        self.label_type1 = QLabel("障碍物重叠:")
        self.mainLayout.addWidget(self.label_type1)
        # 创建单选按钮组
        self.radio_button_group = QButtonGroup()
        self.radio_button_group.setExclusive(True)  # 设置为互斥，只能选择一个单选按钮
        # self.mainLayout.addWidget(self.radio_button_group)

        # 创建是单选按钮
        self.radio_button_ok = QRadioButton("重叠")
        self.radio_button_group.addButton(self.radio_button_ok)  # 将单选按钮添加到单选按钮组
        self.mainLayout.addWidget(self.radio_button_ok)

        # 创建是单选按钮
        self.radio_button_no = QRadioButton("分离")
        self.radio_button_group.addButton(self.radio_button_no)  # 将单选按钮添加到单选按钮组
        self.mainLayout.addWidget(self.radio_button_no)

        self.label_notice = QLabel("")
        self.mainLayout.addWidget(self.label_notice)

        self.add_button()

    def add_button(self):
        # 创建生成障碍物按钮
        button_generate_obstacle = QPushButton("生成障碍物")
        self.mainLayout.addWidget(button_generate_obstacle)
        def on_button_click():
            obstacle_quantity = self.lineEdit1.text()
            if not obstacle_quantity:
                self.label_notice.setText("请输入障碍物数量！")
                return
            obstacle_size = self.slider.value()
            obstacle_types = []
            if not self.checkbox1.isChecked() and not self.checkbox2.isChecked() and not self.checkbox3.isChecked() and not self.checkbox4.isChecked() and not self.checkbox5.isChecked():
                self.label_notice.setText("请选择至少一种障碍物类型！")
                return
            if self.checkbox1.isChecked():
                obstacle_types.append(0)
            if self.checkbox2.isChecked():
                obstacle_types.append(1)
            if self.checkbox3.isChecked():
                obstacle_types.append(2)
            if self.checkbox4.isChecked():
                obstacle_types.append(3)
            if self.checkbox5.isChecked():
                obstacle_types.append(4)
            if not self.radio_button_ok.isChecked() and not self.radio_button_no.isChecked():
                self.label_notice.setText("请选择障碍物是否重叠！")
                return
            if self.radio_button_ok.isChecked():
                obstacle_overlap = "T"
            elif self.radio_button_no.isChecked():
                obstacle_overlap = "F"
            self.pygame_widget.graph_setting(obstacle_quantity, obstacle_size, obstacle_types, obstacle_overlap)
            self.label_notice.setText("障碍物生成成功！")

        # 连接按钮的点击信号
        button_generate_obstacle.clicked.connect(on_button_click)