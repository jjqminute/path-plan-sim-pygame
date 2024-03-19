import math
import re
import sys
import time

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

from arithmetic.APF.apf import apf
from arithmetic.Astar.Map import Map
from arithmetic.Astar.astar import astar
from arithmetic.RRT.rrt import rrt

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

        # 设置障碍物画笔半径
        self.obs_radius = PygameWidget.OBS_RADIUS

        # 设置主平面，障碍物平面和路径规划平面
        self.surface = pygame.Surface((self.width, self.height))
        self.obs_surface = pygame.Surface((self.width, self.height))
        self.plan_surface = pygame.Surface((self.width, self.height))

        # 设置障碍物平面和路径规划平面的透明色
        self.obs_surface.set_colorkey(self.back_color)
        self.plan_surface.set_colorkey(self.back_color)
        self.obs_surface.fill(self.back_color)
        self.plan_surface.fill(self.back_color)

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

        self.main_window = main_window
        # 矩形初始位置和大小
        self.rect_size = 50
        self.rect_newsize = 50
        self.rect = pygame.Rect(100, 100, self.rect_size, self.rect_size)

        self.circle_center = (30, 30)
        self.circle_radius = 30
        self.circle_newradius = 30

        self.elli_center = (30, 90)
        self.elli_width = 50
        self.elli_newwidth = 50
        self.elli_newheight = 100
        self.elli_height = 100
        self.elli_points = []
        self.elli_newpoints = []

        self.dia_center = (30, 30)
        self.dia_size = 60
        self.dia_vertices = []
        self.dia_newsize = 60
        self.dia_newvertices = []

        self.star_center = (30, 30)
        self.star_points = []
        self.star_newpoints = []
        self.star_outer_radius = 40
        self.star_newouter_radius = 40

        self.tri_center = (60, 60)
        self.tri_size = 100
        self.tri_newsize = 100
        self.tri_vertices = []
        self.tri_newvertices = []

        self.angle = 2 * math.pi / 5  # 五角星的内角
        self.dragging = False
        self.offset_x = 0
        self.offset_x = 0
        self.result = None

    def startAstar(self):
        self.result = None
        #self.obs_surface.fill(PygameWidget.BACK_COLOR)
        self.search = astar(self)
        self.result = self.search.process()

        if self.result is not None:
            for k in self.result:

                pygame.draw.circle(self.plan_surface,(0,100,255),(k.x,k.y),3)
                #time.sleep(0.1)
    def startRtt(self):
        self.result = None
        self.search = rrt(self)
        self.result, time1 = self.search.plan()
        if self.result is not None:
            for k in self.result:
                pygame.draw.circle(self.plan_surface,(0,100,255),(k.x,k.y),3)
        if self.result is not None:
            for k in range(len(self.result) - 1):
                pygame.draw.line(self.plan_surface, (0, 100, 255), (self.result[k].x, self.result[k].y),
                                 (self.result[k + 1].x, self.result[k + 1].y), 3)
        track = []
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        self.save_result(time1,track)

    def startApf(self):
        self.result = None
        self.search = apf(self)
        self.result, time1 = self.search.plan()
        if self.result is not None:
            for k in self.result:
                pygame.draw.circle(self.plan_surface, (0, 100, 255), (k[0], k[1]), 3)
            for k in range(len(self.result) - 1):
                pygame.draw.line(self.plan_surface, (0, 100, 255), (self.result[k][0], self.result[k][1]),
                                 (self.result[k + 1][0], self.result[k + 1][1]), 3)
        self.save_result(time1, self.result)

    def save_result(self, time1, track):
        """
        保存结果文件，包括地图
        :param time1: 运行的时间
        :param track: 路径 [(x,y),(x,y),...]
        :return:
        """
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
                    geojson.Feature(geometry=geojson.Polygon([obstacle]), properties={"name": "障碍物"}))

        if self.start_point is not None and self.end_point is not None:
            start_point = Point(self.start_point)
            end_point = Point(self.end_point)
            features.append(Feature(geometry=start_point, properties={"name": "起始点"}))
            features.append(Feature(geometry=end_point, properties={"name": "终点"}))

        feature_collection = FeatureCollection(features)
        js2 = json.loads(str(feature_collection))
        js = dict(time=time1, track=track)
        js2.update(js)
        print(js2)
        # 将FeatureCollection保存为GeoJSON格式的字符串
        geojson_str = json.dumps(js2, indent=4)
        with open(file_path, 'w') as file:
            file.write(geojson_str)
        self.main_window.printf("地图和结果数据已成功保存！", None, None)

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
                    geojson.Feature(geometry=geojson.Polygon([obstacle]), properties={"name": "障碍物"}))

        if self.start_point is not None and self.end_point is not None:
            start_point = Point(self.start_point)
            end_point = Point(self.end_point)
            features.append(Feature(geometry=start_point, properties={"name": "起始点"}))
            features.append(Feature(geometry=end_point, properties={"name": "终点"}))

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
            if geometry['type'] == 'Point' and properties['name'] == "\u8d77\u59cb\u70b9":
                self.start_point = geometry['coordinates']
            if geometry['type'] == 'Point' and properties['name'] == "\u7ec8\u70b9":
                self.end_point = geometry['coordinates']
            elif geometry['type'] == 'Polygon':
                obstacles.append(tuple(geometry['coordinates'][0]))

        self.obstacles = obstacles

        # print(obstacles)

        self.obs_surface.fill(self.back_color)

        for obs in obstacles:
            pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obs)

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
            print(pos)
            pygame.draw.circle(self.obs_surface, self.obs_color, pos, self.obs_radius)
        elif event.button() == Qt.RightButton:
            self.drawing = True
            pos = (event.pos().x(), event.pos().y())
            if self.obstacles != []:
                if self.start_point is None and [event.pos().x(), event.pos().y()] not in self.obstacles[0]:
                    if pos not in self.obstacles:
                        self.start_point = pos
                        print(self.start_point)
                        pygame.draw.circle(self.obs_surface, (0, 255, 0), pos, self.obs_radius)
                        self.main_window.printf("设置起点", event.pos().x(), event.pos().y())
                else:
                    if self.start_point != pos and self.end_point == None:
                        if pos not in self.obstacles:
                            self.end_point = pos
                            print(self.end_point)
                            pygame.draw.circle(self.obs_surface, (255, 0, 0), pos, self.obs_radius)
                            self.main_window.printf("设置终点", event.pos().x(), event.pos().y())
            else:
                self.main_window.text_result.append("请添加障碍物后再设置起始点")

    # 鼠标移动事件处理
    def mouseMoveEvent(self, event):

        if self.drawing:
            current_pos = (event.pos().x(), event.pos().y())
            if self.last_pos:
                draw_line(self.obs_surface, self.obs_color, self.last_pos, current_pos, self.obs_radius)
            self.last_pos = current_pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.last_pos = None

    # 绘制pygame界面
    def paintEvent(self, event):

        self.surface.fill(PygameWidget.BACK_COLOR)
        # if(len(self.obstacles)!=0):
        #     #print(self.obstacles)
        #     for obstacle in self.obstacles[0]:
        #         pygame.draw.circle(self.obs_surface, (0, 0, 0), (obstacle[0], obstacle[1]), self.obs_radius)
        self.surface.blit(self.plan_surface, (0, 0))
        self.surface.blit(self.obs_surface, (0, 0))

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
    # 输入始末点坐标
    def ori_end_input(self, ):  # 输入起始点终点函数
        # print("111111111111111111111111111")
        coordinate = self.main_window.text_input.text()
        print(coordinate)
        pattern = r"\((\d+),(\d+)\)"  # 匹配坐标的正则表达式模式
        match = re.match(pattern, coordinate)
        # print(match)
        if match:
            keyx = int(match.group(1))  # 提取横坐标
            keyy = int(match.group(2))  # 提取纵坐标
            print("起点横坐标:", keyx)
            print("起点纵坐标:", keyy)
            self.painting_ori(keyx, keyy)
        else:
            print("坐标格式不正确")
        coordinate_2 = self.main_window.text_input_2.text()
        # print(coordinate_2)
        pattern_2 = r"\((\d+),(\d+)\)"  # 匹配坐标的正则表达式模式
        match_2 = re.match(pattern, coordinate_2)
        if match_2:
            # global keyx_2, keyy_2
            keyx_2 = int(match_2.group(1))  # 提取横坐标
            keyy_2 = int(match_2.group(2))  # 提取纵坐标
            print("终点横坐标:", keyx_2)
            print("终点纵坐标:", keyy_2)
            self.painting_end(keyx_2, keyy_2)
        else:
            print("坐标格式不正确")
    # 栅格化地图
    def rasterize_map(self):

        obs_array = pygame.surfarray.array3d(self.obs_surface)
        # obs_array = numpy.transpose(obs_array, (1, 0, 2))
        for y in range(self.rows):
            for x in range(self.cols):
                if (x, y) == self.start_point or (x, y) == self.end_point :
                    continue
                # 获取当前栅格对应的像素块
                pixel_block = obs_array[x * self.cell_size:(x + 1) * self.cell_size,
                              y * self.cell_size:(y + 1) * self.cell_size]

                # 检查像素块中是否存在非白色像素（障碍物）
                if numpy.any(numpy.any(pixel_block == list(self.obs_color), axis=2)):
                    self.grid_map[x, y] = 1  # 标记为障碍物
                    rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size,
                                       self.cell_size)
                    pygame.draw.rect(self.obs_surface, self.obs_color, rect)

    # 画起始点
    def painting_ori(self, x, y):
        # 绘画起点 这个和点击画起始点功能冲突 暂时分隔这两个功能，假设输入起始点前地图为空，所以直接填色即可
        # 创建一个新的surface
        # screen = pygame.Surface((self.width, self.height))
        #
        # # 设置背景颜色
        # screen.fill(PygameWidget.WHITE)
        #
        # self.start_point = (x, y)
        # self.win_main.printf("设置起点", x, y)
        # if self.start_point:
        #     pygame.draw.rect(screen, (0, 255, 0),
        #                      (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
        #     image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)
        #
        #     # 将QImage转换为QPixmap
        #     pixmap = QPixmap.fromImage(image)
        #
        #     # 使用QPainter绘制pixmap
        #     painter = QPainter(self)
        #     painter.drawPixmap(0, 0, pixmap)
        #     painter.end()
        #     # grid_widget.painting_ori(x,y)
        self.start_point = (x, y)
        self.main_window.printf("设置起点", x, y)
        if self.start_point:
            pygame.draw.circle(self.obs_surface, (0, 255, 0), (x, y), self.obs_radius)
            self.update()

    def painting_end(self, x1, y1):
        # 绘画终点 假设输入终止点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置背景颜色
        # screen.fill(PygameWidget.WHITE)
        #
        # self.end_point = (x1, y1)
        # self.win_main.printf("设置终点", x1, y1)
        # if self.end_point:
        #     pygame.draw.rect(screen, (255, 0, 0),
        #                      (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)
        #     image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)
        #
        #     # 将QImage转换为QPixmap
        #     pixmap = QPixmap.fromImage(image)
        #
        #     # 使用QPainter绘制pixmap
        #     painter = QPainter(self)
        #     painter.drawPixmap(0, 0, pixmap)
        #     painter.end()
        #     # grid_widget.painting_end(x1,y1)
        self.end_point = (x1, y1)
        self.main_window.printf("设置终点", x1, y1)
        if self.end_point:
            pygame.draw.circle(self.obs_surface, (255, 0, 0), (x1, y1), self.obs_radius)
            self.update()

    # 修改地图分辨率[OK]
    def modifyMap(self, size):
        if self.start_point is None and self.end_point is None and len(self.obstacles) == 0:
            if not isinstance(size, str):
                self.main_window.printf("请输入正确的分辨率！", None, None)
                if int(size) > 0:
                    new_size = int(size)
                    self.cell_size = new_size
                    print(self.cell_size)
                    self.cols = self.width // self.cell_size
                    self.rows = self.height // self.cell_size
                    self.main_window.printf("分辨率调整成功！", None, None)
                else:
                    self.main_window.printf("请输入正确的分辨率！", None, None)
        else:
            self.main_window.printf("当前地图已起始点或障碍点不可调整地图分辨率，请清空地图后再次调整分辨率！", None, None)

    # 随机起始点方法[Ok]
    def generateRandomStart(self):
        if self.start_point is None:
            # 生成随机的x和y坐标
            x = random.choice(range(0, self.width))
            y = random.choice(range(0, self.height))
            if [x,y] not in self.obstacles:
                self.start_point = (x,y)
                print(self.start_point)
                self.main_window.printf("添加起始点：", x, y)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), (x,y), self.obs_radius)
                self.update()
        else:
            self.main_window.printf("error: 已经设置起点！", None, None)

        if self.end_point is None and self.end_point != self.start_point:
            # 生成随机的x和y坐标
            x_1 = random.choice(range(0, self.width ))
            y_1 = random.choice(range(0, self.height))
            if [x_1, y_1] not in self.obstacles:
                self.end_point = (x_1, y_1)
                pygame.draw.circle(self.obs_surface, (255, 0, 0), (x_1, y_1), self.obs_radius)
                self.main_window.printf("添加终点：", y_1, x_1)
                self.update()
        else:
            self.main_window.printf("error: 已经设置终点！", None, None)
        self.update()

    # 清空地图方法[OK]
    def clear_map(self):
        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.obstacles = []  # 清空障碍物列表
        self.update_map()
        self.main_window.printf("已经清空地图", None, None)
        self.update()  # 更新界面

    # 清空地图起始点[OK]
    def clearStartAndEnd(self):
        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.update_map()
        self.main_window.printf("已经清空起始点", None, None)
        self.update()  # 更新界面

    #  更新地图界面方法[OK]
    def update_map(self):
        # 清空surface
        self.surface.fill(PygameWidget.BACK_COLOR)
        # 清空obs_surface
        self.obs_surface.fill(PygameWidget.BACK_COLOR)
        # 清空plan_surface
        self.plan_surface.fill(PygameWidget.BACK_COLOR)

    # 未栅格化地图障碍点获取
    def get_obs_vertices(self):
        capture_bgr = surface_to_cv_bgr(self.obs_surface)
        capture_gray = cv2.cvtColor(capture_bgr, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(capture_gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # for obs in contours:
        #     obs = obs.reshape(-1, 2).tolist()
        #     pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obs)

        self.obstacles = []

        for obs in contours:
            obstacle = obs.squeeze().tolist()
            pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obstacle)
            self.obstacles.append(obstacle)
        print(self.obstacles)

        # cv2.drawContours(capture_bgr, contours, -1, (0, 0, 255), 2)
        # self.obs_surface = cv_bgr_to_surface(capture_bgr)
        # self.obs_surface.set_colorkey(WHITE)
        # cv2.imshow('contours', capture_bgr)
        # print(contours[0].reshape(-1, 2).tolist())
        # print(contours)
        # print(hierarchy)

        # return contours
    # 随机图形障碍物
    def paint_random_one(self):
        current_index = self.main_window.combo_arithmetic_obs.currentIndex()
        if current_index == 1:
            pygame.draw.rect(self.obs_surface, BLACK, (100, 100, self.rect_size, self.rect_size))
        elif current_index == 2:
            pygame.draw.circle(self.obs_surface, BLACK, self.circle_center, self.circle_radius, 0)
        elif current_index == 3:
            # 三角形
            height = self.tri_size * math.sqrt(3) / 2
            # 计算顶点坐标
            self.tri_vertices = [
                (self.tri_center[0], self.tri_center[1] - self.tri_size / 2),  # 上方顶点
                (self.tri_center[0] - self.tri_size / 2, self.tri_center[1] + height),  # 左下顶点
                (self.tri_center[0] + self.tri_size / 2, self.tri_center[1] + height)  # 右下顶点
            ]
            pygame.draw.polygon(self.obs_surface, BLACK, self.tri_vertices)
        elif current_index == 4:
            # 椭圆
            for i in range(360):
                angle_rad = math.radians(i)
                x = self.elli_center[0] + self.elli_width / 2 * math.cos(angle_rad)
                y = self.elli_center[0] + self.elli_height / 2 * math.sin(angle_rad)
                self.elli_points.append((int(x), int(y)))
                # 绘制多边形
            pygame.draw.polygon(self.obs_surface, BLACK, self.elli_points)  # 随机多边形障碍物
        elif current_index == 5:
            # 绘制菱形
            half_size = self.dia_size // 2
            a = math.sqrt(2) * half_size
            self.dia_vertices = [(self.dia_center[0] - half_size, self.dia_center[1] - half_size),
                                 (self.dia_center[0] + half_size, self.dia_center[1] - half_size),
                                 (self.dia_center[0] + a, self.dia_center[1] + a),
                                 (self.dia_center[0] - a, self.dia_center[1] + a)]
            pygame.draw.polygon(self.obs_surface, BLACK, self.dia_vertices)
        elif current_index == 6:
            # 绘制五角星
            for i in range(5):
                x = self.star_center[0] + self.star_outer_radius * math.cos(i * self.angle)
                y = self.star_center[1] + self.star_outer_radius * math.sin(i * self.angle)
                self.star_points.append((int(x), int(y)))
            pygame.draw.polygon(self.obs_surface, BLACK, self.star_points)
    #  随机多边形障碍物
    def random_graph(self,count):
        for _ in range(count):
            shape_type = random.randrange(6)  # 0表示圆形，1表示矩形
            if shape_type == 0:
                radius = random.randrange(10, 51)
                x = random.randrange(radius, self.width - radius)
                y = random.randrange(radius, self.height - radius)
                pygame.draw.circle(self.obs_surface, self.obs_color, (x, y), radius)
            elif shape_type == 1:
                width = random.randrange(20, 81)
                height = random.randrange(20, 81)
                color = (random.randrange(256), random.randrange(256), random.randrange(256))
                x = random.randrange(0, self.width - width)
                y = random.randrange(0, self.height - height)
                pygame.draw.rect(self.obs_surface, self.obs_color, (x, y, width, height))
            elif shape_type == 2:
                side_length = random.randrange(20, 81)
                x = random.randrange(0, self.width - side_length)
                y = random.randrange(0, self.height - side_length)
                triangle_points = [(x, y), (x + side_length, y), (x + side_length // 2, y + int(0.866 * side_length))]
                pygame.draw.polygon(self.obs_surface, self.obs_color, triangle_points)
            elif shape_type == 3:
                # 绘制椭圆
                width = random.randrange(20, 81)
                height = random.randrange(20, 81)
                x = random.randrange(0, self.width - width)
                y = random.randrange(0, self.height - height)
                pygame.draw.ellipse(self.obs_surface, self.obs_color, (x, y, width, height))
            elif shape_type == 4:
                # 绘制菱形
                side_length = random.randrange(20, 81)
                x = random.randrange(0, self.width - side_length)
                y = random.randrange(0, self.height - side_length)
                diamond_points = [(x + side_length // 2, y), (x + side_length, y + side_length // 2),
                                  (x + side_length // 2, y + side_length), (x, y + side_length // 2)]
                pygame.draw.polygon(self.obs_surface, self.obs_color, diamond_points)
            elif shape_type == 5:
                # 绘制五角星
                side_length = random.randrange(20, 81)
                x = random.randrange(0, self.width - side_length)
                y = random.randrange(0, self.height - side_length)
                star_points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5
                    if i % 2 == 0:
                        star_points.append((x + side_length // 2 + side_length * math.cos(angle) / 2,
                                            y + side_length * math.sin(angle) / 2))
                    else:
                        star_points.append(
                            (x + side_length // 2 + side_length * math.cos(angle), y + side_length * math.sin(angle)))
                pygame.draw.polygon(self.obs_surface, self.obs_color, star_points)
        self.main_window.text_result.append("成功生成 %s 个随机障碍物" %count)

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
