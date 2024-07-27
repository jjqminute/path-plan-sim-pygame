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
class SelectAlgorithmWindow(QMainWindow):
        def __init__(self, pygame_widget):
            super().__init__()
            algorithm_folder = 'algorithms'

            self.algorithm_modules = list_algorithm_modules(algorithm_folder)
            self.algorithm_classes = list_algorithm_classes(self.algorithm_modules)
            self.pygame_widget = pygame_widget
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle('算法选择')
            self.setGeometry(100, 100, 400, 300)

            self.centralWidget = QWidget(self)
            self.setCentralWidget(self.centralWidget)

            self.mainLayout = QVBoxLayout()
            self.centralWidget.setLayout(self.mainLayout)

            # 添加算法选择的下拉列表
            self.algorithmComboBox = QComboBox()
            self.algorithmComboBox.addItems(self.algorithm_modules)
            self.mainLayout.addWidget(self.algorithmComboBox)

            # 添加其他组件
            # self.addParameterInput("Parameter 1", 0, 10)
            # self.addParameterInput("Parameter 2", 1, 100)
            # 添加更多参数...

            
            # 保存结果部分
            self.radioLayout1 = QHBoxLayout()
            label_result = QLabel("是否保存结果:")
            self.radioLayout1.addWidget(label_result)
            # label_result.setGeometry(30, 60, 80, 30)
            self.radio_button_result = QButtonGroup()
            self.radio_button_result.setExclusive(True)

            self.add_radio_buttons()
            # self.radioLayout.setSpacing(100)
            # self.radioLayout.setAlignment(QtCore.Qt.AlignHCenter)

            self.mainLayout.addLayout(self.radioLayout1)
            # 设置结果文件名称的部分
            self.label_path = QLabel("")
            self.mainLayout.addWidget(self.label_path)
            # label_path.setGeometry(30, 120, 200, 30)
            self.line_edit_result = QLineEdit("")
            self.line_edit_result.setPlaceholderText("请输入文件名")
            self.mainLayout.addWidget(self.line_edit_result)
            # line_edit_result.setGeometry(90, 150, 120, 30)
            self.line_edit_result.hide()  # 默认是不保存结果,所以先隐藏

            self.radio_button_result.buttonClicked.connect(self.on_result_click)
            # 运行次数部分
            self.radioLayout2 = QHBoxLayout()
            self.mainLayout.addLayout(self.radioLayout2)
            label_run = QLabel("是否运行多次:")
            self.radioLayout2.addWidget(label_run)
            # label_run.setGeometry(30, 90, 80, 30)
            self.radio_button_run = QButtonGroup()
            self.radio_button_run.setExclusive(True)
            self.radio_button_run_true = QRadioButton("是")
            self.radioLayout2.addWidget(self.radio_button_run_true)
            # radio_button_run_true.setGeometry(110, 90, 80, 30)
            self.radio_button_run.addButton(self.radio_button_run_true)
            self.radio_button_run_false = QRadioButton("否")
            self.radioLayout2.addWidget(self.radio_button_run_false)
            self.radioLayout2.addStretch()
            # radio_button_run_false.setGeometry(170, 90, 80, 30)
            self.radio_button_run_false.setChecked(True)  # 默认是只运行一次
            self.radio_button_run.addButton(self.radio_button_run_false)
            
            # 选择运行次数部分
            self.spin_box = QSpinBox()  # 数字选择框
            self.mainLayout.addWidget(self.spin_box)
            # spin_box.setGeometry(30, 180, 50, 30)
            self.spin_box.setMinimum(0)  # 设置最小值
            self.spin_box.setMaximum(100)  # 设置最大值
            self.spin_box.setValue(1)  # 设置默认值
            self.spin_box.hide()  # 默认是运行一次,所以先隐藏
            
            self.radio_button_run.buttonClicked.connect(self.on_run_click)
            # 创建生成障碍物按钮
            self.button_generate_obstacle = QPushButton("开始规划")
            # self.button_generate_obstacle.setGeometry(90, 180, 120, 30)  # 设置按钮位置和大小

            self.label_notice = QLabel("")
            self.mainLayout.addWidget(self.label_notice)
            # label_notice.setGeometry(80, 210, 150, 30)  # 设置标签位置和大小
            

            self.add_button()

        def on_result_click(self, button):
            if button == self.radio_button_result_true:
                select_folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
                self.label_path.setText(select_folder)
                self.line_edit_result.show()
            else:
                self.line_edit_result.hide()

        def on_run_click(self, button):
            if button == self.radio_button_run_true:
                self.spin_box.show()
            else:
                self.spin_box.hide()

        def add_radio_buttons(self):
            
            self.radio_button_result_true = QRadioButton("是")
            self.radioLayout1.addWidget(self.radio_button_result_true)
            # radio_button_result_true.setGeometry(110, 60, 80, 30)
            self.radio_button_result.addButton(self.radio_button_result_true)

            self.radio_button_result_false = QRadioButton("否")
            self.radioLayout1.addWidget(self.radio_button_result_false)
            # radio_button_result_false.setGeometry(170, 60, 80, 30)
            self.radio_button_result_false.setChecked(True)  # 默认是不保存结果
            self.radio_button_result.addButton(self.radio_button_result_false)

            self.radioLayout1.addStretch()


        def add_button(self):
            button = QPushButton('运行')
            button.clicked.connect(self.run_algorithm)
            self.mainLayout.addWidget(button)

        def start_plan(self, algorithm_instance):
            self.pygame_widget.result = None
            self.pygame_widget.result, self.pygame_widget.time = algorithm_instance.plan(self.pygame_widget.plan_surface)
            track = []
            for point in self.pygame_widget.result:
                track.append((point.x, point.y))
            return track, self.pygame_widget.time

        def run_algorithm(self):
            # 检测路径是否合法
            if self.radio_button_result_true.isChecked() and self.label_path.text() == "":
                self.label_notice.setText("请选择文件!")
                self.radio_button_result_false.setChecked(True)
                return
            # 获取循环次数
            if self.radio_button_run_true.isChecked():
                spin_box_value = self.spin_box.value()
            else:
                spin_box_value = 1
            for i in range(spin_box_value):
                track = []  # 算法执行所得的路径
                time = None  # 算法花费的时间

                selected_algorithm_index = self.algorithmComboBox.currentIndex()
                selected_algorithm_class = self.algorithm_classes[selected_algorithm_index]
                algorithm_instance = selected_algorithm_class(self.pygame_widget)
                track, time = self.start_plan(algorithm_instance)

                self.label_notice.setText("正在规划路径！")
                # 保存结果部分
                if self.radio_button_result_true.isChecked():
                    filepath = self.label_path.text()+"/"+self.line_edit_result.text()+str(i)+".txt"
                    self.pygame_widget.save_result(time1=time, track=track, file_path=filepath)
