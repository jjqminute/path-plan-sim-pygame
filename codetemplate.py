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
class AnalyticalPlanningWindow(QMainWindow):
    def __init__(self, pygame_widget):
        super().__init__()
        self.pygame_widget = pygame_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('分析规划')
        self.setGeometry(100, 100, 400, 300)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)
