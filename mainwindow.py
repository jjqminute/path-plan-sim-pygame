import re
import os
import importlib
import threading
import matplotlib.pyplot as plt

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication, QFileDialog, QLineEdit, QLabel, QSlider, \
    QCheckBox, QButtonGroup, QRadioButton, QPushButton, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from algorithmlist import AlgorithmList

from mappygame import PygameWidget
from result import load_demo, Category_Demo, Category_Compare

from selectalgorithmwindow import SelectAlgorithmWindow # 选择算法窗口类
from analyticalplanningwindow import AnalyticalPlanningWindow
from randomob import RandomOb
from argumentob import ArgumentOb
from graphob import GraphOb
from inputstartandend import InputStartAndEnd
from modifymap import ModifyMap

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

class MainWindow(QMainWindow):
    windows = []  # 存储所有创建的窗口实例
    def __init__(self):
        super().__init__()
        self.loginWindow_new = None
        self.pygame_widget = PygameWidget(self)
        self.init_ui()

    def init_ui(self):
        self.setObjectName("MainWindow")
        self.resize(1050, 850)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./img/logo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(1050, 850))
        self.setMaximumSize(QtCore.QSize(1050, 850))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.text_result = QtWidgets.QTextBrowser(self.centralwidget)
        self.text_result.setGeometry(QtCore.QRect(40, 500, 921, 251))
        self.text_result.setObjectName("text_result")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 20, 921, 450))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1006, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_5 = QtWidgets.QMenu(self.menubar)
        self.menu_5.setObjectName("menu_5")
        # 添加新的工具栏
        self.menu_ob = QtWidgets.QMenu(self.menubar)
        self.menu_ob.setObjectName("menu_ob")
        self.menu_startAndEnd = QtWidgets.QMenu(self.menubar)
        self.menu_startAndEnd.setObjectName("menu_startAndEnd")
        self.menu_map = QtWidgets.QMenu(self.menubar)
        self.menu_map.setObjectName("menu_map")
        self.menu_plan = QtWidgets.QMenu(self.menubar)
        self.menu_plan.setObjectName("menu_plan")
        self.menu_display = QtWidgets.QMenu(self.menubar)
        self.menu_display.setObjectName("menu_display")

        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.toolBar.setMovable(False)  # 设置工具栏为不可移动
        self.actionLoadTest = QtWidgets.QAction(self)
        self.actionLoadTest.setObjectName("actionLoadTest")
        self.actionExit = QtWidgets.QAction(self)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.triggered.connect(self.loginOut)
        self.actionOpen = QtWidgets.QAction(self)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.triggered.connect(self.pygame_widget.open_map)

        self.actionCreate = QtWidgets.QAction(self)
        self.actionCreate.setObjectName("actionCreate")
        # 点击菜单连接方法
        self.actionCreate.triggered.connect(self.openNewWindow)
        # 点击菜单退出方法
        self.actionExit.triggered.connect(self.loginOut)
        self.actionSave = QtWidgets.QAction(self)
        self.actionSave.setObjectName("actionSave")
        # 保存地图的方法
        self.actionSave.triggered.connect(self.pygame_widget.save_map)
        self.createArithmetic = QtWidgets.QAction(self)
        self.createArithmetic.setObjectName("createArithmetic")
        self.createArithmetic.triggered.connect(self.openArithmeticList)
        self.actionVersion = QtWidgets.QAction(self)
        self.actionVersion.setObjectName("actionVersion")
        # 版本信息弹出框链接
        self.actionVersion.triggered.connect(self.versionInformation)
        self.actionhelp = QtWidgets.QAction(self)
        self.actionhelp.setObjectName("actionhelp")
        # 帮助手册弹出框链接
        self.actionhelp.triggered.connect(self.helpInfo)
        self.actionmodel = QtWidgets.QAction(self)
        self.actionmodel.setObjectName("actionmodel")

        # 下载地图模板
        self.actionArithmeticList = QtWidgets.QAction(self)
        self.actionArithmeticList.setObjectName("actionArithmeticList")
        self.actionArithmeticList.triggered.connect(self.openArithmeticList)

        # 随机障碍物
        self.action_random = QtWidgets.QAction(self)
        self.action_random.setObjectName("action_random")
        self.action_random.triggered.connect(self.open_randomOb)
        # 参数障碍物
        self.action_canshu = QtWidgets.QAction(self)
        self.action_canshu.setObjectName("action_canshu")
        self.action_canshu.triggered.connect(self.open_modifyOb)
        # 图形障碍物
        self.action_graph = QtWidgets.QAction(self)
        self.action_graph.setObjectName("action_graph")
        self.action_graph.triggered.connect(self.select_graph)
        # 随机起始点
        self.action_randomPoint = QtWidgets.QAction(self)
        self.action_randomPoint.setObjectName("action_randomPoint")
        self.action_randomPoint.triggered.connect(self.pygame_widget.generateRandomStart)
        # 输入起始点
        self.action_input = QtWidgets.QAction(self)
        self.action_input.setObjectName("action_input")
        self.action_input.triggered.connect(self.startAndEnd)
        # 清空地图
        self.action_empty = QtWidgets.QAction(self)
        self.action_empty.setObjectName("action_empty")
        self.action_empty.triggered.connect(self.pygame_widget.clear_map)
        # 调整栅格大小
        self.action_mapModify = QtWidgets.QAction(self)
        self.action_mapModify.setObjectName("action_mapModify")
        self.action_mapModify.triggered.connect(self.modify_map)
        # 路径规划
        self.action_plan = QtWidgets.QAction(self)
        self.action_plan.setObjectName("action_plan")
        self.action_plan.triggered.connect(self.select_method)
        # 分析规划
        self.action_analyse = QtWidgets.QAction(self)
        self.action_analyse.setObjectName("action_analyse")
        self.action_analyse.triggered.connect(self.open_start_path)
        # 获取图形
        self.action_get = QtWidgets.QAction(self)
        self.action_get.setObjectName("action_get")
        self.action_get.triggered.connect(self.pygame_widget.get_obs_vertices)
        # 栅格化地图
        self.action_rasterization = QtWidgets.QAction(self)
        self.action_rasterization.setObjectName("action_rasterization")
        self.action_rasterization.triggered.connect(self.pygame_widget.rasterize_map)
        self.menu.addAction(self.actionCreate)
        self.menu.addAction(self.actionOpen)
        self.menu.addAction(self.actionSave)
        self.menu.addAction(self.createArithmetic)
        self.menu.addAction(self.actionmodel)
        self.menu.addAction(self.actionArithmeticList)
        self.menu_5.addAction(self.actionExit)
        self.menu_5.addAction(self.actionVersion)
        self.menu_5.addAction(self.actionhelp)
        self.menu_ob.addAction(self.action_random)
        self.menu_ob.addAction(self.action_canshu)
        self.menu_ob.addAction(self.action_graph)
        self.menu_startAndEnd.addAction(self.action_randomPoint)
        self.menu_startAndEnd.addAction(self.action_input)
        self.menu_map.addAction(self.action_empty)
        self.menu_map.addAction(self.action_mapModify)
        self.menu_plan.addAction(self.action_plan)
        self.menu_plan.addAction(self.action_analyse)
        self.menu_plan.addAction(self.action_get)
        self.menu_plan.addAction(self.action_rasterization)
        # 添加工具栏中选项卡
        self.select_action1 = self.menu_display.addAction("路径规划")
        self.select_action1.setCheckable(True)
        self.select_action1.triggered.connect(lambda:self.add_tool(0))

        self.select_action2 = self.menu_display.addAction("分析规划")
        self.select_action2.setCheckable(True)
        self.select_action2.triggered.connect(lambda: self.add_tool(1))

        self.select_action3 = self.menu_display.addAction("获取图形")
        self.select_action3.setCheckable(True)
        self.select_action3.triggered.connect(lambda: self.add_tool(2))

        self.select_action4 = self.menu_display.addAction("地图栅格化")
        self.select_action4.setCheckable(True)
        self.select_action4.triggered.connect(lambda: self.add_tool(3))

        self.select_action5 = self.menu_display.addAction("清空地图")
        self.select_action5.setCheckable(True)
        self.select_action5.triggered.connect(lambda: self.add_tool(4))

        self.select_action6 = self.menu_display.addAction("随机起始点")
        self.select_action6.setCheckable(True)
        self.select_action6.triggered.connect(lambda: self.add_tool(5))

        self.select_action7 = self.menu_display.addAction("输入起始点")
        self.select_action7.setCheckable(True)
        self.select_action7.triggered.connect(lambda: self.add_tool(6))

        self.select_action8 = self.menu_display.addAction("图形障碍物")
        self.select_action8.setCheckable(True)
        self.select_action8.triggered.connect(lambda: self.add_tool(7))

        self.select_action9 = self.menu_display.addAction("参数障碍物")
        self.select_action9.setCheckable(True)
        self.select_action9.triggered.connect(lambda: self.add_tool(8))

        self.select_action10 = self.menu_display.addAction("随机障碍物")
        self.select_action10.setCheckable(True)
        self.select_action10.triggered.connect(lambda: self.add_tool(9))

        self.select_action11 = self.menu_display.addAction("调整栅格")
        self.select_action11.setCheckable(True)
        self.select_action11.triggered.connect(lambda: self.add_tool(10))

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_ob.menuAction())
        self.menubar.addAction(self.menu_startAndEnd.menuAction())
        self.menubar.addAction(self.menu_map.menuAction())
        self.menubar.addAction(self.menu_plan.menuAction())
        self.menubar.addAction(self.menu_display.menuAction())
        self.menubar.addAction(self.menu_5.menuAction())

        self.toolBar.addAction(self.actionCreate)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionmodel)
        self.toolBar.addAction(self.actionExit)

        self.toolBar.addAction(self.actionCreate)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionmodel)
        self.toolBar.addAction(self.actionhelp)
        self.toolBar.addAction(self.actionArithmeticList)
        self.toolBar.addAction(self.actionExit)
        # 侧边栏
        self.sideToolBar = QtWidgets.QToolBar(self)
        self.sideToolBar.setObjectName("sideToolBar")
        # self.sideToolBar.setMovable(False)  # 设置工具栏为不可移动
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.sideToolBar)
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.layout.addWidget(self.pygame_widget)



    # 起始点输入窗口
    # def input_startAndEnd(self, MainWindow, pygame_widget):
    #     self.loginWindow_new = None
    #     MainWindow.setObjectName("地图起始点")
    #     MainWindow.setFixedSize(300, 160)
    #     # 创建起点标签
    #     self.label_start = QLabel("起点:", MainWindow)
    #     self.label_start.setGeometry(10, 20, 80, 30)  # 设置标签位置和大小
    #     # 创建第一个输入框
    #     self.lineEdit1 = QLineEdit(MainWindow)
    #     self.lineEdit1.setGeometry(80, 20, 200, 30)  # 设置输入框位置和大小
    #     self.lineEdit1.setPlaceholderText("请输入起点（x，y）")  # 设置提示文字
    #     # 创建起点标签
    #     self.label_end = QLabel("终点:", MainWindow)
    #     self.label_end.setGeometry(10, 60, 80, 30)  # 设置标签位置和大小
    #     # 创建第一个输入框
    #     self.lineEdit2 = QLineEdit(MainWindow)
    #     self.lineEdit2.setGeometry(80, 60, 200, 30)  # 设置输入框位置和大小
    #     self.lineEdit2.setPlaceholderText("请输入起点（x，y）")  # 设置提示文字
    #
    #     # 创建生成起始点按钮
    #     self.button_modify = QPushButton("生成", MainWindow)
    #     self.button_modify.setGeometry(120, 100, 60, 30)  # 设置按钮位置和大小
    #     label_notice = QLabel("", MainWindow)
    #     label_notice.setGeometry(100, 120, 150, 30)  # 设置标签位置和大小
    #
    #     def on_button_click():
    #         start = self.lineEdit1.text()
    #         end = self.lineEdit2.text()
    #
    #         # TODO 起始点坐标获取以及调用方法未完成
    #         if not start and not end:
    #             label_notice.setText("请输入起始点坐标！")
    #             return
    #
    #         print(start)
    #         pattern = r"\((\d+),(\d+)\)"  # 匹配坐标的正则表达式模式
    #         match = re.match(pattern, start)
    #         print(match)
    #         if match:
    #             keyx = int(match.group(1))  # 提取横坐标
    #             keyy = int(match.group(2))  # 提取纵坐标
    #             print("起点横坐标:", keyx)
    #             print("起点纵坐标:", keyy)
    #             pygame_widget.painting_ori(keyx, keyy)  # 目前执行到这里程序就结束了，应该是调用有问题
    #         else:
    #             print("坐标格式不正确")
    #         match_2 = re.match(pattern, end)
    #         if match_2:
    #             # global keyx_2, keyy_2
    #             keyx_2 = int(match_2.group(1))  # 提取横坐标
    #             keyy_2 = int(match_2.group(2))  # 提取纵坐标
    #             print("终点横坐标:", keyx_2)
    #             print("终点纵坐标:", keyy_2)
    #             pygame_widget.painting_end(keyx_2, keyy_2)
    #         else:
    #             print("坐标格式不正确")
    #         label_notice.setText("输入起始点生成成功！")
    #     # 连接按钮的点击信号
    #     self.button_modify.clicked.connect(on_button_click)


    # 常用工具栏动态添加
    def add_tool(self,index):
        if index == 0:
            if self.select_action1.isChecked():
                self.sideToolBar.addAction(self.action_plan)
            else:
                self.sideToolBar.removeAction(self.action_plan)
        elif index == 1:
            if self.select_action2.isChecked():
                self.sideToolBar.addAction(self.action_analyse)
            else:
                self.sideToolBar.removeAction(self.action_analyse)
        elif index == 2:
            if self.select_action3.isChecked():
                self.sideToolBar.addAction(self.action_get)
            else:
                self.sideToolBar.removeAction(self.action_get)
        elif index == 3:
            if self.select_action4.isChecked():
                self.sideToolBar.addAction(self.action_rasterization)
            else:
                self.sideToolBar.removeAction(self.action_rasterization)
        elif index == 4:
            if self.select_action5.isChecked():
                self.sideToolBar.addAction(self.action_empty)
            else:
                self.sideToolBar.removeAction(self.action_empty)
        elif index == 5:
            if self.select_action6.isChecked():
                self.sideToolBar.addAction(self.action_randomPoint)
            else:
                self.sideToolBar.removeAction(self.action_randomPoint)
        elif index == 6:
            if self.select_action7.isChecked():
                self.sideToolBar.addAction(self.action_input)
            else:
                self.sideToolBar.removeAction(self.action_input)
        elif index == 7:
            if self.select_action8.isChecked():
                self.sideToolBar.addAction(self.action_graph)
            else:
                self.sideToolBar.removeAction(self.action_graph)
        elif index == 8:
            if self.select_action9.isChecked():
                self.sideToolBar.addAction(self.action_canshu)
            else:
                self.sideToolBar.removeAction(self.action_canshu)
        elif index == 9:
            if self.select_action10.isChecked():
                self.sideToolBar.addAction(self.action_random)
            else:
                self.sideToolBar.removeAction(self.action_random)
        elif index == 10:
            if self.select_action11.isChecked():
                self.sideToolBar.addAction(self.action_mapModify)
            else:
                self.sideToolBar.removeAction(self.action_mapModify)

    # 图形障碍物窗口
    def select_graph(self):
        select_algorithm_window = GraphOb(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中
    # 随机障碍物窗口
    def open_randomOb(self):
        select_algorithm_window = RandomOb(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中

    # 随机障碍物窗口
    def startAndEnd(self):
        select_algorithm_window = InputStartAndEnd(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中
        # new_window = QtWidgets.QMainWindow()
        # mainWindow.input_startAndEnd(new_window, self.pygame_widget)
        # new_window.setWindowTitle('输入起始点')
        # new_window.show()
        # self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 随机障碍物窗口
    def modify_map(self):
        select_algorithm_window = ModifyMap(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中
    # 路径规划选择算法窗口
    def select_method(self):
        select_algorithm_window = SelectAlgorithmWindow(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中
    # 打开参数障碍物窗口
    def open_modifyOb(self):
        select_algorithm_window = ArgumentOb(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中

        # 打开参数障碍物窗口
    def open_start_path(self):
        analytical_planning_window = AnalyticalPlanningWindow(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        analytical_planning_window.show()
        self.windows.append(analytical_planning_window)



    # 文本框输出提示信息
    def printf(self, msg, x=None, y=None):
        if x is None and y is None:
            self.text_result.append("%s" % msg)
        else:
            self.text_result.append("%s(%d:%d)" % (msg, x, y))

    # 创建新窗口方法
    def openNewWindow(self):
        sub_window = SubWindow()
        # sub_window.setWindowTitle('基于Pygame的路径规划算法仿真平台')
        sub_window.show()
        self.windows.append(sub_window)  # 将新创建的窗口实例添加到列表中

    # 退出登录
    def loginOut(self):
        self.MainWindow.hide()
        # TODO 退出功能的实现，退出时问用户是否保存地图数据

    # 版本信息弹出框 TODO 需要更改
    def versionInformation(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("基于Pygame的路径规划算法仿真平台V1.0")
        message_box.setText(
            "路径规划算法仿真平台可以帮助实际应用中的路径规划问题，如无人车、无人机、物流配送等领域的规划和优化。通过仿真平台，可以提前预测和分析路径规划算法在实际环境中的表现，从而减少实际试验的成本和风险。同时，仿真平台还可以为实际应用中的路径规划算法提供实时的优化和调整，以满足不同场景和需求的要求。"
            "路径规划仿真平台V1.0版本是指一种软件工具，可以模拟路径，通过路径规划算法计算最优路径，并可视化显示路径和相关参数。用户可以通过输入环境地图和调整参数等方式，对仿真平台进行操作和控制。")
        message_box.setIcon(QMessageBox.Information)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.button(QMessageBox.Ok).setFixedSize(100, 40)  # 设置按钮尺寸
        message_box.setFixedSize(800, 800)  # 设置提示框尺寸

        message_box.exec()

    # 帮助信息提示 TODO 需要更改
    def helpInfo(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("基于Pygame的路径规划算法仿真平台V1.0帮助手册")
        message_box.setText(
            "路径规划仿真平台V1.0版本是指一种软件工具，可以模拟路径，通过路径规划算法计算最优路径，并可视化显示路径和相关参数。用户可以通过输入环境地图和调整参数等方式，对仿真平台进行操作和控制。"
            "仿真平台的使用：本平台使用手动设置起点、终点与障碍点的位置，通过鼠标左键设置障碍点，鼠标右键点击第一次为红色起点点击第二次为绿色终点，地图是可以实时清空和刷新的，只要用户对地图进行改变"
            "平台就会自动刷新，并且本平台采用可以手动调整地图的粒度大小的，但是建议用户采用的地图粒度大小在10-50区间为最佳效果。")
        message_box.setIcon(QMessageBox.Information)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.button(QMessageBox.Ok).setFixedSize(100, 40)  # 设置按钮尺寸
        message_box.setFixedSize(800, 800)  # 设置提示框尺寸
        message_box.exec()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "基于Pygame的路径规划算法仿真平台"))
        # self.pushButton.setText(_translate("MainWindow", "清空地图"))
        self.text_result.setPlaceholderText(_translate("MainWindow", "输出路径规划结果"))
        self.text_result.append(
            "欢迎来到基于Pygame的路径规划算法仿真平台，以下是路径规划的结果仅供大家参考（右键按第一次是起点第二次是终点，左键设置起点）：")
        self.text_result.append("红色为起点、绿色为终点、黑色为障碍点，平台具体方法请点击帮助手册查看！")
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.menu_5.setTitle(_translate("MainWindow", "关于"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionLoadTest.setText(_translate("MainWindow", "压力测试"))
        self.actionExit.setText(_translate("MainWindow", "退出"))
        self.actionOpen.setText(_translate("MainWindow", "打开文件"))
        self.actionCreate.setText(_translate("MainWindow", "新建窗口"))
        self.actionSave.setText(_translate("MainWindow", "保存地图"))
        self.createArithmetic.setText(_translate("MainWindow", "新增算法"))
        self.actionVersion.setText(_translate("MainWindow", "版本信息"))
        self.actionhelp.setText(_translate("MainWindow", "帮助手册"))
        self.actionmodel.setText(_translate("MainWindow", "下载地图模板"))
        self.actionArithmeticList.setText(_translate("MainWindow", "算法列表"))
        self.menu_ob.setTitle(_translate("MainWindow", "障碍物设置"))
        self.menu_startAndEnd.setTitle(_translate("MainWindow", "起始点设置"))
        self.menu_map.setTitle(_translate("MainWindow", "地图设置"))
        self.menu_plan.setTitle(_translate("MainWindow", "路径规划"))
        self.menu_display.setTitle(_translate("MainWindow", "常用工具栏"))
        self.action_random.setText(_translate("MainWindow", "随机障碍物"))
        self.action_canshu.setText(_translate("MainWindow", "参数障碍物"))
        self.action_graph.setText(_translate("MainWindow", "图形障碍物"))
        self.action_randomPoint.setText(_translate("MainWindow", "随机起始点"))
        self.action_input.setText(_translate("MainWindow", "输入起始点"))
        self.action_empty.setText(_translate("MainWindow", "清空地图"))
        self.action_mapModify.setText(_translate("MainWindow", "调整栅格"))
        self.action_plan.setText(_translate("MainWindow", "路径规划"))
        self.action_analyse.setText(_translate("MainWindow", "分析规划"))
        self.action_get.setText(_translate("MainWindow", "获取图形"))
        self.action_rasterization.setText(_translate("MainWindow", "栅格化"))
    
    def start_plan(self, algorithm_instance):
        self.pygame_widget.result = None
        self.pygame_widget.result,time = algorithm_instance(self).plan(self.pygame_widget.plan_surface)
        track = []
        for point in self.pygame_widget.result:
            track.append((point.x, point.y))
        return track, time

    def ori_end_input(self):  # 输入起始点终点函数
        coordinate = self.text_input.text()
        print(coordinate)
        pattern = r"\((\d+),(\d+)\)"  # 匹配坐标的正则表达式模式
        match = re.match(pattern, coordinate)
        print(match)
        if match:
            keyx = int(match.group(1))  # 提取横坐标
            keyy = int(match.group(2))  # 提取纵坐标
            print("起点横坐标:", keyx)
            print("起点纵坐标:", keyy)
            self.pygame_widget.painting_ori(keyx, keyy)  # 目前执行到这里程序就结束了，应该是调用有问题
        else:
            print("坐标格式不正确")
        coordinate_2 = self.text_input_2.text()
        # print(coordinate_2)
        pattern_2 = r"\((\d+),(\d+)\)"  # 匹配坐标的正则表达式模式
        match_2 = re.match(pattern, coordinate_2)
        if match_2:
            # global keyx_2, keyy_2
            keyx_2 = int(match_2.group(1))  # 提取横坐标
            keyy_2 = int(match_2.group(2))  # 提取纵坐标
            print("终点横坐标:", keyx_2)
            print("终点纵坐标:", keyy_2)
            self.pygame_widget.painting_end(keyx_2, keyy_2)
        else:
            print("坐标格式不正确")

    def openArithmeticList(self):
        self.algorithm_list = AlgorithmList()
        self.algorithm_list.show()

# 子窗口类
class SubWindow(MainWindow):
    def __init__(self):
        super().__init__()

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
