import re
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication, QFileDialog, QLineEdit, QLabel, QSlider, \
    QCheckBox, QButtonGroup, QRadioButton, QPushButton, QComboBox, QSpinBox
from AlgorithmList import AlgorithmList
from GridWidget import GridWidget
from MapPygame import PygameWidget


class Ui_MainWindow(object):
    windows = []  # 存储所有创建的窗口实例

    # 参数障碍物窗口 根据用户选择生成相同大小障碍物
    def modify_obstacles(self, MainWindow, grid_widget):
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
            grid_widget.graph_setting(obstacle_quantity, obstacle_size, obstacle_types, obstacle_overlap)
            label_notice.setText("障碍物生成成功！")

        # 连接按钮的点击信号
        self.button_generate_obstacle.clicked.connect(on_button_click)

    # TODO 开始规划选择算法窗口
    def start_path(self, MainWindow, grid_widget):
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

        # 创建生成障碍物按钮
        self.button_start = QPushButton("开始规划", MainWindow)
        self.button_start.setGeometry(130, 250, 120, 30)  # 设置按钮位置和大小

    # 随机障碍物提示输入障碍物数量窗口
    def random_ob(self, MainWindow, grid_widget):
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
            grid_widget.random_graph_new(int(obstacle_quantity))
            label_notice.setText("障碍物生成成功！")
        # 连接按钮的点击信号
        self.button_generate_obstacle.clicked.connect(on_button_click)

    # 路径规划选择算法
    def select_arithmetic(self, MainWindow, grid_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(300, 250)
        # 创建选择算法标签
        self.label_analyse = QLabel("选择算法:", MainWindow)
        self.label_analyse.setGeometry(30, 30, 80, 30)  # 设置标签位置和大小
        # 创建单选按钮组
        radio_button_group = QButtonGroup(MainWindow)
        radio_button_group.setExclusive(True)  # 设置为互斥，只能选择一个单选按钮
        # 创建A*算法单选按钮
        radio_button_astar = QRadioButton("AStar", MainWindow)
        radio_button_astar.setGeometry(90, 30, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_astar)  # 将单选按钮添加到单选按钮组
        # 创建RRT算法单选按钮
        radio_button_rrt = QRadioButton("RRT", MainWindow)
        radio_button_rrt.setGeometry(150, 30, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_rrt)  # 将单选按钮添加到单选按钮组
        # 创建APF算法单选按钮
        radio_button_apf = QRadioButton("APF", MainWindow)
        radio_button_apf.setGeometry(210, 30, 80, 30)  # 设置单选按钮位置和大小
        radio_button_group.addButton(radio_button_apf)  # 将单选按钮添加到单选按钮组
        # 保存结果部分
        label_result = QLabel("是否保存结果:", MainWindow)
        label_result.setGeometry(30, 60, 80, 30)
        radio_button_result = QButtonGroup(MainWindow)
        radio_button_result.setExclusive(True)
        radio_button_result_true = QRadioButton("是", MainWindow)
        radio_button_result_true.setGeometry(110, 60, 80, 30)
        radio_button_result.addButton(radio_button_result_true)
        radio_button_result_false = QRadioButton("否", MainWindow)
        radio_button_result_false.setGeometry(170, 60, 80, 30)
        radio_button_result_false.setChecked(True)  # 默认是不保存结果
        radio_button_result.addButton(radio_button_result_false)
        # 运行次数部分
        label_run = QLabel("是否运行多次:", MainWindow)
        label_run.setGeometry(30, 90, 80, 30)
        radio_button_run = QButtonGroup(MainWindow)
        radio_button_run.setExclusive(True)
        radio_button_run_true = QRadioButton("是", MainWindow)
        radio_button_run_true.setGeometry(110, 90, 80, 30)
        radio_button_run.addButton(radio_button_run_true)
        radio_button_run_false = QRadioButton("否", MainWindow)
        radio_button_run_false.setGeometry(170, 90, 80, 30)
        radio_button_run_false.setChecked(True)  # 默认是只运行一次
        radio_button_run.addButton(radio_button_run_false)
        # 设置结果文件名称的部分
        label_path = QLabel("",MainWindow)
        label_path.setGeometry(30, 120, 200, 30)
        line_edit_result = QLineEdit("", MainWindow)
        line_edit_result.setPlaceholderText("请输入文件名")
        line_edit_result.setGeometry(90, 150, 120, 30)
        line_edit_result.hide()  # 默认是不保存结果,所以先隐藏
        # 选择运行次数部分
        spin_box = QSpinBox(MainWindow)  # 数字选择框
        spin_box.setGeometry(30, 180, 50, 30)
        spin_box.setMinimum(0)  # 设置最小值
        spin_box.setMaximum(100)  # 设置最大值
        spin_box.setValue(1)  # 设置默认值
        spin_box.hide()  # 默认是运行一次,所以先隐藏
        def on_result_click(button):
            if button == radio_button_result_true:
                select_folder = QFileDialog.getExistingDirectory(MainWindow, "选择文件夹", "")
                label_path.setText(select_folder)
                line_edit_result.show()
            else:
                line_edit_result.hide()
        radio_button_result.buttonClicked.connect(on_result_click)
        def on_run_click(button):
            if button == radio_button_run_true:
                spin_box.show()
            else:
                spin_box.hide()
        radio_button_run.buttonClicked.connect(on_run_click)
        # 创建生成障碍物按钮
        self.button_generate_obstacle = QPushButton("开始规划", MainWindow)
        self.button_generate_obstacle.setGeometry(90, 180, 120, 30)  # 设置按钮位置和大小

        label_notice = QLabel("", MainWindow)
        label_notice.setGeometry(80, 210, 150, 30)  # 设置标签位置和大小

        def on_button_click():
            if not radio_button_astar.isChecked() and not radio_button_rrt.isChecked() and not radio_button_apf.isChecked():
                label_notice.setText("请选择规划路径所用算法！")
                return
            # 检测路径是否合法
            if label_path.text() == "":
                label_notice.setText("请选择文件!")
                radio_button_result_false.setChecked(True)
                return
            # 获取循环次数
            if radio_button_run_true.isChecked():
                spin_box_value = spin_box.value()
            else:
                spin_box_value = 1
            for i in range(spin_box_value):
                track = []  # 算法执行所得的路径
                time = None  # 算法花费的时间
                if radio_button_astar.isChecked():
                    obstacle_overlap = "Astar"
                    track, time = grid_widget.startAstar()
                elif radio_button_rrt.isChecked():
                    obstacle_overlap = "RRT"
                    track, time = grid_widget.startRtt()
                elif radio_button_apf.isChecked():
                    obstacle_overlap = "APF"
                    track, time = grid_widget.startApf()
                label_notice.setText("正在规划路径！")
                # 保存结果部分
                if radio_button_result_true.isChecked():
                    filepath = label_path.text()+"/"+line_edit_result.text()+str(i)+".txt"
                    grid_widget.save_result(time1=time, track=track, file_path=filepath)

        # 连接按钮的点击信号
        self.button_generate_obstacle.clicked.connect(on_button_click)

    # 地图分辨率调整
    def map(self, MainWindow, grid_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("地图参数")
        MainWindow.setFixedSize(300, 120)
        # 创建障碍物数量标签
        self.label_sum = QLabel("分辨率:", MainWindow)
        self.label_sum.setGeometry(10, 20, 80, 30)  # 设置标签位置和大小
        # 创建第一个输入框
        self.lineEdit1 = QLineEdit(MainWindow)
        self.lineEdit1.setGeometry(80, 20, 200, 30)  # 设置输入框位置和大小
        self.lineEdit1.setPlaceholderText("请输入分辨率大小")  # 设置提示文字
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
                label_notice.setText("请输入地图分辨率！")
                return
            grid_widget.modifyMap(int(obstacle_quantity))
            label_notice.setText("分辨率修改成功！")
        def on_button_default():
            print("默认地图")
        # 连接按钮的点击信号
        self.button_modify.clicked.connect(on_button_click)

    # 起始点输入窗口
    def input_startAndEnd(self, MainWindow, grid_widget):
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
                grid_widget.painting_ori(keyx, keyy)  # 目前执行到这里程序就结束了，应该是调用有问题
            else:
                print("坐标格式不正确")
            match_2 = re.match(pattern, end)
            if match_2:
                # global keyx_2, keyy_2
                keyx_2 = int(match_2.group(1))  # 提取横坐标
                keyy_2 = int(match_2.group(2))  # 提取纵坐标
                print("终点横坐标:", keyx_2)
                print("终点纵坐标:", keyy_2)
                grid_widget.painting_end(keyx_2, keyy_2)
            else:
                print("坐标格式不正确")
            label_notice.setText("输入起始点生成成功！")
        # 连接按钮的点击信号
        self.button_modify.clicked.connect(on_button_click)

    # 选择图形障碍物生成窗口 单个生成
    def graph_ob(self, MainWindow, grid_widget):
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
            grid_widget.paint_random_one(selected_index+1)
            label_notice.setText("障碍物生成成功！")
        # 连接按钮的点击信号到处理函数
        self.button_modify.clicked.connect(on_button_click)

    def setupUi(self, MainWindow, grid_widget):
        self.loginWindow_new = None
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 850)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./img/logo.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1100, 850))
        MainWindow.setMaximumSize(QtCore.QSize(1100, 850))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # # 横坐标输入框
        # self.text_input = QtWidgets.QLineEdit(self.centralwidget)
        # self.text_input.setPlaceholderText("输入起始点横纵坐标(x,y):")
        # self.text_input.setGeometry(QtCore.QRect(430, 425, 200, 25))
        # text = self.text_input.text()
        # # 纵坐标输入框
        # self.text_input_2 = QtWidgets.QLineEdit(self.centralwidget)
        # self.text_input_2.setPlaceholderText("输入终点横纵坐标(x,y):")
        # self.text_input_2.setGeometry(QtCore.QRect(640, 425, 200, 25))
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
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 20, 921, 450))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setObjectName("layout")
        # 算法列表
        # self.combo_arithmetic = QtWidgets.QComboBox(self.centralwidget)
        # self.combo_arithmetic.setGeometry(QtCore.QRect(310, 425, 100, 25))
        # self.combo_arithmetic.setObjectName("combo_arithmetic")
        # self.combo_arithmetic.addItem("")
        # self.combo_arithmetic.addItem("")
        # self.combo_arithmetic.addItem("")
        # self.combo_arithmetic.addItem("")
        # self.combo_arithmetic.addItem("")
        # 选择障碍物图形
        # self.combo_arithmetic_obs = QtWidgets.QComboBox(self.centralwidget)
        # self.combo_arithmetic_obs.setGeometry(QtCore.QRect(830, 455, 100, 25))
        # self.combo_arithmetic_obs.setObjectName("combo_arithmetic_obs")
        # self.combo_arithmetic_obs.addItem("")
        # self.combo_arithmetic_obs.addItem("")
        # self.combo_arithmetic_obs.addItem("")
        # self.combo_arithmetic_obs.addItem("")
        # self.combo_arithmetic_obs.addItem("")
        # self.combo_arithmetic_obs.addItem("")
        # self.combo_arithmetic_obs.addItem("")
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
        self.toolBar.setMovable(False)  # 设置工具栏为不可移动


        self.actionLoadTest = QtWidgets.QAction(MainWindow)
        self.actionLoadTest.setObjectName("actionLoadTest")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.triggered.connect(self.loginOut)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        # self.label_map = QtWidgets.QLabel(self.centralwidget)
        # self.label_map.setGeometry(QtCore.QRect(40, 425, 54, 21))
        # self.label_map.setObjectName("label_map")
        # self.label_map_block = QtWidgets.QLabel(self.centralwidget)
        # self.label_map_block.setGeometry(QtCore.QRect(40, 455, 70, 21))
        # self.label_map_block.setObjectName("label_map_block")
        # self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        # self.lineEdit.setGeometry(QtCore.QRect(85, 425, 51, 21))
        # self.lineEdit.setObjectName("lineEdit")
        # self.lineEdit.setText(str(10))
        # 地图障碍物数量输入框
        # self.lineEdit_block = QtWidgets.QLineEdit(self.centralwidget)
        # self.lineEdit_block.setGeometry(QtCore.QRect(105, 455, 60, 23))
        # self.lineEdit_block.setObjectName("lineEdit_block")
        # self.lineEdit_block.setPlaceholderText("请输入障碍物的数量")
        # self.lineEdit_block.setText(str(10))
        # 调整地图按钮
        # self.btn_modifyMap = QtWidgets.QPushButton(self.centralwidget)
        # self.btn_modifyMap.setGeometry(QtCore.QRect(150, 425, 75, 23))
        # self.btn_modifyMap.setObjectName("btn_modifyMap")
        # # 调整地图的粒度
        # self.btn_modifyMap.clicked.connect(lambda: grid_widget.modifyMap(int(self.lineEdit.text())))
        # # 默认地图按钮
        # self.btn_default = QtWidgets.QPushButton(self.centralwidget)
        # self.btn_default.setGeometry(QtCore.QRect(230, 425, 75, 23))
        # self.btn_default.setObjectName("btn_default")
        # 恢复地图默认粒度
        # self.btn_default.clicked.connect(grid_widget.defaultMap)
        # 打开地图的方法
        self.actionOpen.triggered.connect(grid_widget.open_map)
        # 输入起始点确认按钮
        # self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        # self.pushButton_4.setGeometry(QtCore.QRect(840, 425, 75, 25))
        # self.pushButton_4.setObjectName("pushButton_4")
        # self.pushButton_4.clicked.connect(self.ori_end_input)
        # 随机障碍物按钮
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(180, 455, 80, 23))
        self.pushButton_5.setObjectName("pushButton_5")
        # (lambda:grid_widget.random_graph_new(int(self.lineEdit_block.text())))
        self.pushButton_5.clicked.connect(self.open_randomOb)

        # 随机起始点按钮
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(550, 455, 80, 23))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.clicked.connect(grid_widget.generateRandomStart)
        # 分析规划按钮
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(640, 455, 80, 23))
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.clicked.connect(self.open_start_path) # 方法
        # 单路径规划
        self.pushButton_plan = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_plan.setGeometry(QtCore.QRect(640, 455, 80, 23))
        self.pushButton_plan.setObjectName("pushButton_plan")
        self.pushButton_plan.clicked.connect(self.select_method) # 方法
        # 地图调整
        self.pushButton_modify_map = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_modify_map.setGeometry(QtCore.QRect(640, 455, 80, 23))
        self.pushButton_modify_map.setObjectName("pushButton_modify_map")
        self.pushButton_modify_map.clicked.connect(self.modify_map)  # 方法
        # 输入起始点按钮
        self.pushButton_input_startAndEnd = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_input_startAndEnd.setGeometry(QtCore.QRect(640, 455, 80, 23))
        self.pushButton_input_startAndEnd.setObjectName("pushButton_input_startAndEnd")
        self.pushButton_input_startAndEnd.clicked.connect(self.startAndEnd)  # 方法
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
        self.pushButton_paint_rand.clicked.connect(self.select_graph)
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
        # 侧边栏
        self.sideToolBar = QtWidgets.QToolBar(MainWindow)
        self.sideToolBar.setObjectName("sideToolBar")
        # self.sideToolBar.setMovable(False)  # 设置工具栏为不可移动
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.sideToolBar)
        self.sideToolBar.addWidget(self.pushButton_plan)
        self.sideToolBar.addWidget(self.pushButton_7)
        self.sideToolBar.addWidget(self.pushButton_new)
        self.sideToolBar.addWidget(self.pushButton_3)
        self.sideToolBar.addWidget(self.pushButton)
        self.sideToolBar.addWidget(self.pushButton_6)
        self.sideToolBar.addWidget(self.pushButton_input_startAndEnd)
        self.sideToolBar.addWidget(self.pushButton_paint_rand)
        self.sideToolBar.addWidget(self.pushButton_ob)
        self.sideToolBar.addWidget(self.pushButton_5)
        self.sideToolBar.addWidget(self.pushButton_modify_map)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # self.grid_widget = grid_widget
    # 图形障碍物窗口
    def select_graph(self):
        new_window = QtWidgets.QMainWindow()
        ui.graph_ob(new_window, self.grid_widget)
        new_window.setWindowTitle('图形障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 随机障碍物窗口
    def open_randomOb(self):
        new_window = QtWidgets.QMainWindow()
        ui.random_ob(new_window, self.grid_widget)
        new_window.setWindowTitle('随机障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    # 随机障碍物窗口
    def startAndEnd(self):
        new_window = QtWidgets.QMainWindow()
        ui.input_startAndEnd(new_window, self.grid_widget)
        new_window.setWindowTitle('输入起始点')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 随机障碍物窗口
    def modify_map(self):
        new_window = QtWidgets.QMainWindow()
        ui.map(new_window, self.grid_widget)
        new_window.setWindowTitle('随机障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 路径规划选择算法窗口
    def select_method(self):
        new_window = QtWidgets.QMainWindow()
        ui.select_arithmetic(new_window, self.grid_widget)
        new_window.setWindowTitle('仿真算法')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 打开参数障碍物窗口
    def open_modifyOb(self):
        new_window = QtWidgets.QMainWindow()
        ui.modify_obstacles(new_window, self.grid_widget)
        new_window.setWindowTitle('参数障碍物')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

        # 打开参数障碍物窗口
    def open_start_path(self):
        new_window = QtWidgets.QMainWindow()
        ui.start_path(new_window, self.grid_widget)
        new_window.setWindowTitle('规划算法')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中
    # 文本框输出提示信息
    def printf(self, msg, x, y):
        if x is None and y is None:
            self.text_result.append("%s" % msg)
        else:
            self.text_result.append("%s(%d:%d)" % (msg, x, y))

    # 创建新窗口方法
    def openNewWindow(self):
        new_window = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        grid_widget = GridWidget(ui)
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
        # self.label_map.setText(_translate("MainWindow", "分辨率："))
        self.pushButton_plan.setText(_translate("MainWindow", "路径规划"))
        # self.btn_modifyMap.setText(_translate("MainWindow", "调整"))
        # self.btn_default.setText(_translate("MainWindow", "默认"))
        self.actionArithmeticList.setText(_translate("MainWindow", "算法列表"))
        # self.pushButton_4.setText(_translate("MainWindow", "生成"))
        self.pushButton_5.setText(_translate("MainWindow", "随机障碍物"))
        self.pushButton_6.setText(_translate("MainWindow", "随机起始点"))
        self.pushButton_7.setText(_translate("MainWindow", "分析规划"))
        # self.combo_arithmetic.setItemText(0, _translate("MainWindow", "请选择算法"))
        # self.combo_arithmetic.setItemText(1, _translate("MainWindow", "Astar"))
        # self.combo_arithmetic.setItemText(2, _translate("MainWindow", "RRT"))
        # self.combo_arithmetic.setItemText(3, _translate("MainWindow", "APF"))
        # self.combo_arithmetic.setItemText(4, _translate("MainWindow", "4"))
        # self.combo_arithmetic_obs.setItemText(0, _translate("MainWindow", "图形障碍物"))
        # self.combo_arithmetic_obs.setItemText(1, _translate("MainWindow", "矩形"))
        # self.combo_arithmetic_obs.setItemText(2, _translate("MainWindow", "圆形"))
        # self.combo_arithmetic_obs.setItemText(3, _translate("MainWindow", "三角形"))
        # self.combo_arithmetic_obs.setItemText(4, _translate("MainWindow", "椭圆形"))
        # self.combo_arithmetic_obs.setItemText(5, _translate("MainWindow", "菱形"))
        # self.combo_arithmetic_obs.setItemText(6, _translate("MainWindow", "五角形"))
        self.pushButton_paint_rand.setText(_translate("MainWindow", "图形障碍物"))
        self.pushButton_ob.setText(_translate("MainWindow", "参数障碍物"))
        self.pushButton_modify_map.setText(_translate("MainWindow", "地图调整"))
        self.pushButton_input_startAndEnd.setText(_translate("MainWindow", "输入起始点"))
    # 路径规划
    def startPath(self):
        # 根据不同的算法
        if self.combo_arithmetic.currentText() == "Astar":
            print("启动A星算法！！！")
            self.grid_widget.startAstar()
        elif self.combo_arithmetic.currentText() == "RRT":
            print("启动RRT算法！！！")
            self.grid_widget.startRtt()
        elif self.combo_arithmetic.currentText() == "APF":
            print("启动APF算法！！！")
            self.grid_widget.startApf()

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
