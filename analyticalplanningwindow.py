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
        self.windows = []
        self.add_button()


    def add_button(self):
        button1 = QPushButton('单次路径结果比较分析')
        button1.clicked.connect(self.on_single_click)
        self.mainLayout.addWidget(button1)
        button2 = QPushButton('多次路径比较分析')
        button2.clicked.connect(self.on_category_click)
        self.mainLayout.addWidget(button2)
        button3 = QPushButton('不同算法性能比较')
        button3.clicked.connect(self.on_category_compare_click)
        self.mainLayout.addWidget(button3)

    # 单次路径结果比较分析方法
    def on_single_click(self):
        files, _ = QFileDialog.getOpenFileNames(self, '打开结果文件', '', '结果文件 (*.txt)')
        for index, f in enumerate(files):  # 循环选中的所有文件
            self.open_result_single(index, f)

    def open_result_single(self, index, f):
        """
        打开单路径分析窗口。在分析路径的窗口里打开。
        :param index:当前的文件是选中的第几个文件，用于调整窗口的位置
        :param f:文件的路径
        :return:None
        """
        new_window = QtWidgets.QMainWindow()
        self.result_single(new_window, self.pygame_widget, index, f)
        new_window.setWindowTitle('单路径分析')
        new_window.show()
        # 将新创建的窗口实例添加到列表中
        self.windows.append(new_window)

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

    def on_category_click(self):
        dialog = QFileDialog()
        dialog.setWindowTitle("选择要进行多次结果分析的文件夹")
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        if dialog.exec_():
            try:
                category = Category_Demo()  # 创建多结果类
                category.read_file(dialog.selectedFiles()[0])  # 获取选择的文件夹的路径
                self.open_result_category(category, dialog.selectedFiles()[0])
            except ValueError as e:
                # label_notice.setText(str(e))
                print(str(e))

    def open_result_category(self, category, dir_path):
        """
        打开多路径分析窗口。在分析路径的窗口打开。
        :return:
        """
        new_window = QtWidgets.QMainWindow()
        self.result_category(new_window, self.pygame_widget, category, dir_path)
        new_window.setWindowTitle('多路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

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

    def on_category_compare_click(self):
        files, _ = QFileDialog.getOpenFileNames(self, '选择要进行性能对比的文件', '', '计算结果文件 (*.txt)')
        if files:
            compare = Category_Compare()
            compare.read_category(files)
            self.open_result_category_compare(compare)

    def open_result_category_compare(self, compare):
        """
        打开多算法比较信息的窗口
        :param compare: 比较信息,包含多个category
        :return: None
        """
        new_window = QtWidgets.QMainWindow()
        self.result_category_compare(new_window, self.pygame_widget, compare)
        new_window.setWindowTitle('多路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

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
        self.result_category_average(new_window, self.pygame_widget, category)
        new_window.setWindowTitle('多路径分析')
        new_window.show()
        self.windows.append(new_window)  # 将新创建的窗口实例添加到列表中

    def result_category_average(self, MainWindow, pygame_widget, category):
        """
        多结果分析求平均值窗口设计
        :param category:
        :return:
        """
        MainWindow.setGeometry(100, 100, 500, 500)
        label_smooth = QLabel("平均平滑度是：" + str(category.ave_smooth))
        label_time = QLabel("平均时间是：" + str(category.ave_time))
        label_path_length = QLabel("平均路径长度是：" + str(category.ave_path_length))
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