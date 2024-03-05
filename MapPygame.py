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
import cv2
import numpy

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def surface_to_cv_bgr(surface: pygame.Surface) -> cv2.typing.MatLike:
    """
    Converts pygame surface pixel data into opencv BGR format Mat
    """

    surface_string = pygame.image.tostring(surface, 'RGB')

    # convert from (width, height, channel) to (height, width, channel)
    size = surface.get_size()
    array = numpy.frombuffer(surface_string, dtype=numpy.uint8).reshape((size[1], size[0], 3))

    img_bgr = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

    return img_bgr


def cv_bgr_to_surface(img_bgr: cv2.typing.MatLike) -> pygame.Surface:
    """
    Converts pygame surface pixel data into opencv BGR format Mat
    """
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    height, width = img_rgb.shape[:2]
    surface = pygame.image.frombuffer(img_rgb.tobytes(), (width, height), 'RGB')

    return surface


def draw_line(surface, color, start_pos, end_pos, radius):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(abs(dx), abs(dy))

    for i in range(distance):
        x = int(start_pos[0] + float(i) / distance * dx)
        y = int(start_pos[1] + float(i) / distance * dy)
        pygame.draw.circle(surface, color, (x, y), radius)


class PygameWidget(QWidget):
    BACK_COLOR = WHITE
    OBS_COLOR = BLACK
    OBS_RADIUS = 5
    WIDTH = 920
    HEIGHT = 390
    CELL_SIZE = 10

    def __init__(self, main_window, parent=None):
        super(PygameWidget, self).__init__(parent)

        # 初始化pygame
        pygame.init()

        # 设置窗口大小
        self.width, self.height = PygameWidget.WIDTH, PygameWidget.HEIGHT
        self.setMinimumSize(self.width, self.height)

        # 设置背景颜色
        self.back_color = PygameWidget.BACK_COLOR
        # 设置障碍物颜色
        self.obs_color = PygameWidget.OBS_COLOR

        self.grid_color = PygameWidget.OBS_COLOR

        # 设置障碍物画笔半径
        self.obs_radius = PygameWidget.OBS_RADIUS

        # 设置主平面，障碍物平面和路径规划平面
        self.surface = pygame.Surface((self.width, self.height))
        self.obs_surface = pygame.Surface((self.width, self.height))
        self.plan_surface = pygame.Surface((self.width, self.height))

        self.grid_surface = pygame.Surface((self.width, self.height))

        # 设置障碍物平面和路径规划平面的透明色
        self.obs_surface.set_colorkey(self.back_color)
        self.plan_surface.set_colorkey(self.back_color)

        self.grid_surface.set_colorkey(self.back_color)

        self.obs_surface.fill(self.back_color)
        self.plan_surface.fill(self.back_color)

        self.grid_surface.fill(self.back_color)

        # 栅格大小
        self.cell_size = PygameWidget.CELL_SIZE

        # 初始化多边形轮廓存储的障碍物
        self.obstacles = []

        # # 障碍物列表
        # self.block_map = []

        # 地图列表
        self.cols = self.width // self.cell_size
        self.rows = self.height // self.cell_size

        # 初始化栅格化存储的地图
        # self.map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.grid_map = numpy.zeros((self.cols, self.rows), dtype=numpy.uint8)

        # 起始点和终点
        self.start_point = None
        self.end_point = None

        # 创建一个定时器，用于更新界面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)  # 设置帧率为60

        # 初始化状态
        self.drawing = False
        self.last_pos = None
        self.grid = False

        self.main_window = main_window

    def save_map(self):
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

        if file_path is None:
            self.main_window.printf("路径未选择！", None, None)
            return

        features = []

        # feature_collection = None

        if self.obstacles is not None:
            for obstacle in self.obstacles:
                if obstacle[0] != obstacle[-1]:
                    obstacle.append(obstacle[0])
                features.append(
                    geojson.Feature(geometry=geojson.Polygon([obstacle]), properties={"name": "obstacle"}))

        if self.start_point is not None and self.end_point is not None:
            start_point = Point(self.start_point)
            end_point = Point(self.end_point)
            features.append(Feature(geometry=start_point, properties={"name": "start point"}))
            features.append(Feature(geometry=end_point, properties={"name": "goal point"}))

        feature_collection = FeatureCollection(features)

        # 将FeatureCollection保存为GeoJSON格式的字符串
        geojson_str = json.dumps(feature_collection, indent=4)

        print(geojson_str)

        with open(file_path, 'w') as file:
            file.write(geojson_str)
        self.main_window.printf("地图已成功保存！", None, None)

        # 关闭文件保存对话框
        # self.win_main.quit()

    def open_map(self):
        # 创建文件对话框
        dialog = QFileDialog()
        # 设置文件对话框标题
        dialog.setWindowTitle('打开地图')
        # 设置文件过滤器
        dialog.setNameFilter('地图文件 (*.txt *.csv)')

        # 打开文件对话框，并返回选择的文件路径
        file_path, _ = dialog.getOpenFileName(self, '打开地图', '', '地图文件 (*.txt *.csv)')

        # with open('file_path', 'r') as file:
        #     data = json.load(file)
        # 打开并读取txt文件内容
        if not file_path:
            self.main_window.printf("路径未选择！", None, None)
            return
        # 如果选择了文件路径，则进行地图识别的操作
        with open(file_path, 'r') as file:
            geojson_str = file.read()

        # 将字符串解析为GeoJSON对象
        geojson_obj = geojson.loads(geojson_str)
        print(geojson_obj)
        # 打开地图前需要先清空地图
        # self.clearObstacles()
        # # 清空地图后，重新设置地图分辨率
        # self.modifyMap(int(self.cell_size))
        obstacles = []
        for feature in geojson_obj['features']:
            geometry = feature['geometry']
            properties = feature['properties']
            if geometry['type'] == 'Point' and properties['name'] == "start point":
                self.start_point = geometry['coordinates']
            if geometry['type'] == 'Point' and properties['name'] == "goal point":
                self.end_point = geometry['coordinates']
            elif geometry['type'] == 'Polygon':
                # for contour in geometry['coordinates']:

                obstacles.append(geometry['coordinates'][0])

        self.obstacles = obstacles

        # print(obstacles)
        self.update_obs_surface()

        # self.obs_surface.fill(self.back_color)
        #
        # for obs in obstacles:
        #     pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obs)

        # screen = pygame.Surface((self.width, self.height))
        #
        # # 设置颜色
        # WHITE = (255, 255, 255)
        #
        # # 设置背景颜色
        # screen.fill(WHITE)
        #
        # # 绘制障碍物
        # for obstacle in self.obstacles:
        #     pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)
        #
        # # 绘制起始点和终点
        # if self.start_point:
        #     pygame.draw.rect(screen, (0, 255, 0),
        #                      (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
        # if self.end_point:
        #     pygame.draw.rect(screen, (255, 0, 0),
        #                      (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)
        #
        # # 将pygame surface转换为QImage
        # image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)
        #
        # # 将QImage转换为QPixmap
        # pixmap = QPixmap.fromImage(image)
        #
        # # 使用QPainter绘制pixmap
        # painter = QPainter(self)
        # painter.drawPixmap(0, 0, pixmap)
        # painter.end()

    # 鼠标点击事件处理
    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.drawing = True
            pos = (event.pos().x(), event.pos().y())
            self.last_pos = pos
            pygame.draw.circle(self.obs_surface, self.obs_color, pos, self.obs_radius)
            # print((x, y))

    # 鼠标移动事件处理
    def mouseMoveEvent(self, event):

        if self.drawing:
            current_pos = (event.pos().x(), event.pos().y())
            if self.last_pos:
                draw_line(self.obs_surface, self.obs_color, self.last_pos, current_pos, self.obs_radius)
            self.last_pos = current_pos

        # if event.button() == Qt.LeftButton:  # 鼠标左键
        #
        #     pygame.draw.circle(self.obs_surface, self.obs_color, (x, y), self.obs_radius)
        #     if (x, y) != self.start_point and (x, y) != self.end_point:
        #         # 将鼠标点击的位置对齐到网格上
        #         x = (x // self.cell_size) * self.cell_size
        #         y = (y // self.cell_size) * self.cell_size
        #         if (x, y) not in self.obstacles:
        #             self.obstacles.append((x, y))
        #             self.map[x // self.cell_size][y // self.cell_size - 1] = 1
        #             print(self.map)
        #             self.main_window.printf("设置障碍物", x // self.cell_size, y // self.cell_size)
        #             self.update()
        #         else:
        #             self.obstacles.remove((x, y))
        #             self.map[x // self.cell_size][y // self.cell_size - 1] = 0
        #             print(self.map)
        #             self.main_window.printf("取消障碍物", x // self.cell_size, y // self.cell_size)
        #             self.update()
        # elif event.button() == Qt.RightButton:  # 鼠标右键
        #     # 将鼠标点击的位置对齐到网格上
        #     x = (x // self.cell_size) * self.cell_size
        #     y = (y // self.cell_size) * self.cell_size
        #     if self.start_point is None:
        #         if (x, y) not in self.obstacles:
        #             self.start_point = (x, y)
        #             print(self.start_point)
        #             self.main_window.printf("设置起点", x // self.cell_size, y // self.cell_size)
        #     else:
        #         if self.start_point != (x, y) and self.end_point is None:
        #             if (x, y) not in self.obstacles:
        #                 self.end_point = (x, y)
        #                 print(self.end_point)
        #                 self.main_window.printf("设置终点", x // self.cell_size, y // self.cell_size)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.last_pos = None

    # 绘制pygame界面
    def paintEvent(self, event):

        self.surface.fill(PygameWidget.BACK_COLOR)
        self.surface.blit(self.obs_surface, (0, 0))
        self.surface.blit(self.plan_surface, (0, 0))
        if self.grid:
            self.surface.blit(self.grid_surface, (0, 0))

        # # 绘制障碍物
        # for obstacle in self.obstacles:
        #     pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)
        #
        # # 绘制起始点和终点
        # if self.start_point:
        #     pygame.draw.rect(screen, (0, 255, 0),
        #                      (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
        # if self.end_point:
        #     pygame.draw.rect(screen, (255, 0, 0),
        #                      (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)

        # 将pygame surface转换为QImage
        surface_string = pygame.image.tostring(self.surface, 'RGB')
        # width, height = self.surface.get_size()
        image = QImage(surface_string, self.width, self.height, QImage.Format_RGB888)

        # 将QImage转换为QPixmap
        pixmap = QPixmap.fromImage(image)

        # 使用QPainter绘制pixmap
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

    def rasterize_map(self):

        obs_array = pygame.surfarray.array3d(self.obs_surface)
        # obs_array = numpy.transpose(obs_array, (1, 0, 2))

        for y in range(self.rows):
            for x in range(self.cols):
                # 获取当前栅格对应的像素块
                pixel_block = obs_array[x * self.cell_size:(x + 1) * self.cell_size,
                              y * self.cell_size:(y + 1) * self.cell_size]

                # 检查像素块中是否存在非白色像素（障碍物）
                if numpy.any(numpy.any(pixel_block != list(self.back_color), axis=2)):
                    self.grid_map[x, y] = 1  # 标记为障碍物
                    rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size,
                                       self.cell_size)
                    pygame.draw.rect(self.obs_surface, self.obs_color, rect)

        for y in range(self.rows + 1):
            pygame.draw.line(self.grid_surface, self.grid_color, (0, y * self.cell_size), (self.width, y * self.cell_size))
        for x in range(self.cols + 1):
            pygame.draw.line(self.grid_surface, self.grid_color, (x * self.cell_size, 0), (x * self.cell_size, self.height))

        self.grid = True

    # 画起始点
    def painting_ori(self, x, y):
        # 绘画起点 这个和点击画起始点功能冲突 暂时分隔这两个功能，假设输入起始点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置背景颜色
        screen.fill(PygameWidget.WHITE)

        self.start_point = (x, y)
        self.main_window.printf("设置起点", x, y)
        if self.start_point:
            pygame.draw.rect(screen, (0, 255, 0),
                             (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
            image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

            # 将QImage转换为QPixmap
            pixmap = QPixmap.fromImage(image)

            # 使用QPainter绘制pixmap
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            # grid_widget.painting_ori(x,y)

    def painting_end(self, x1, y1):
        # 绘画终点 假设输入终止点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置背景颜色
        screen.fill(PygameWidget.WHITE)

        self.end_point = (x1, y1)
        self.main_window.printf("设置终点", x1, y1)
        if self.end_point:
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)
            image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

            # 将QImage转换为QPixmap
            pixmap = QPixmap.fromImage(image)

            # 使用QPainter绘制pixmap
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            # grid_widget.painting_end(x1,y1)

    def random_obstacles(self, x1, y1, x2, y2):
        # # 随机生成连续障碍物点
        # for i in range(3):
        #     x = random.randint(x1, x2)
        #     y = random.randint(y1, y2)
        #     z = random.randint(10, 15)
        #     for j in range(z):
        #         if (x, y) != self.start_point and (x, y) != self.end_point:
        #             if (x, y) not in self.obstacles:
        #                 self.obstacles.append((x, y))
        #                 x = x + 1
        # for i in range(4):
        #     x = random.randint(x1, x2)
        #     y = random.randint(y1, y2)
        #     z = random.randint(10, 15)
        #     for j in range(z):
        #         if (x, y) != self.start_point and (x, y) != self.end_point:
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

    # def paint_block(self, x1, y1, x2, y2):
    #
    #     screen = pygame.Surface((self.width, self.height))
    #
    #     # 设置背景颜色
    #     screen.fill(PygameWidget.WHITE)
    #
    #     for obstacle in self.obstacles:
    #         pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)
    #
    #     # 将pygame surface转换为QImage
    #     image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)
    #
    #     # 将QImage转换为QPixmap
    #     pixmap = QPixmap.fromImage(image)
    #
    #     # 使用QPainter绘制pixmap
    #     painter = QPainter(self)
    #     painter.drawPixmap(0, 0, pixmap)
    #     painter.end()
    #     # grid_widget.paint_block(x1, y1, x2, y2)

    # 修改地图分辨率
    def modifyMap(self, size):
        if self.start_point is None and self.end_point is None and len(self.obstacles) == 0:
            if not isinstance(size, str):
                self.main_window.printf("请输入正确的分辨率！", None, None)
                if int(size) > 0:
                    new_size = int(size)
                    self.cell_size = new_size
                    self.update()
                    self.main_window.printf("分辨率调整成功！", None, None)
                else:
                    self.main_window.printf("请输入正确的分辨率！", None, None)
        else:
            self.main_window.printf("当前地图已起始点或障碍点不可调整地图分辨率，请清空地图后再次调整分辨率！", None, None)

    # 随机起始点方法
    def generateRandomStart(self):
        if self.start_point is None:
            # 生成随机的x和y坐标
            x = random.choice(range(0, self.width - 1, 5))
            y = random.choice(range(0, self.height - 1, 5))
            if (x, y) not in self.obstacles:
                self.start_point = (x, y)
                self.main_window.printf("添加起始点：", x, y)
                self.update()
        else:
            self.main_window.printf("error: 已经设置起点！", None, None)

        if self.end_point is None and self.end_point != self.start_point:
            # 生成随机的x和y坐标
            x_1 = random.choice(range(0, self.width - 1, 5))
            y_1 = random.choice(range(0, self.height - 1, 5))
            if (x_1, y_1) not in self.obstacles:
                self.end_point = (x_1, y_1)
                self.main_window.printf("添加终点：", y_1, x_1)
                self.update()
        else:
            self.main_window.printf("error: 已经设置终点！", None, None)
        self.update()

    def update_obs_surface(self):
        self.obs_surface.fill(self.back_color)
        for obs in self.obstacles:
            pygame.draw.polygon(self.obs_surface, self.obs_color, obs)

    # 清空地图方法
    def clear_obstacles(self):
        # self.start_point = None  # 清除起点
        # self.end_point = None  # 清除终点
        self.obstacles = []  # 清空障碍物列表
        self.update_obs_surface()
        self.main_window.printf("已经清空地图", None, None)
        # self.update()  # 更新界面

    # 清空地图起始点
    def clearStartAndEnd(self):
        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.main_window.printf("已经清空起始点", None, None)
        self.update()  # 更新界面

    def get_obs_vertices(self):
        capture_bgr = surface_to_cv_bgr(self.obs_surface)
        capture_gray = cv2.cvtColor(capture_bgr, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(capture_gray, 254, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # for obs in contours:
        #     obs = obs.reshape(-1, 2).tolist()
        #     pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obs)

        self.obstacles = []

        for obs in contours:
            obstacle = obs.squeeze().tolist()
            pygame.draw.polygon(self.obs_surface, self.obs_color, obstacle)
            self.obstacles.append(obstacle)

        # print(self.obstacles)

        # cv2.drawContours(capture_bgr, contours, -1, (0, 0, 255), 2)
        # self.obs_surface = cv_bgr_to_surface(capture_bgr)
        # self.obs_surface.set_colorkey(WHITE)
        # cv2.imshow('contours', capture_bgr)
        # print(contours[0].reshape(-1, 2).tolist())
        # print(contours)
        # print(hierarchy)

        # return contours


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
