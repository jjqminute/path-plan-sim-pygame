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

        self.select_action11 = self.menu_display.addAction("地图栅格大小调整")
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

    # 参数障碍物窗口 根据用户选择生成相同大小障碍物
    def modify_obstacles(self, MainWindow, pygame_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(400, 300) # 窗口大小锁定
        # 创建障碍物数量标签
        self.label_sum = QLabel("障碍物数量:", MainWindow)
        self.label_sum.setGeometry(60, 50, 80, 30)  # 设置标签位置和大小
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit(MainWindow)
        self.lineEdit1.setGeometry(140, 50, 200, 30)  # 设置输入框位置和大小
        self.lineEdit1.setPlaceholderText("请输入障碍物的数量")  # 设置提示文字

        # 创建障碍物大小标签
        label_size = QLabel("障碍物大小:", MainWindow)
        label_size.setGeometry(60, 100, 80, 30)  # 设置标签位置和大小
        # # 创建第二个输入框
        # self.lineEdit2 = QLineEdit(MainWindow)
        # self.lineEdit2.setGeometry(140, 100, 200, 30)  # 设置输入框位置和大小
        # self.lineEdit2.setPlaceholderText("迭代次数")  # 设置提示文字
        # 创建障碍物大小滑块
        slider = QSlider(MainWindow)
        slider.setGeometry(140, 100, 200, 30)  # 设置滑块位置和大小
        slider.setMinimum(5)  # 设置最小值
        slider.setMaximum(200)  # 设置最大值
        slider.setOrientation(Qt.Horizontal)  # 设置水平方向
        # 创建标签用于显示滑块的值
        label_slider_value = QLabel("5", MainWindow)
        label_slider_value.setGeometry(350, 100, 40, 30)  # 设置标签位置和大小

        # 连接滑块数值改变的信号和槽
        slider.valueChanged.connect(lambda value: label_slider_value.setText(str(value)))
        # 创建障碍物大小标签
        label_type = QLabel("障碍物类型:", MainWindow)
        label_type.setGeometry(60, 150, 80, 30)  # 设置标签位置和大小

        # 创建多选框
        checkbox1 = QCheckBox("圆形", MainWindow)
        checkbox1.setGeometry(140, 150, 150, 30)  # 设置多选框位置和大小

        checkbox2 = QCheckBox("正方形", MainWindow)
        checkbox2.setGeometry(210, 150, 150, 30)  # 设置多选框位置和大小

        checkbox3 = QCheckBox("椭圆", MainWindow)
        checkbox3.setGeometry(280, 150, 150, 30)  # 设置多选框位置和大小

        checkbox4 = QCheckBox("菱形", MainWindow)
        checkbox4.setGeometry(140, 180, 150, 30)  # 设置多选框位置和大小

        checkbox5 = QCheckBox("矩形", MainWindow)
        checkbox5.setGeometry(210, 180, 150, 30)  # 设置多选框位置和大小

        # 创建障碍物是否重叠
        label_type = QLabel("障碍物重叠:", MainWindow)
        label_type.setGeometry(60, 210, 80, 30)  # 设置标签位置和大小

        # 创建单选按钮组
        radio_button_group = QButtonGroup(MainWindow)
        radio_button_group.setExclusive(True)  # 设置为互斥，只能选择一个单选按钮
        # 创建是单选按钮
        radio_button_ok = QRadioButton("重叠", MainWindow)
        radio_button_ok.setGeometry(140, 210, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_ok)  # 将单选按钮添加到单选按钮组
        # 创建是单选按钮
        radio_button_no = QRadioButton("分离", MainWindow)
        radio_button_no.setGeometry(210, 210, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_no)  # 将单选按钮添加到单选按钮组

        # 创建生成障碍物按钮
        self.button_generate_obstacle = QPushButton("生成障碍物", MainWindow)
        self.button_generate_obstacle.setGeometry(130, 250, 120, 30)  # 设置按钮位置和大小

        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(140, 15, 150, 30)  # 设置标签位置和大小

        def on_button_click():
            obstacle_quantity = self.lineEdit1.text()
            if not obstacle_quantity:
                label_notice.setText("请输入障碍物数量！")
                return
            obstacle_size = slider.value()
            obstacle_types = []
            if not checkbox1.isChecked() and not checkbox2.isChecked() and not checkbox3.isChecked() and not checkbox4.isChecked() and not checkbox5.isChecked():
                label_notice.setText("请选择至少一种障碍物类型！")
                return
            if checkbox1.isChecked():
                obstacle_types.append(0)
            if checkbox2.isChecked():
                obstacle_types.append(1)
            if checkbox3.isChecked():
                obstacle_types.append(2)
            if checkbox4.isChecked():
                obstacle_types.append(3)
            if checkbox5.isChecked():
                obstacle_types.append(4)
            if not radio_button_ok.isChecked() and not radio_button_no.isChecked():
                label_notice.setText("请选择障碍物是否重叠！")
                return
            if radio_button_ok.isChecked():
                obstacle_overlap = "T"
            elif radio_button_no.isChecked():
                obstacle_overlap = "F"
            pygame_widget.graph_setting(obstacle_quantity, obstacle_size, obstacle_types, obstacle_overlap)
            label_notice.setText("障碍物生成成功！")

        # 连接按钮的点击信号
        self.button_generate_obstacle.clicked.connect(on_button_click)

    # TODO 开始规划选择算法窗口
    def start_path(self, MainWindow, pygame_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(400, 300)
        # 创建障选择算法标签
        self.label_sum = QLabel("规划算法:", MainWindow)
        self.label_sum.setGeometry(60, 50, 80, 30)  # 设置标签位置和大小

        # 创建多选框
        checkbox1 = QCheckBox("A*算法", MainWindow)
        checkbox1.setGeometry(120, 50, 150, 30)  # 设置多选框位置和大小

        checkbox2 = QCheckBox("RRT算法", MainWindow)
        checkbox2.setGeometry(180, 50, 150, 30)  # 设置多选框位置和大小

        checkbox2 = QCheckBox("APF算法", MainWindow)
        checkbox2.setGeometry(250, 50, 150, 30)  # 设置多选框位置和大小
        # 创建是否分析算法结果标签
        self.label_analyse = QLabel("是否分析:", MainWindow)
        self.label_analyse.setGeometry(60, 100, 80, 30)  # 设置标签位置和大小
        # 创建单选按钮组
        radio_button_group = QButtonGroup(MainWindow)
        radio_button_group.setExclusive(True)  # 设置为互斥，只能选择一个单选按钮
        # 创建是单选按钮
        radio_button_ok = QRadioButton("是", MainWindow)
        radio_button_ok.setGeometry(120, 100, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_ok)  # 将单选按钮添加到单选按钮组
        # 创建是单选按钮
        radio_button_no = QRadioButton("否", MainWindow)
        radio_button_no.setGeometry(180, 100, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_no)  # 将单选按钮添加到单选按钮组
        # 创建提示label
        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(100, 250, 120, 30)
        # 单次路径结果比较分析
        button_single = QPushButton("单次路径结果比较分析", MainWindow)
        button_single.setGeometry(10, 10, 150, 30)
        def on_single_click():
            files, _ = QFileDialog.getOpenFileNames(MainWindow, '打开结果文件', '', '结果文件 (*.txt)')
            for index, f in enumerate(files):  # 循环选中的所有文件
                self.open_result_single(index, f)
        button_single.clicked.connect(on_single_click)

        # 多路径比较分析
        button_category = QPushButton("多次路径比较分析", MainWindow)
        button_category.setGeometry(10, 40, 150, 30)
        def on_category_click():
            dialog = QFileDialog()
            dialog.setWindowTitle("选择要进行多次结果分析的文件夹")
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            if dialog.exec_():
                try:
                    category = Category_Demo()  # 创建多结果类
                    category.read_file(dialog.selectedFiles()[0])  # 获取选择的文件夹的路径
                    self.open_result_category(category, dialog.selectedFiles()[0])
                except ValueError as e:
                    label_notice.setText(str(e))
        button_category.clicked.connect(on_category_click)
        # 创建生成障碍物按钮
        self.button_start = QPushButton("开始规划", MainWindow)
        self.button_start.setGeometry(130, 250, 120, 30)  # 设置按钮位置和大小

        # 不同算法性能对比(多个多次路径比较分析)
        button_category_compare = QPushButton("不同算法性能比较", MainWindow)
        button_category_compare.setGeometry(10, 70, 150, 30)
        def on_category_compare_click():
            files, _ = QFileDialog.getOpenFileNames(MainWindow, '选择要进行性能对比的文件', '', '计算结果文件 (*.txt)')
            if files:
                compare = Category_Compare()
                compare.read_category(files)
                self.open_result_category_compare(compare)
        button_category_compare.clicked.connect(on_category_compare_click)


    # 随机障碍物提示输入障碍物数量窗口
    def random_ob(self, MainWindow, pygame_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("随机障碍物")
        MainWindow.setFixedSize(300, 120)
        # 创建障碍物数量标签
        self.label_sum = QLabel("障碍物数量:", MainWindow)
        self.label_sum.setGeometry(10, 20, 80, 30)  # 设置标签位置和大小
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit(MainWindow)
        self.lineEdit1.setGeometry(80, 20, 200, 30)  # 设置输入框位置和大小
        self.lineEdit1.setPlaceholderText("请输入障碍物的数量")  # 设置提示文字
        # 创建生成障碍物按钮
        self.button_generate_obstacle = QPushButton("生成障碍物", MainWindow)
        self.button_generate_obstacle.setGeometry(90, 60, 120, 30)  # 设置按钮位置和大小
        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(90, 90, 150, 30)  # 设置标签位置和大小

        def on_button_click():
            obstacle_quantity = self.lineEdit1.text()
            if not obstacle_quantity:
                label_notice.setText("请输入障碍物数量！")
                return
            pygame_widget.random_graph_new(int(obstacle_quantity))
            label_notice.setText("障碍物生成成功！")
        # 连接按钮的点击信号
        self.button_generate_obstacle.clicked.connect(on_button_click)


    
    

    # 地图栅格大小调整
    def map(self, MainWindow, pygame_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("地图参数")
        MainWindow.setFixedSize(300, 120)
        # 创建障碍物数量标签
        self.label_sum = QLabel("栅格大小:", MainWindow)
        self.label_sum.setGeometry(10, 20, 80, 30)  # 设置标签位置和大小
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit(MainWindow)
        self.lineEdit1.setGeometry(80, 20, 200, 30)  # 设置输入框位置和大小
        self.lineEdit1.setPlaceholderText("请输入栅格大小")  # 设置提示文字
        # 创建生成障碍物按钮
        self.button_modify = QPushButton("调整", MainWindow)
        self.button_modify.setGeometry(90, 60, 60, 30)  # 设置按钮位置和大小
        self.button_default = QPushButton("默认", MainWindow)
        self.button_default.setGeometry(160, 60, 60, 30)  # 设置按钮位置和大小
        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(90, 90, 150, 30)  # 设置标签位置和大小

        def on_button_click():
            obstacle_quantity = self.lineEdit1.text()
            if not obstacle_quantity:
                label_notice.setText("请输入地图栅格大小！")
                return
            try:
                int(obstacle_quantity)
                pygame_widget.modifyMap(int(obstacle_quantity))
            except (ValueError, TypeError):
                label_notice.setText("请输入正确的整型栅格大小！")
                return
            label_notice.setText("栅格大小修改成功！")
        def on_button_default():
            print("默认地图")
        # 连接按钮的点击信号
        self.button_modify.clicked.connect(on_button_click)

    # 起始点输入窗口
    def input_startAndEnd(self, MainWindow, pygame_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("地图起始点")
        MainWindow.setFixedSize(300, 160)
        # 创建起点标签
        self.label_start = QLabel("起点:", MainWindow)
        self.label_start.setGeometry(10, 20, 80, 30)  # 设置标签位置和大小
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit(MainWindow)
        self.lineEdit1.setGeometry(80, 20, 200, 30)  # 设置输入框位置和大小
        self.lineEdit1.setPlaceholderText("请输入起点（x，y）")  # 设置提示文字
        # 创建起点标签
        self.label_end = QLabel("终点:", MainWindow)
        self.label_end.setGeometry(10, 60, 80, 30)  # 设置标签位置和大小
        # 创建第一个输入框
        self.lineEdit2 = QLineEdit(MainWindow)
        self.lineEdit2.setGeometry(80, 60, 200, 30)  # 设置输入框位置和大小
        self.lineEdit2.setPlaceholderText("请输入起点（x，y）")  # 设置提示文字

        # 创建生成起始点按钮
        self.button_modify = QPushButton("生成", MainWindow)
        self.button_modify.setGeometry(120, 100, 60, 30)  # 设置按钮位置和大小
        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(100, 120, 150, 30)  # 设置标签位置和大小

        def on_button_click():
            start = self.lineEdit1.text()
            end = self.lineEdit2.text()

            # TODO 起始点坐标获取以及调用方法未完成
            if not start and not end:
                label_notice.setText("请输入起始点坐标！")
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
                pygame_widget.painting_ori(keyx, keyy)  # 目前执行到这里程序就结束了，应该是调用有问题
            else:
                print("坐标格式不正确")
            match_2 = re.match(pattern, end)
            if match_2:
                # global keyx_2, keyy_2
                keyx_2 = int(match_2.group(1))  # 提取横坐标
                keyy_2 = int(match_2.group(2))  # 提取纵坐标
                print("终点横坐标:", keyx_2)
                print("终点纵坐标:", keyy_2)
                pygame_widget.painting_end(keyx_2, keyy_2)
            else:
                print("坐标格式不正确")
            label_notice.setText("输入起始点生成成功！")
        # 连接按钮的点击信号
        self.button_modify.clicked.connect(on_button_click)

    # 选择图形障碍物生成窗口 单个生成
    def graph_ob(self, MainWindow, pygame_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("图形障碍物")
        MainWindow.setFixedSize(300, 120)
        # 创建起点标签
        self.label_graph = QLabel("障碍物类型:", MainWindow)
        self.label_graph.setGeometry(60, 20, 80, 30)  # 设置标签位置和大小
        # 创建下拉列表
        self.combo_box = QComboBox(MainWindow)
        self.combo_box.setGeometry(130, 20, 120, 30)  # 设置下拉列表位置和大小
        self.combo_box.addItem("矩形")
        self.combo_box.addItem("圆形")
        self.combo_box.addItem("三角形")
        self.combo_box.addItem("椭圆形")
        self.combo_box.addItem("菱形")
        self.combo_box.addItem("五角形")
        # 创建生成障碍物按钮
        self.button_modify = QPushButton("生成", MainWindow)
        self.button_modify.setGeometry(90, 60, 120, 30)  # 设置按钮位置和大小
        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(90, 90, 150, 30)  # 设置标签位置和大小

        # 按钮点击事件处理函数
        def on_button_click():
            selected_index = self.combo_box.currentIndex()
            pygame_widget.paint_random_one(selected_index+1)
            label_notice.setText("障碍物生成成功！")
        # 连接按钮的点击信号到处理函数
        self.button_modify.clicked.connect(on_button_click)

    def result_single(self, MainWindow, pygame_widget, index, f):
        """
        结果分析窗口设计
        :param MainWindow: 当前窗体
        :param pygame_widget: pygame widget
        :param index: 当前是选中的第几个文件，用于调整窗体显示的位置
        :param f: 文件的路径
        :return: None
        """
        MainWindow.setGeometry(100 + 10 * index, 100 + 10 * index, 500, 500)
        r = load_demo(f)
        fig = r.draw_track()  # 路径图片
        canvas = FigureCanvas(fig)  # 用于展示
        button_save_fig = QPushButton("保存图片")
        def on_button_save_fig_click():
            dialog = QFileDialog()
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            # 设置对话框标题
            dialog.setWindowTitle('保存路径图片')
            # 设置文件过滤器
            dialog.setNameFilter('路径图片 (*.png)')
            # 设置默认文件名，包含文件类型后缀
            dialog.setDefaultSuffix('png')
            # 打开文件对话框，并返回保存的文件路径
            file_path, _ = dialog.getSaveFileName(MainWindow, '保存计算结果', '', '路径图片 (*.png)')
            fig.savefig(file_path)
        button_save_fig.clicked.connect(on_button_save_fig_click)
        label_time = QLabel("运行时间是：" + str(r.time), MainWindow)
        label_smoothness = QLabel("路径平滑度是：" + str(r.smoothness), MainWindow)
        label_path_length = QLabel("路径长度是：" + str(r.pathlen), MainWindow)
        button_smoothness = QPushButton("展示曲率")
        def on_button_smoothness_click():
            new_window = QtWidgets.QMainWindow()
            fig_curvature = r.draw_curvature()
            curvature = FigureCanvas(fig_curvature)
            button_save_curvature = QPushButton("保存图片")
            def on_button_save_curvature_click():
                dialog = QFileDialog()
                dialog.setAcceptMode(QFileDialog.AcceptSave)
                # 设置对话框标题
                dialog.setWindowTitle('保存曲率图片')
                # 设置文件过滤器
                dialog.setNameFilter('曲率图片 (*.png)')
                # 设置默认文件名，包含文件类型后缀
                dialog.setDefaultSuffix('png')
                # 打开文件对话框，并返回保存的文件路径
                file_path, _ = dialog.getSaveFileName(MainWindow, '保存曲率', '', '曲率图片 (*.png)')
                fig_curvature.savefig(file_path)
            button_save_curvature.clicked.connect(on_button_save_curvature_click)
            layout_curvature = QVBoxLayout(new_window)
            layout_curvature.addWidget(curvature)
            layout_curvature.addWidget(button_save_curvature)
            new_window.setWindowTitle('曲率展示')
            curvature_widget = QWidget(new_window)
            curvature_widget.setLayout(layout_curvature)
            new_window.setCentralWidget(curvature_widget)
            new_window.show()
            self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
        button_smoothness.clicked.connect(on_button_smoothness_click)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        layout.addWidget(button_save_fig)
        layout.addWidget(label_smoothness)
        layout.addWidget(label_path_length)
        layout.addWidget(label_time)
        layout.addWidget(button_smoothness)
        main_widget = QWidget(MainWindow)
        main_widget.setLayout(layout)
        MainWindow.setCentralWidget(main_widget)
        MainWindow.show()

    def result_category(self, MainWindow, pygame_widget, category, dir_path):
        """
        多次结果分析窗口设计
        :param MainWindow: 窗口
        :param pygame_widget: pygame widget
        :param category: 多次结果类
        :param dir_path: 当前选中的文件夹的路径
        :return: None
        """
        MainWindow.setGeometry(100, 100, 500, 500)
        label_notice = QLabel("当前选中的文件夹是:"+dir_path)
        button_notice = QPushButton("重新选择")

        def on_button_notice_click():  # 重新选择要分析的文件夹
            dialog = QFileDialog()
            dialog.setWindowTitle("选择要进行多次结果分析的文件夹")
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            if dialog.exec_():
                try:
                    nonlocal category  # nonlocal关键字代表想要修改的变量是外部作用域中的变量,而不是一个新的局部变量
                    category = Category_Demo()  # 创建多结果类
                    category.read_file(dialog.selectedFiles()[0])  # 获取选择的文件夹的路径
                    label_notice.setText("当前选中的文件夹是:"+dialog.selectedFiles()[0])
                except ValueError as e:
                    label_notice.setText(str(e))
        button_notice.clicked.connect(on_button_notice_click)
        layout_notice = QHBoxLayout()
        layout_notice.addWidget(label_notice)
        layout_notice.addWidget(button_notice)
        sub_widget = QWidget()
        sub_widget.setLayout(layout_notice)
        button_path_compare = QPushButton("路径叠加")

        def on_button_path_compare_click():
            self.open_result_track_compare(category)
        button_path_compare.clicked.connect(on_button_path_compare_click)
        button_average = QPushButton("求平均值")
        def on_button_average():
            self.open_result_average(category)
        button_average.clicked.connect(on_button_average)
        layout = QVBoxLayout()
        layout.addWidget(sub_widget)
        layout.addWidget(button_path_compare)
        layout.addWidget(button_average)
        main_widget = QWidget(MainWindow)
        main_widget.setLayout(layout)
        MainWindow.setCentralWidget(main_widget)
        MainWindow.show()

    def result_category_average(self, MainWindow, pygame_widget, category):
        """
        多结果分析求平均值窗口设计
        :param category:
        :return:
        """
        MainWindow.setGeometry(100, 100, 500, 500)
        label_smooth = QLabel("平均平滑度是："+str(category.ave_smooth))
        label_time = QLabel("平均时间是："+str(category.ave_time))
        label_path_length = QLabel("平均路径长度是："+str(category.ave_path_length))
        textbox_name = QLineEdit("")
        textbox_name.setPlaceholderText("请输入算法名称")
        button_save = QPushButton("保存结果")

        def on_button_save_click():
            dialog = QFileDialog()
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            # 设置对话框标题
            dialog.setWindowTitle('保存category')
            # 设置文件过滤器
            dialog.setNameFilter('category文件 (*.txt)')
            # 设置默认文件名，包含文件类型后缀
            dialog.setDefaultSuffix('txt')
            # 打开文件对话框，并返回保存的文件路径
            file_path, _ = dialog.getSaveFileName(MainWindow, '保存计算结果', '', '计算结果文件 (*.txt)')
            category.save_file(file_path, textbox_name.text())
        button_save.clicked.connect(on_button_save_click)
        layout = QVBoxLayout()
        layout.addWidget(label_time)
        layout.addWidget(label_path_length)
        layout.addWidget(label_smooth)
        layout.addWidget(textbox_name)
        layout.addWidget(button_save)
        main_widget = QWidget(MainWindow)
        main_widget.setLayout(layout)
        MainWindow.setCentralWidget(main_widget)

    def result_category_compare(self, MainWindow, pygame_widget, compare):
        MainWindow.setGeometry(100, 100, 500, 500)
        button_image = QPushButton("对比结果生成图片")
        def on_button_image_click():
            dialog = QFileDialog()
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            dialog.setWindowTitle('保存表格')
            dialog.setDefaultSuffix('png')
            file_path, _ = dialog.getSaveFileName(MainWindow, '保存表格', '', '(*.png)')
            compare.save_image(file_path)
        button_image.clicked.connect(on_button_image_click)
        button_csv = QPushButton("对比结果生成csv")
        def on_button_csv_clink():
            dialog = QFileDialog()
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            dialog.setWindowTitle('保存表格')
            dialog.setDefaultSuffix('csv')
            file_path, _ = dialog.getSaveFileName(MainWindow, '保存表格', '', '(*.csv)')
            compare.save_csv(file_path)
        button_csv.clicked.connect(on_button_csv_clink)
        layout = QVBoxLayout()
        layout.addWidget(button_image)
        layout.addWidget(button_csv)
        main_widget = QWidget(MainWindow)
        main_widget.setLayout(layout)
        MainWindow.setCentralWidget(main_widget)

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
        new_window = QtWidgets.QMainWindow()
        mainWindow.graph_ob(new_window, self.pygame_widget)
        new_window.setWindowTitle('图形障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 随机障碍物窗口
    def open_randomOb(self):
        new_window = QtWidgets.QMainWindow()
        mainWindow.random_ob(new_window, self.pygame_widget)
        new_window.setWindowTitle('随机障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    # 随机障碍物窗口
    def startAndEnd(self):
        new_window = QtWidgets.QMainWindow()
        mainWindow.input_startAndEnd(new_window, self.pygame_widget)
        new_window.setWindowTitle('输入起始点')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 随机障碍物窗口
    def modify_map(self):
        new_window = QtWidgets.QMainWindow()
        mainWindow.map(new_window, self.pygame_widget)
        new_window.setWindowTitle('随机障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 路径规划选择算法窗口
    def select_method(self):
        select_algorithm_window = SelectAlgorithmWindow(self.pygame_widget)
        # mainWindow.select_arithmetic(select_algorithm_window, self.pygame_widget)
        select_algorithm_window.show()
        self.windows.append(select_algorithm_window)  # 将新创建的窗口实例添加到列表中
    # 打开参数障碍物窗口
    def open_modifyOb(self):
        new_window = QtWidgets.QMainWindow()
        mainWindow.modify_obstacles(new_window, self.pygame_widget)
        new_window.setWindowTitle('参数障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

        # 打开参数障碍物窗口
    def open_start_path(self):
        new_window = QtWidgets.QMainWindow()
        mainWindow.start_path(new_window, self.pygame_widget)
        new_window.setWindowTitle('规划算法')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    def open_result_single(self, index, f):
        """
        打开单路径分析窗口。在分析路径的窗口里打开。
        :param index:当前的文件是选中的第几个文件，用于调整窗口的位置
        :param f:文件的路径
        :return:None
        """
        new_window = QtWidgets.QMainWindow()
        mainWindow.result_single(new_window, self.pygame_widget, index, f)
        new_window.setWindowTitle('单路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    def open_result_category(self, category, dir_path):
        """
        打开多路径分析窗口。在分析路径的窗口打开。
        :return:
        """
        new_window = QtWidgets.QMainWindow()
        mainWindow.result_category(new_window, self.pygame_widget, category, dir_path)
        new_window.setWindowTitle('多路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    def open_result_track_compare(self, category):
        """
        打开多路径分析中路径叠加的窗口
        :category:多结果
        :return:None
        """
        new_window = QtWidgets.QMainWindow()
        fig = category.track_compare()
        canvas = FigureCanvas(fig)
        button_save_fig = QPushButton("保存路径叠加图片")
        def on_button_save_fig_click():  # 保存路径叠加图片
            dialog = QFileDialog()
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            # 设置对话框标题
            dialog.setWindowTitle('保存路径叠加图片')
            # 设置文件过滤器
            dialog.setNameFilter('路径叠加图片 (*.png)')
            # 设置默认文件名，包含文件类型后缀
            dialog.setDefaultSuffix('png')
            # 打开文件对话框，并返回保存的文件路径
            file_path, _ = dialog.getSaveFileName(new_window, '保存路径叠加图片', '', '路径叠加图片 (*.png)')
            fig.savefig(file_path)
        button_save_fig.clicked.connect(on_button_save_fig_click)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        layout.addWidget(button_save_fig)
        new_window.setCentralWidget(canvas)
        new_window.setWindowTitle('多路径分析')
        main_widget = QWidget(new_window)
        main_widget.setLayout(layout)
        new_window.setCentralWidget(main_widget)
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    def open_result_average(self, category):
        """
        打开多路径分析中计算平均值的窗口
        :param category: 多结果
        :return: None
        """
        new_window = QtWidgets.QMainWindow()
        mainWindow.result_category_average(new_window, self.pygame_widget, category)
        new_window.setWindowTitle('多路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    def open_result_category_compare(self, compare):
        """
        打开多算法比较信息的窗口
        :param compare: 比较信息,包含多个category
        :return: None
        """
        new_window = QtWidgets.QMainWindow()
        mainWindow.result_category_compare(new_window, self.pygame_widget, compare)
        new_window.setWindowTitle('多路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

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
        self.action_mapModify.setText(_translate("MainWindow", "调整地图栅格大小"))
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
