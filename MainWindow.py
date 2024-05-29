import re
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication, QFileDialog, QLineEdit, QLabel, QSlider, \
    QCheckBox, QButtonGroup, QRadioButton, QPushButton
from AlgorithmList import AlgorithmList
from GridWidget import GridWidget
from MapPygame import PygameWidget


class Ui_MainWindow(object):
    windows = []  # 存储所有创建的窗口实例

    # 参数障碍物窗口
    def modify_obstacles(self, MainWindow, grid_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
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
        # 创建滑块
        slider = QSlider(MainWindow)
        slider.setGeometry(140, 100, 200, 30)  # 设置滑块位置和大小
        slider.setMinimum(5)  # 设置最小值
        slider.setMaximum(200)  # 设置最大值
        slider.setOrientation(Qt.Horizontal)  # 设置水平方向

        # 创建标签用于显示滑块的值
        label_slider_value = QLabel("5", MainWindow)
        label_slider_value.setGeometry(125, 100, 40, 30)  # 设置标签位置和大小

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
            grid_widget.graph_setting(obstacle_quantity, obstacle_size, obstacle_types, obstacle_overlap)
            label_notice.setText("障碍物生成成功！")

        # 连接按钮的点击信号
        self.button_generate_obstacle.clicked.connect(on_button_click)

    # TODO 开始规划选择算法窗口
    def start_path(self, MainWindow, grid_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 300)
        print()

    def setupUi(self, MainWindow, grid_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1006, 850)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./img/logo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 850))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 850))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # 横坐标输入框
        self.text_input = QtWidgets.QLineEdit(self.centralwidget)
        self.text_input.setPlaceholderText("输入起始点横纵坐标(x,y):")
        self.text_input.setGeometry(QtCore.QRect(430, 425, 200, 25))
        text = self.text_input.text()
        # 纵坐标输入框
        self.text_input_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.text_input_2.setPlaceholderText("输入终点横纵坐标(x,y):")
        self.text_input_2.setGeometry(QtCore.QRect(640, 425, 200, 25))
        # 清除地图方法图形按钮
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(130, 425, 75, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(grid_widget.clear_map)
        self.text_result = QtWidgets.QTextBrowser(self.centralwidget)
        self.text_result.setGeometry(QtCore.QRect(40, 500, 921, 251))
        self.text_result.setObjectName("text_result")
        # 获取图形按钮
        self.pushButton_new = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_new.setGeometry(QtCore.QRect(40, 425, 75, 25))
        self.pushButton_new.setObjectName("pushButton_new")
        self.grid_widget = grid_widget
        self.pushButton_new.clicked.connect(self.grid_widget.get_obs_vertices)
        # 地图栅格化按钮
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(220, 425, 75, 25))
        self.pushButton_3.setObjectName("pushButton_3")
        # 地图栅格方法
        self.pushButton_3.clicked.connect(self.grid_widget.rasterize_map)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 20, 921, 401))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        # 算法列表
        self.combo_arithmetic = QtWidgets.QComboBox(self.centralwidget)
        self.combo_arithmetic.setGeometry(QtCore.QRect(310, 425, 100, 25))
        self.combo_arithmetic.setObjectName("combo_arithmetic")
        self.combo_arithmetic.addItem("")
        self.combo_arithmetic.addItem("")
        self.combo_arithmetic.addItem("")
        self.combo_arithmetic.addItem("")
        self.combo_arithmetic.addItem("")
        self.combo_arithmetic.addItem("")
        self.combo_arithmetic.addItem("")

        # 选择障碍物图形
        self.combo_arithmetic_obs = QtWidgets.QComboBox(self.centralwidget)
        self.combo_arithmetic_obs.setGeometry(QtCore.QRect(830, 455, 100, 25))
        self.combo_arithmetic_obs.setObjectName("combo_arithmetic_obs")
        self.combo_arithmetic_obs.addItem("")
        self.combo_arithmetic_obs.addItem("")
        self.combo_arithmetic_obs.addItem("")
        self.combo_arithmetic_obs.addItem("")
        self.combo_arithmetic_obs.addItem("")
        self.combo_arithmetic_obs.addItem("")
        self.combo_arithmetic_obs.addItem("")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1006, 23))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_5 = QtWidgets.QMenu(self.menubar)
        self.menu_5.setObjectName("menu_5")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.actionLoadTest = QtWidgets.QAction(MainWindow)
        self.actionLoadTest.setObjectName("actionLoadTest")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.triggered.connect(self.loginOut)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.label_map = QtWidgets.QLabel(self.centralwidget)
        self.label_map.setGeometry(QtCore.QRect(40, 455, 54, 21))
        self.label_map.setObjectName("label_map")
        self.label_map_block = QtWidgets.QLabel(self.centralwidget)
        self.label_map_block.setGeometry(QtCore.QRect(320, 455, 70, 21))
        self.label_map_block.setObjectName("label_map_block")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(85, 455, 51, 21))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setText(str(10))
        # 地图障碍物数量输入框
        self.lineEdit_block = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_block.setGeometry(QtCore.QRect(390, 455, 60, 23))
        self.lineEdit_block.setObjectName("lineEdit_block")
        self.lineEdit_block.setPlaceholderText("请输入障碍物的数量")
        self.lineEdit_block.setText(str(10))
        # 调整地图按钮
        self.btn_modifyMap = QtWidgets.QPushButton(self.centralwidget)
        self.btn_modifyMap.setGeometry(QtCore.QRect(150, 455, 75, 23))
        self.btn_modifyMap.setObjectName("btn_modifyMap")
        # 调整地图的粒度
        self.btn_modifyMap.clicked.connect(lambda: grid_widget.modifyMap(int(self.lineEdit.text())))
        # 默认地图按钮
        self.btn_default = QtWidgets.QPushButton(self.centralwidget)
        self.btn_default.setGeometry(QtCore.QRect(230, 455, 75, 23))
        self.btn_default.setObjectName("btn_default")
        # 恢复地图默认粒度
        # self.btn_default.clicked.connect(grid_widget.defaultMap)
        # 打开地图的方法
        self.actionOpen.triggered.connect(grid_widget.open_map)
        # 输入起始点确认按钮
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(840, 425, 75, 25))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.ori_end_input)
        # 随机障碍物按钮
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(460, 455, 80, 23))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.clicked.connect(lambda: grid_widget.random_graph_new(int(self.lineEdit_block.text())))
        # 随机起始点按钮
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(550, 455, 80, 23))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.clicked.connect(grid_widget.generateRandomStart)
        # 开始规划按钮
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(640, 455, 80, 23))
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.clicked.connect(self.startPath)  # 方法
        self.actionCreate = QtWidgets.QAction(MainWindow)
        self.actionCreate.setObjectName("actionCreate")
        # 点击菜单连接方法
        self.actionCreate.triggered.connect(self.openNewWindow)
        # 点击菜单退出方法
        self.actionExit.triggered.connect(self.loginOut)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        # 保存地图的方法
        self.actionSave.triggered.connect(grid_widget.save_map)
        self.createArithmetic = QtWidgets.QAction(MainWindow)
        self.createArithmetic.setObjectName("createArithmetic")
        self.createArithmetic.triggered.connect(self.openArithmeticList)
        self.actionVersion = QtWidgets.QAction(MainWindow)
        self.actionVersion.setObjectName("actionVersion")
        # 版本信息弹出框链接
        self.actionVersion.triggered.connect(self.versionInformation)
        self.actionhelp = QtWidgets.QAction(MainWindow)
        self.actionhelp.setObjectName("actionhelp")
        # 帮助手册弹出框链接
        self.actionhelp.triggered.connect(self.helpInfo)
        self.actionmodel = QtWidgets.QAction(MainWindow)
        self.actionmodel.setObjectName("actionmodel")
        # 生成单个图形障碍物可控大小
        self.pushButton_paint_rand = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_paint_rand.setGeometry(QtCore.QRect(730, 454, 80, 25))
        self.pushButton_paint_rand.setObjectName("pushButton_paint_rand")
        self.pushButton_paint_rand.clicked.connect(self.grid_widget.paint_random_one)
        # 参数障碍物按钮
        self.pushButton_ob = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_ob.setGeometry(QtCore.QRect(730, 454, 80, 25))
        self.pushButton_ob.setObjectName("pushButton_ob")
        self.pushButton_ob.clicked.connect(self.open_modifyOb)
        # 下载地图模板
        # self.actionmodel.triggered.connect(grid_widget.downLoadModelMap)
        self.actionArithmeticList = QtWidgets.QAction(MainWindow)
        self.actionArithmeticList.setObjectName("actionArithmeticList")
        self.actionArithmeticList.triggered.connect(self.openArithmeticList)
        self.menu.addAction(self.actionCreate)
        self.menu.addAction(self.actionOpen)
        self.menu.addAction(self.actionSave)
        self.menu.addAction(self.createArithmetic)
        self.menu.addAction(self.actionmodel)
        self.menu.addAction(self.actionArithmeticList)
        self.menu_5.addAction(self.actionExit)
        self.menu_5.addAction(self.actionVersion)
        self.menu_5.addAction(self.actionhelp)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_5.menuAction())
        self.toolBar.addAction(self.actionCreate)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionmodel)
        self.toolBar.addAction(self.actionhelp)
        self.toolBar.addAction(self.actionArithmeticList)
        self.toolBar.addAction(self.actionExit)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # self.grid_widget = grid_widget

    # 打开参数障碍物窗口
    def open_modifyOb(self):
        new_window = QtWidgets.QMainWindow()
        ui.modify_obstacles(new_window, self.grid_widget)
        new_window.setWindowTitle('参数障碍物')
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
        new_window = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        pw = PygameWidget(ui)
        ui.setupUi(new_window, pw)

        new_window.setWindowTitle('基于Pygame的路径规划算法仿真平台')
        # 添加地图
        ui.layout.addWidget(pw)
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

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
        self.pushButton.setText(_translate("MainWindow", "清空地图"))
        self.text_result.setPlaceholderText(_translate("MainWindow", "输出路径规划结果"))
        self.text_result.append(
            "欢迎来到基于Pygame的路径规划算法仿真平台，以下是路径规划的结果仅供大家参考（右键按第一次是起点第二次是终点，左键设置起点）：")
        self.text_result.append("红色为起点、绿色为终点、黑色为障碍点，平台具体方法请点击帮助手册查看！")
        self.pushButton_new.setText(_translate("MainWindow", "获取图形"))
        self.pushButton_3.setText(_translate("MainWindow", "地图栅格化"))
        # self.checkBox.setText(_translate("MainWindow", "AStar算法"))
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
        self.label_map.setText(_translate("MainWindow", "分辨率："))
        self.label_map_block.setText(_translate("MainWindow", "随机障碍物："))
        self.btn_modifyMap.setText(_translate("MainWindow", "调整"))
        self.btn_default.setText(_translate("MainWindow", "默认"))
        self.actionArithmeticList.setText(_translate("MainWindow", "算法列表"))
        self.pushButton_4.setText(_translate("MainWindow", "生成"))
        self.pushButton_5.setText(_translate("MainWindow", "随机障碍物"))
        self.pushButton_6.setText(_translate("MainWindow", "随机起始点"))
        self.pushButton_7.setText(_translate("MainWindow", "开始规划"))
        self.combo_arithmetic.setItemText(0, _translate("MainWindow", "请选择算法"))
        self.combo_arithmetic.setItemText(1, _translate("MainWindow", "Astar"))
        self.combo_arithmetic.setItemText(2, _translate("MainWindow", "RRT"))
        self.combo_arithmetic.setItemText(3, _translate("MainWindow", "APF"))
        self.combo_arithmetic.setItemText(4, _translate("MainWindow", "APFRRT"))
        self.combo_arithmetic.setItemText(5, _translate("MainWindow", "MPV"))
        self.combo_arithmetic.setItemText(5, _translate("MainWindow", "PRM"))

        self.combo_arithmetic_obs.setItemText(0, _translate("MainWindow", "图形障碍物"))
        self.combo_arithmetic_obs.setItemText(1, _translate("MainWindow", "矩形"))
        self.combo_arithmetic_obs.setItemText(2, _translate("MainWindow", "圆形"))
        self.combo_arithmetic_obs.setItemText(3, _translate("MainWindow", "三角形"))
        self.combo_arithmetic_obs.setItemText(4, _translate("MainWindow", "椭圆形"))
        self.combo_arithmetic_obs.setItemText(5, _translate("MainWindow", "菱形"))
        self.combo_arithmetic_obs.setItemText(6, _translate("MainWindow", "五角形"))
        self.pushButton_paint_rand.setText(_translate("MainWindow", "图形障碍物"))
        self.pushButton_ob.setText(_translate("MainWindow", "参数障碍物"))

    # 路径规划
    def startPath(self):
        self.grid_widget.plan_surface.fill((255, 255, 255))
        if not self.grid_widget.obstacles or not self.grid_widget.start_point or not self.grid_widget.end_point:
            self.printf("未设置障碍物或起始点或终点")
        # 根据不同的算法
        else:
            if self.combo_arithmetic.currentText() == "Astar":
                self.printf("启动A星算法！！！")
                self.grid_widget.startAstar()
            elif self.combo_arithmetic.currentText() == "RRT":
                self.printf("启动RRT算法！！！")
                self.grid_widget.start_rrt()
            elif self.combo_arithmetic.currentText() == "APF":
                self.printf("启动APF算法！！！")
                self.grid_widget.startApf()
            elif self.combo_arithmetic.currentText() == "APFRRT":
                self.printf("启动APF-RRT算法！！！")
                self.grid_widget.startApfRrt()
            elif self.combo_arithmetic.currentText() == "MPV":
                self.printf("启动MPV算法！！！")
                self.grid_widget.start_mpv()
            elif self.combo_arithmetic.currentText() == "PRM":
                self.printf("启动PRM算法！！！")
                self.grid_widget.startPRm()

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
            pw.painting_ori(keyx, keyy)  # 目前执行到这里程序就结束了，应该是调用有问题
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
            pw.painting_end(keyx_2, keyy_2)
        else:
            print("坐标格式不正确")

    def openArithmeticList(self):
        self.algorithm_list = AlgorithmList()
        self.algorithm_list.show()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    mainWindow = QtWidgets.QMainWindow()
    grid_widget = GridWidget(ui)
    pw = PygameWidget(ui)
    ui.setupUi(mainWindow, pw)
    # 添加地图
    ui.layout.addWidget(pw)
    mainWindow.show()
    sys.exit(app.exec())
