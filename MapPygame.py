import sys
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtCore import QTimer
import random
import json
import geojson
from geojson import Point, Feature, FeatureCollection
from collections import defaultdict
import geopandas as gpd
from shapely.geometry import Point, MultiPoint, shape

class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super(PygameWidget, self).__init__(parent)

        # 设置窗口大小
        self.width, self.height = 920, 399
        self.setMinimumSize(self.width, self.height)

        # 障碍物以及起始点大小
        self.cell_size = 10

        # 初始化pygame
        pygame.init()

        # 创建一个空的障碍物列表
        self.obstacles = []

        # 起始点和终点
        self.start_point = None
        self.end_point = None

        # 创建一个定时器，用于更新界面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)  # 设置帧率为60


    def saveMap(self):
        # 创建文件对话框
        dialog = QFileDialog()
        # 设置文件对话框为保存文件模式
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        # 设置对话框标题
        dialog.setWindowTitle('保存地图')
        # 设置文件过滤器
        dialog.setNameFilter('地图文件 (*.txt)')
        # 设置默认文件名，包含文件类型后缀
        dialog.setDefaultSuffix('txt')

        # 打开文件对话框，并返回保存的文件路径
        file_path, _ = dialog.getSaveFileName(self, '保存地图', '', '地图文件 (*.txt)')

        if file_path:
            features = []
            start_point = Point(self.start_point)
            end_point = Point(self.end_point)
            multi_points = self.obstacles
            if multi_points:
                features.append(geojson.Feature(geometry=geojson.MultiPoint(multi_points),properties={"name": "障碍物点"}))
            features.append(Feature(geometry=start_point, properties={"name": "起始点"}))
            features.append(Feature(geometry=end_point, properties={"name": "终点"}))
            feature_collection = FeatureCollection(features)

            # 将FeatureCollection保存为GeoJSON格式的字符串
            geojson_str = json.dumps(feature_collection, indent=4)

            print(geojson_str)

            with open(file_path, 'w') as file:
                file.write(geojson_str)
            self.win_main.printf("地图已成功保存！", None, None)
            # 关闭文件保存对话框
            # self.win_main.quit()

    def openMap(self):
        # 创建文件对话框
        dialog = QFileDialog()
        # 设置文件对话框标题
        dialog.setWindowTitle('打开地图')
        # 设置文件过滤器
        dialog.setNameFilter('地图文件 (*.txt *.csv)')

        # 打开文件对话框，并返回选择的文件路径
        file_path, _ = dialog.getOpenFileName(self, '打开地图', '', '地图文件 (*.txt *.csv)')

        # 如果选择了文件路径，则进行地图识别的操作
        if file_path:
            if file_path:
                # with open('file_path', 'r') as file:
                #     data = json.load(file)
                # 打开并读取txt文件内容
                with open(file_path, 'r') as file:
                    geojson_str = file.read()

                    # 将字符串解析为GeoJSON对象
                geojson_obj = geojson.loads(geojson_str)
                print(geojson_obj)
                # 打开地图前需要先清空地图
                # self.clearObstacles()
                # # 清空地图后，重新设置地图分辨率
                # self.modifyMap(int(self.cell_size))
                multi_points = []
                for feature in geojson_obj['features']:
                    geometry = feature['geometry']
                    properties =feature['properties']
                    if geometry['type'] == 'Point' and properties['name']=="\u8d77\u59cb\u70b9":
                        self.start_point = geometry['coordinates']
                    if geometry['type'] == 'Point' and properties['name']=="\u7ec8\u70b9":
                        self.end_point = geometry['coordinates']
                    elif geometry['type'] == 'MultiPoint':
                        multi_points.extend(geometry['coordinates'])
                self.obstacles=multi_points

                screen = pygame.Surface((self.width, self.height))

                # 设置颜色
                WHITE = (255, 255, 255)

                # 设置背景颜色
                screen.fill(WHITE)

                # 绘制障碍物
                for obstacle in self.obstacles:
                    pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)

                # 绘制起始点和终点
                if self.start_point:
                    pygame.draw.rect(screen, (0, 255, 0),
                                     (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
                if self.end_point:
                    pygame.draw.rect(screen, (255, 0, 0),
                                     (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)

                # 将pygame surface转换为QImage
                image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

                # 将QImage转换为QPixmap
                pixmap = QPixmap.fromImage(image)

                # 使用QPainter绘制pixmap
                painter = QPainter(self)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()


    # 鼠标点击事件处理
    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if event.button() == Qt.LeftButton:  # 鼠标左键
            if (x,y) != self.start_point and (x,y) != self.end_point:
                # 将鼠标点击的位置对齐到网格上
                x = (x // self.cell_size) * self.cell_size
                y = (y // self.cell_size) * self.cell_size
                if (x,y) not in self.obstacles:
                    self.obstacles.append((x,y))
                    print(self.obstacles)
        elif event.button() == Qt.RightButton:  # 鼠标右键
            # 将鼠标点击的位置对齐到网格上
            x = (x // self.cell_size) * self.cell_size
            y = (y // self.cell_size) * self.cell_size
            if self.start_point is None:
                if (x,y) not in self.obstacles:
                    self.start_point = (x,y)
                    print(self.start_point)
            else:
                if self.start_point != (x,y) and self.end_point == None:
                    if (x, y) not in self.obstacles:
                        self.end_point = (x,y)
                        print(self.end_point)

    # 绘制pygame界面
    def paintEvent(self, event):
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)

        # 绘制障碍物
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)

        # 绘制起始点和终点
        if self.start_point:
            pygame.draw.rect(screen, (0, 255, 0), (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
        if self.end_point:
            pygame.draw.rect(screen, (255, 0, 0), (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)

        # 将pygame surface转换为QImage
        image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

        # 将QImage转换为QPixmap
        pixmap = QPixmap.fromImage(image)

        # 使用QPainter绘制pixmap
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

    #画起始点
    def painting_ori(self, x, y):
        # 绘画起点 这个和点击画起始点功能冲突 暂时分隔这两个功能，假设输入起始点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)
        self.start_point = (x, y)
        if self.start_point:
            pygame.draw.rect(screen, (0, 255, 0), (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
            image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

            # 将QImage转换为QPixmap
            pixmap = QPixmap.fromImage(image)

            # 使用QPainter绘制pixmap
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            #grid_widget.painting_ori(x,y)

    def painting_end(self, x1, y1):
        # 绘画终点 假设输入终止点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)
        self.end_point=(x1,y1)
        if self.end_point:
            pygame.draw.rect(screen, (255, 0, 0), (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)
            image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

            # 将QImage转换为QPixmap
            pixmap = QPixmap.fromImage(image)

            # 使用QPainter绘制pixmap
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            #grid_widget.painting_end(x1,y1)
    def random_obstacles(self, x1, y1, x2, y2):
    #随机生成连续障碍物点
        # for i in range(3):
        #     x = random.randint(x1, x2)
        #     y = random.randint(y1, y2)
        #     z = random.randint(10, 15)
        #     for j in range(z):
        #         if (x, y) != self.start_point and (x, y) != self.end_point :
        #             if (x, y) not in self.obstacles:
        #                 self.obstacles.append((x,y))
        #                 x = x + 1
        # for i in range(4):
        #     x = random.randint(x1, x2)
        #     y = random.randint(y1, y2)
        #     z = random.randint(10, 15)
        #     for j in range(z):
        #         if (x, y) != self.start_point and (x, y) != self.end_point :
        #             if (x, y) not in self.obstacles:
        #                 self.obstacles.append((x, y))
        #                 y = y + 1

        with open('package.geojson', 'r', encoding='UTF-8') as f:
            data = json.load(f)
        print(data)

        # 遍历每一个feature，提取geometry和properties，并添加到GeoDataFrame中
        # 遍历features
        for feature in data['features']:
            geometry = feature['geometry']

            # 判断几何类型
            # if geometry['type'] == 'Point':
            #     # 提取点的坐标
            #     coordinates = geometry['coordinates']
            #     print(f"Point coordinates: {coordinates}")
            if geometry['type'] == 'MultiPoint':
                # 提取多点坐标
                coordinates = geometry['coordinates']
                print(f"MultiPoint coordinates: {coordinates}")
            self.obstacles.append(coordinates)
        self.paint_block(x1, y1, x2, y2)

    def paint_block(self, x1, y1, x2, y2):

        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)

        for obstacle in self.obstacles:
            pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)

        # 将pygame surface转换为QImage
        image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

        # 将QImage转换为QPixmap
        pixmap = QPixmap.fromImage(image)

        # 使用QPainter绘制pixmap
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        #grid_widget.paint_block(x1, y1, x2, y2)


    def clear_map(self):
        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.obstacles = []  # 清空障碍物列表
        self.update()  # 更新界面

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle('Pygame in PyQt')

        # 创建Pygame部件
        self.pygame_widget = PygameWidget()

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.pygame_widget)

        # 创建主窗口部件
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
