import math
import re
import sys
import time
import pandas as pd
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
from maze import MazeGenerator
from arithmetic.APF.apf import apf
from arithmetic.Astar.Map import Map
from arithmetic.Astar.astar import astar
from arithmetic.RRT.rrt import Rrt
from arithmetic.PRM.prm import prm
from arithmetic.APFRRT.APFRRT import APFRRT
from result import Result_Demo
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

color_mapping = {
        (255, 0, 0): (255, 0, 0),  # 红色保持不变
        (0, 255, 0): (0, 255, 0),  # 绿色保持不变
        (0, 0, 0): (0, 0, 0),  # 黑色保持不变
        # 添加其他颜色的映射关系
    }
# Pygame 的 Surface 对象转换为 OpenCV 的 BGR 格式
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

# 一个 OpenCV 的 BGR 格式图像（Mat 对象）转换为 Pygame 的 Surface 对象
def cv_bgr_to_surface(img_bgr: cv2.typing.MatLike) -> pygame.Surface:
    """
    Converts pygame surface pixel data into opencv BGR format Mat
    """
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    height, width = img_rgb.shape[:2]
    surface = pygame.image.frombuffer(img_rgb.tobytes(), (width, height), 'RGB')

    return surface

# 鼠标拖动绘制障碍物画线
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
    START_COLOR = (0, 0, 0)
    END_COLOR = (255.0, 0)
    OBS_RADIUS = 5
    WIDTH = 920
    HEIGHT = 390
    CELL_SIZE = 10
    POINT_RADIUS = 5
    # 初始化参数 包括算法参数，始末点颜色，障碍物颜色，图层，障碍物初始位置参数
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
        self.start_color = PygameWidget.START_COLOR
        self.end_color = PygameWidget.END_COLOR
        # 设置障碍物画笔半径
        self.obs_radius = PygameWidget.OBS_RADIUS

        # 设置主平面，障碍物平面，路径规划平面和起点终点平面
        self.surface = pygame.Surface((self.width, self.height))
        self.obs_surface = pygame.Surface((self.width, self.height))
        self.plan_surface = pygame.Surface((self.width, self.height))
        self.point_surface = pygame.Surface((self.width, self.height))

        self.grid_surface = pygame.Surface((self.width, self.height))

        # 设置障碍物平面和路径规划平面的透明色
        self.obs_surface.set_colorkey(self.back_color)
        self.plan_surface.set_colorkey(self.back_color)
        self.point_surface.set_colorkey(self.back_color)

        self.grid_surface.set_colorkey(self.back_color)

        self.obs_surface.fill(self.back_color)
        self.plan_surface.fill(self.back_color)
        self.point_surface.fill(self.back_color)

        self.grid_surface.fill(self.back_color)

        # 栅格大小
        self.cell_size = PygameWidget.CELL_SIZE
        self.cell_size_temp=10
        # 初始化多边形轮廓存储的障碍物
        self.obstacles = []

        # # 障碍物列表
        # self.block_map = []

        # 地图列表
        self.cols = self.width // self.cell_size
        self.rows = self.height // self.cell_size
        self.cols_temp = 92
        self.rows_temp = 39
        #
        self.rasterize_map_num=0
        self.start_rect_temp=None
        self.end_rect_temp=None
        # 初始化多边形轮廓存储的障碍物
        self.obstacles = []

        # RRT算法步长
        self.rrt_step = 10
        self.rrt_max_iterations = 10000
        # Astar参数修改
        self.Astar_para = 10
        # APF算法参数
        self.apf_step = 10
        self.apf_max_iterations = 10000
        self.apf_attraction = 0.5
        self.apf_repulsion = 0.5
        # prm算法参数
        self.prm_max_point_num=1000
        self.prm_step=30
        # 初始化栅格化存储的地图
        # self.map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.grid_map = numpy.zeros((self.cols, self.rows), dtype=numpy.uint8)
        self.red_paint = False
        self.green_paint = False
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
    # 实验部分所需随机产生始末点函数
    def ran_experience_point(self,para):
        for i in range(para):
            self.start_point= (random.randint(0, 910), random.randint(0, 380))
            self.end_point=(random.randint(0, 910), random.randint(0, 380))
            # print(self.start_point,self.end_point)
    # 检查随机始末点是否与障碍物碰撞
    def collision(self,point,polygon):
        num_intersections = 0
        n = len(polygon)

        for i in range(n):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]

            # 检查射线是否与边相交
            if (p1[1] > point[1]) != (p2[1] > point[1]) and \
                    point[0] < (p2[0] - p1[0]) * (point[1] - p1[1]) / (p2[1] - p1[1]) + p1[0]:
                num_intersections += 1

        # 如果相交次数是奇数，则点在多边形内部
        return num_intersections % 2 == 1
    # TODO  修改函数参数的四个函数
    def modifyRRT(self,step,iterations):
        self.main_window.text_result.append("成功修改步长为%s" %step)
        self.main_window.text_result.append("修改迭代次数为%s" %iterations)
        self.rrt_step = step
        self.rrt_max_iterations=iterations

    def modifyAstar(self,para):
        self.main_window.text_result.append("成功修改启发式函数权重系数为%s" %para)
        self.Astar_para = para

    def modifyAPF(self,step,iterations,attraction,repulsion):
        self.main_window.text_result.append("成功修改步长为%s" % step)
        self.main_window.text_result.append("修改迭代次数为%s" % iterations)
        self.main_window.text_result.append("修改吸引力系数为%s" % attraction)
        self.main_window.text_result.append("修改排斥力系数为%s" % repulsion)
        self.rrt_step = step
        self.rrt_max_iterations = iterations
        self.apf_attraction=attraction
        self.apf_repulsion=repulsion
    def modifyprm(self,max_point_num,step):
        self.main_window.text_result.append("成功修改撒点数目为%s" % max_point_num)
        self.main_window.text_result.append("修改步长为%s" % step)
        self.prm_step=step
        self.prm_max_point_num=max_point_num



    # TODO 五个算法的开始规划函数 单次仿真
    # A*算法
    def startAstar(self):
        self.result = None
        # self.obs_surface.fill(PygameWidget.BACK_COLOR)
        self.search = astar(self)
        self.result = self.search.process()
        print("ASTAR over")
        print(self.result)
        if self.result is not None:
            for k in self.result:
                pygame.draw.circle(self.plan_surface, (0, 100, 255), (k.x, k.y), 3)
                # time.sleep(0.1)
        track = []
        time1=self.search.plan()
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        # self.save_result(time1,track)
        return track, time1

    # RRT算法
    def startRtt(self):
        self.result = None
        self.search = Rrt(self)
        self.result, time1 = self.search.plan(self.plan_surface)
        self.search.step = self.rrt_step
        self.search.max_iterations = self.rrt_max_iterations
        if self.result is not None:
            for k in self.result:
                pygame.draw.circle(self.plan_surface, (0, 100, 255), (k.x, k.y), 3)
        if self.result is not None:
            for k in range(len(self.result) - 1):
                pygame.draw.line(self.plan_surface, (100, 100, 0), (self.result[k].x, self.result[k].y),
                                 (self.result[k + 1].x, self.result[k + 1].y), 3)
        track = []
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        # self.save_result(time1,track)
        return track, time1

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
        return self.result,time1

    def startApfRrt(self):
        self.result = None
        self.result,time = APFRRT(self).plan(self.plan_surface)
        track = []
        for point in self.result[:-1]:
            track.append((point.x, point.y))
        return track, time

    def startPRm(self):
        self.result = None
        self.result, time = prm(self).plan(self.plan_surface)
        track = []
        for point in self.result:
            track.append((point.x, point.y))
        return track, time

    # TODO 五个算法的开始规划函数  多次仿真与不显示路径规划过程的实验仿真
    def startAstar_exp_mul(self):
        self.result = None
        # self.obs_surface.fill(PygameWidget.BACK_COLOR)
        self.search = astar(self)
        self.result = self.search.process()
        print("ASTAR over")
        track = []
        time1=self.search.plan()
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        # self.save_result(time1,track)
        return track, time1
    def startAstar_exp(self):
        self.start_point = (random.randint(0, 910), random.randint(0, 380))
        self.end_point = (random.randint(0, 910), random.randint(0, 380))
        self.result = None
        # self.obs_surface.fill(PygameWidget.BACK_COLOR)
        self.search = astar(self)
        self.result = self.search.process()
        print("ASTAR over")
        track = []
        time1=self.search.plan()
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        # self.save_result(time1,track)
        return track, time1
    def startRtt_exp_mul(self):
        self.result = None
        self.search = Rrt(self)
        self.result, time1 = self.search.plan_test(self.plan_surface)
        self.search.step = self.rrt_step
        self.search.max_iterations = self.rrt_max_iterations
        track = []
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        # self.save_result(time1,track)
        return track, time1
    def startRtt_exp(self):
        self.start_point = (random.randint(0, 910), random.randint(0, 380))
        self.end_point = (random.randint(0, 910), random.randint(0, 380))
        self.result = None
        self.search = Rrt(self)
        self.result, time1 = self.search.plan_test(self.plan_surface)
        self.search.step = self.rrt_step
        self.search.max_iterations = self.rrt_max_iterations
        track = []
        for point in self.result:
            x = point.x
            y = point.y
            track.append((x, y))
        # self.save_result(time1,track)
        return track, time1
    def startApf_exp_mul(self):
        self.result = None
        self.search = apf(self)
        self.result, time1 = self.search.plan()
        return self.result,time1
    def startApf_exp(self):
        self.start_point = (random.randint(0, 910), random.randint(0, 380))
        self.end_point = (random.randint(0, 910), random.randint(0, 380))
        self.result = None
        self.search = apf(self)
        self.result, time1 = self.search.plan()
        return self.result,time1
    def startApfRrt_exp_mul(self):
        self.result = None
        self.result,time = APFRRT(self).plan_test(self.plan_surface)
        track = []
        for point in self.result[:-1]:
            track.append((point.x, point.y))
        return track, time
    def startApfRrt_exp(self):
        self.start_point = (random.randint(0, 910), random.randint(0, 380))
        self.end_point = (random.randint(0, 910), random.randint(0, 380))
        self.result = None
        self.result,time = APFRRT(self).plan_test(self.plan_surface)
        track = []
        for point in self.result[:-1]:
            track.append((point.x, point.y))
        return track, time
    def startPRm_exp_mul(self):
        self.result = None
        self.result, time = prm(self).plan_test(self.plan_surface)
        track = []
        for point in self.result:
            track.append((point.x, point.y))
        return track, time
    def startPRm_exp(self):
        self.start_point = (random.randint(0, 910), random.randint(0, 380))
        self.end_point = (random.randint(0, 910), random.randint(0, 380))
        self.result = None
        self.result, time = prm(self).plan_test(self.plan_surface)
        track = []
        for point in self.result:
            track.append((point.x, point.y))
        return track, time
    # 保存结果 geojson txt
    def save_result(self, time1, track, file_path):
        """
        保存结果文件，包括地图
        :param time1: 运行的时间
        :param track: 路径 [(x,y),(x,y),...]
        :return:
        """
        # # 创建文件对话框
        # dialog = QFileDialog()
        # # 设置文件对话框为保存文件模式
        # dialog.setAcceptMode(QFileDialog.AcceptSave)
        # # 设置对话框标题
        # dialog.setWindowTitle('保存地图')
        # # 设置文件过滤器
        # dialog.setNameFilter('地图文件 (*.txt)')
        # # 设置默认文件名，包含文件类型后缀
        # dialog.setDefaultSuffix('txt')

        # 打开文件对话框，并返回保存的文件路径
        # file_path, _ = dialog.getSaveFileName(self, '保存地图', '', '地图文件 (*.txt)')

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
        # print(feature_collection)
        # 先封装经过计算再存入结果文件
        r = Result_Demo(self.start_point, self.end_point, time1, self.obstacles, track,None,0)
        print(r.smoothness,r.time,r.pathlen)
        print(r.compute_smoothness())
        js2 = json.loads(str(feature_collection))
        js = dict(time=time1, track=track, smoothness=r.smoothness, pathlen=r.pathlen)  # 加入r中计算的数据到结果类中
        js2.update(js)
        # print(js2)
        # 将FeatureCollection保存为GeoJSON格式的字符串
        geojson_str = json.dumps(js2, indent=4)
        with open(file_path, 'w') as file:
            file.write(geojson_str)
        self.main_window.printf("地图和结果数据已成功保存！", None, None)
        return r.pathlen

    # 保存地图文件 geojson
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
        # 打开地图文件
    # 打开地图
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
        print(file_path, _)
        # 打开地图前需要先清空地图
        # self.clearObstacles()
        # # 清空地图后，重新设置地图分辨率
        # self.modifyMap(int(self.cell_size))
        obstacles = []
        for feature in geojson_obj['features']:
            geometry = feature['geometry']
            properties = feature['properties']
            if geometry['type'] == 'Point' and properties['name'] == "起始点":
                self.start_point = geometry['coordinates']
            if geometry['type'] == 'Point' and properties['name'] == "终点":
                self.end_point = geometry['coordinates']
            elif geometry['type'] == 'Polygon':
                obstacles.append(tuple(geometry['coordinates'][0]))
        print(self.start_point, self.end_point)

        self.obstacles = obstacles

        # print(obstacles)

        self.obs_surface.fill(self.back_color)

        for obs in obstacles:
            pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obs)
        pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
        pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
        self.update()

    # 鼠标点击事件处理 线状障碍物 右键始末点，ctrl与右键控制障碍物
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            pos = (event.pos().x(), event.pos().y())
            self.last_pos = pos
            print(pos)
            pygame.draw.circle(self.obs_surface, self.obs_color, pos, self.obs_radius)
        elif event.modifiers() == Qt.ControlModifier and event.button() == Qt.RightButton :
            current_index = self.main_window.get_selected_value()
            print(current_index)
            if current_index == 1:
                rect = pygame.Rect(self.rect.left, self.rect.top, self.rect_size, self.rect_size)
                self.rect.left = event.pos().x()
                self.rect.top = event.pos().y()
                new_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect_newsize, self.rect_newsize)
                print(current_index)
                pygame.draw.rect(self.obs_surface, WHITE, rect)
                pygame.draw.rect(self.obs_surface, BLACK, new_rect)
                pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
                # self.update()
                # # self.update()
            elif current_index == 2:
                pygame.draw.circle(self.obs_surface, (255, 255, 255), self.circle_center, self.circle_newradius)
                pygame.draw.circle(self.obs_surface, BLACK, (event.pos().x(), event.pos().y()),
                                   self.circle_radius)
                # print(self.circle_radius)
                self.circle_center = (event.pos().x(), event.pos().y())

                pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
                # self.update()
            elif current_index == 3:
                pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.tri_vertices)
                height = self.tri_size * math.sqrt(3) / 2
                # 计算顶点坐标
                self.tri_vertices = [
                    (event.pos().x(), event.pos().y() - self.tri_size / 2),  # 上方顶点
                    (event.pos().x() - self.tri_size / 2, event.pos().y() + height),  # 左下顶点
                    (event.pos().x() + self.tri_size / 2, event.pos().y() + height)  # 右下顶点
                ]
                pygame.draw.polygon(self.obs_surface, BLACK, self.tri_vertices)
                self.tri_center = (event.pos().x(), event.pos().y())
                pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
                # self.update()
            elif current_index == 4:
                # 重绘椭圆
                pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.elli_points)
                self.elli_points = []
                for i in range(360):
                    angle_rad = math.radians(i)
                    x = event.pos().x() + self.elli_width / 2 * math.cos(angle_rad)
                    y = event.pos().y() + self.elli_height / 2 * math.sin(angle_rad)
                    self.elli_points.append((int(x), int(y)))
                    # 绘制多边形
                pygame.draw.polygon(self.obs_surface, BLACK, self.elli_points)  # 随机多边形障碍物
                self.elli_center = (event.pos().x(), event.pos().y())
                pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
                # self.update()
            elif current_index == 5:
                # 重绘菱形
                pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.dia_vertices)
                self.dia_vertices = []
                half_size = self.dia_size // 2
                a = math.sqrt(2) * half_size
                self.dia_vertices = [(event.pos().x() - half_size, event.pos().y() - half_size),
                                     (event.pos().x() + half_size, event.pos().y() - half_size),
                                     (event.pos().x() + a, event.pos().y() + a),
                                     (event.pos().x() - a, event.pos().y() + a)]
                pygame.draw.polygon(self.obs_surface, BLACK, self.dia_vertices)
                self.star_center = (event.pos().x(), event.pos().y())
                self.dia_center = (event.pos().x(), event.pos().y())
                pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
                # self.update()
            elif current_index == 6:
                pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.star_points)
                self.star_points = []
                for i in range(5):
                    x = event.pos().x() + self.star_outer_radius * math.cos(i * self.angle)
                    y = event.pos().y() + self.star_outer_radius * math.sin(i * self.angle)
                    self.star_points.append((int(x), int(y)))
                pygame.draw.polygon(self.obs_surface, BLACK, self.star_points)
                self.star_center = (event.pos().x(), event.pos().y())
                pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
                pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)

        elif event.button() == Qt.RightButton:
            self.drawing = True
            pos = (event.pos().x(), event.pos().y())
            if self.obstacles != []:
                if self.start_point is None and [event.pos().x(), event.pos().y()] not in self.obstacles[0]:
                    if pos not in self.obstacles:
                        self.start_point = pos
                        print(self.start_point)
                        pygame.draw.circle(self.point_surface, (0, 255, 0), pos, self.obs_radius)
                        self.main_window.printf("设置起点", event.pos().x(), event.pos().y())
                else:
                    if self.start_point != pos and self.end_point == None:
                        if pos not in self.obstacles:
                            self.end_point = pos
                            print(self.end_point)
                            pygame.draw.circle(self.point_surface, (255, 0, 0), pos, self.obs_radius)
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
            self.last_pos = None
            self.get_obs_vertices()
    def wheelEvent(self, event):
        current_index = self.main_window.get_selected_value()
        if current_index == 1:
            # 获取滚轮滚动的角度
            delta = event.angleDelta().y()
            self.rect_size = self.rect_newsize
            # 根据滚轮方向调整矩形大小
            if delta > 0:
                # 滚轮向上，增大矩形大小
                self.rect_newsize += 10
            elif delta < 0:
                # 滚轮向下，减小矩形大小
                self.rect_newsize = max(0, self.rect_size - 10)  # 保证不小于最小值

            # 更新矩形位置
            new_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect_size, self.rect_size)
            pygame.draw.rect(self.obs_surface, (255, 255, 255), new_rect)
            new_rect_1 = pygame.Rect(self.rect.left, self.rect.top, self.rect_newsize, self.rect_newsize)
            pygame.draw.rect(self.obs_surface, BLACK, new_rect_1)
            self.rect_size=self.rect_newsize
            pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
            pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
            # 更新窗口
            self.update()
        elif current_index == 2:
            delta = event.angleDelta().y()
            self.circle_radius = self.circle_newradius
            if delta > 0:
                # 滚轮向上，增大矩形大小
                self.circle_newradius += 10
            elif delta < 0:
                # 滚轮向下，减小矩形大小
                self.circle_newradius = max(0, self.circle_newradius - 10)  # 保证不小于最小值
            pygame.draw.circle(self.obs_surface, (255, 255, 255), self.circle_center, self.circle_radius)
            # print(self.circle_radius,self.circle_newradius)
            pygame.draw.circle(self.obs_surface, BLACK, self.circle_center, self.circle_newradius)
            self.circle_radius=self.circle_newradius
            pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
            pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
            self.update()
        elif current_index == 3:
            delta = event.angleDelta().y()
            self.tri_size = self.tri_newsize
            newheight = self.tri_newsize * math.sqrt(3) / 2
            if delta > 0:
                # 滚轮向上，增大矩形大小
                self.tri_newsize += 10
            elif delta < 0:
                # 滚轮向下，减小矩形大小
                self.tri_newsize = max(0, self.tri_newsize - 10)  # 保证不小于最小值
            # 计算顶点坐标
            self.tri_newvertices = [
                (self.tri_center[0], self.tri_center[1] - self.tri_newsize / 2),  # 上方顶点
                (self.tri_center[0] - self.tri_newsize / 2, self.tri_center[1] + newheight),  # 左下顶点
                (self.tri_center[0] + self.tri_newsize / 2, self.tri_center[1] + newheight)  # 右下顶点
            ]
            pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.tri_vertices)
            pygame.draw.polygon(self.obs_surface, BLACK, self.tri_newvertices)
            self.tri_vertices = self.tri_newvertices
            pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
            pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
            self.update()
        elif current_index == 4:
            delta = event.angleDelta().y()
            self.elli_width = self.elli_newwidth
            self.elli_height = self.elli_newheight
            if delta > 0:
                # 滚轮向上，增大矩形大小
                self.elli_newwidth += 5
                self.elli_newheight += 10
            elif delta < 0:
                # 滚轮向下，减小矩形大小
                self.elli_newheight = max(0, self.elli_newheight - 10)
                self.elli_newwidth = max(0, self.elli_newwidth - 5)  # 保证不小于最小值
            self.elli_newpoints = []
            for i in range(360):
                angle_rad = math.radians(i)
                x = self.elli_center[0] + self.elli_newwidth / 2 * math.cos(angle_rad)
                y = self.elli_center[1] + self.elli_newheight / 2 * math.sin(angle_rad)
                self.elli_newpoints.append((int(x), int(y)))
                # 绘制多边形
            pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.elli_points)  # 随机多边形障碍物
            pygame.draw.polygon(self.obs_surface, BLACK, self.elli_newpoints)
            self.elli_points = self.elli_newpoints
            pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
            pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
            self.update()
        elif current_index == 5:
            delta = event.angleDelta().y()
            self.dia_size = self.dia_newsize
            newhalf_size = self.dia_newsize // 2
            a = math.sqrt(2) * newhalf_size
            if delta > 0:
                # 滚轮向上，增大矩形大小
                self.dia_newsize += 10
            elif delta < 0:
                # 滚轮向下，减小矩形大小
                self.dia_newsize = max(0, self.dia_newsize - 10)  # 保证不小于最小值
            # 计算顶点坐标

            self.dia_newvertices = [(self.dia_center[0] - newhalf_size, self.dia_center[1] - newhalf_size),
                                    (self.dia_center[0] + newhalf_size, self.dia_center[1] - newhalf_size),
                                    (self.dia_center[0] + a, self.dia_center[1] + a),
                                    (self.dia_center[0] - a, self.dia_center[1] + a)]
            pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.dia_vertices)
            print("dia", self.dia_vertices)
            print("newdia", self.dia_newvertices)
            pygame.draw.polygon(self.obs_surface, BLACK, self.dia_newvertices)
            self.dia_vertices = self.dia_newvertices
            pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
            pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
            self.update()
        elif current_index == 6:
            delta = event.angleDelta().y()
            self.star_outer_radius = self.star_newouter_radius
            if delta > 0:
                # 滚轮向上，增大矩形大小
                self.star_newouter_radius += 10
            elif delta < 0:
                # 滚轮向下，减小矩形大小
                self.star_newouter_radius = max(0, self.star_newouter_radius - 10)  # 保证不小于最小值
            self.star_newpoints = []
            # 绘制五角星
            for i in range(5):
                x = self.star_center[0] + self.star_newouter_radius * math.cos(i * self.angle)
                y = self.star_center[1] + self.star_newouter_radius * math.sin(i * self.angle)
                self.star_newpoints.append((int(x), int(y)))
            pygame.draw.polygon(self.obs_surface, (255, 255, 255), self.star_points)
            pygame.draw.polygon(self.obs_surface, BLACK, self.star_newpoints)
            self.star_points = self.star_newpoints
            pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
            pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)
            self.update()

    # 绘制pygame界面 重绘时被调用
    def paintEvent(self, event):
        self.surface.fill(PygameWidget.BACK_COLOR)
        self.surface.blit(self.obs_surface, (0, 0))
        self.surface.blit(self.point_surface, (0, 0))
        self.surface.blit(self.plan_surface, (0, 0))

        if self.grid:
            self.surface.blit(self.grid_surface, (0, 0))
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

        red= numpy.array([255, 0, 0])
        black=numpy.array([0,0,0])
        green=numpy.array([0,255,0])
        for y in range(self.rows_temp + 1):
            pygame.draw.line(self.grid_surface, (255, 255, 255), (0, y * self.cell_size_temp),
                             (self.width, y * self.cell_size_temp))
        for x in range(self.cols_temp + 1):
            pygame.draw.line(self.grid_surface, (255, 255, 255), (x * self.cell_size_temp, 0),
                             (x * self.cell_size_temp, self.height))

        obs_array = pygame.surfarray.array3d(self.obs_surface)
        for y in range(self.rows):
            for x in range(self.cols):
                # if (x, y) == self.start_point or (x, y) == self.end_point:
                #     continue

                pixel_block = obs_array[x * self.cell_size:(x + 1) * self.cell_size,
                              y * self.cell_size:(y + 1) * self.cell_size]

                if numpy.any(numpy.all(pixel_block == black, axis=2)):
                    self.grid_map[x, y] = 1  # 标记为障碍物
                    rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size,
                                       self.cell_size)
                    pygame.draw.rect(self.obs_surface, (0,0,0), rect)  # 使用新的颜色绘制障碍物
        start_grid_x = self.start_point[0] // self.cell_size
        start_grid_y = self.start_point[1] // self.cell_size
        end_grid_x = self.end_point[0] // self.cell_size
        end_grid_y = self.end_point[1] // self.cell_size
        # 绘制始点和末点的标记
        start_rect = pygame.Rect(start_grid_x * self.cell_size, start_grid_y * self.cell_size, self.cell_size,
                                 self.cell_size)
        end_rect = pygame.Rect(end_grid_x * self.cell_size, end_grid_y * self.cell_size, self.cell_size, self.cell_size)
        if self.end_rect_temp==None:
            pygame.draw.circle(self.point_surface, (255, 255, 255), self.start_point, self.obs_radius)
            pygame.draw.circle(self.point_surface, (255, 255, 255), self.end_point, self.obs_radius)
            pygame.draw.rect(self.point_surface, (0, 255, 0), start_rect)  # 使用绿色绘制始点
            pygame.draw.rect(self.point_surface, (255, 0, 0), end_rect)  # 使用红色绘制末点
        else:
            pygame.draw.rect(self.point_surface, (255, 255, 255), self.start_rect_temp)  # 使用绿色绘制始点
            pygame.draw.rect(self.point_surface, (255, 255, 255), self.end_rect_temp)  # 使用红色绘制末点
            pygame.draw.rect(self.point_surface, (0, 255, 0), start_rect)  # 使用绿色绘制始点
            pygame.draw.rect(self.point_surface, (255, 0, 0), end_rect)  # 使用红色绘制末点
        self.end_rect_temp=end_rect
        self.start_rect_temp=start_rect
        # 绘制格线
        for y in range(self.rows + 1):
            pygame.draw.line(self.grid_surface, self.grid_color, (0, y * self.cell_size),
                             (self.width, y * self.cell_size))
        for x in range(self.cols + 1):
            pygame.draw.line(self.grid_surface, self.grid_color, (x * self.cell_size, 0),
                             (x * self.cell_size, self.height))
        self.rows_temp = self.rows
        self.cols_temp = self.cols
        self.cell_size_temp = self.cell_size
        self.grid = True
        self.green_paint=False
        self.red_paint=False



    # 画起始点
    def painting_ori(self, x, y):
        # 输入新的起始点需要判断是否在之前已经生成起始点了，生成起始点就需要将原来的擦除以及self。start_point换成新的值
        if(self.start_point != None):
            pygame.draw.circle(self.obs_surface, (255, 255, 255), self.start_point, self.obs_radius)
            self.start_point = None
        self.start_point = (x, y)
        self.main_window.printf("设置起点", x, y)
        if self.start_point:
            pygame.draw.circle(self.obs_surface, (0, 255, 0), (x, y), self.obs_radius)
            self.update()

    def painting_end(self, x1, y1):
        if (self.end_point != None):
            pygame.draw.circle(self.obs_surface, (255, 255, 255), self.end_point, self.obs_radius)
            self.end_point = None
        # 绘画终点 假设输入终止点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))
        self.end_point = (x1, y1)
        self.main_window.printf("设置终点", x1, y1)
        if self.end_point:
            pygame.draw.circle(self.obs_surface, (255, 0, 0), (x1, y1), self.obs_radius)
            self.update()

    # 修改地图分辨率[OK]
    def modifyMap(self, size):
        # if self.start_point is None and self.end_point is None and len(self.obstacles) == 0:
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
        # else:
        #     self.main_window.printf("当前地图已起始点或障碍点不可调整地图分辨率，请清空地图后再次调整分辨率！", None, None)

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
        self.clear_map_surface()
        self.main_window.printf("已经清空地图", None, None)
        self.update()  # 更新界面

    # 清空地图起始点[OK]
    def clearStartAndEnd(self):
        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.update_map()
        self.main_window.printf("已经清空始末点", None, None)
        self.update()  # 更新界面
    def update_obs_surface(self):
        self.obs_surface.fill(self.back_color)
        for obs in self.obstacles:
            pygame.draw.polygon(self.obs_surface, self.obs_color, obs)

    def clear_map_surface(self):
        # 清空obs_surface
        self.obs_surface.fill(self.back_color)
        # 清空point_surface
        self.point_surface.fill(self.back_color)

    # # 清空plan_surface
        self.plan_surface.fill(self.back_color)
        self.grid_surface.fill(self.back_color)
    #  更新地图界面方法[OK]
    def update_map(self):

        # 清空obs_surface
        #  self.obs_surface.fill(self.back_color)
        # 清空point_surface
          self.point_surface.fill(self.back_color)
        # # 清空plan_surface
        #  self.plan_surface.fill(self.back_color)
        #  self.grid_surface.fill(self.back_color)
        # # 清空surface
        # self.surface.fill(PygameWidget.BACK_COLOR)
        # # 清空obs_surface
        # self.obs_surface.fill(PygameWidget.BACK_COLOR)
        # # 清空plan_surface
        # self.plan_surface.fill(PygameWidget.BACK_COLOR)

    # 未栅格化地图障碍点获取 找到障碍物轮廓 其中pygame.draw.polygon() 函数默认对封闭图形内部进行填充色彩
    def get_obs_vertices(self):
        capture_bgr = surface_to_cv_bgr(self.obs_surface)
        capture_gray = cv2.cvtColor(capture_bgr, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(capture_gray, 50, 255, cv2.THRESH_BINARY_INV)#捕捉图片颜色 即障碍物区域
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)#查找边界

        # for obs in contours:
        #     obs = obs.reshape(-1, 2).tolist()
        #     pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obs)

        self.obstacles = []

        for obs in contours:
            obstacle = obs.squeeze().tolist()
            pygame.draw.polygon(self.obs_surface, PygameWidget.OBS_COLOR, obstacle)#自动内部填充
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

    # 图形障碍物 可单独控制
    def paint_random_one(self,current_index):
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
        self.get_obs_vertices()



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
            elif shape_type == 3:
                # 绘制不重叠的椭圆
                width = random.randrange(20, 81)
                height = random.randrange(20, 81)
                x, y = self.get_non_overlapping_position(width, height)
                pygame.draw.ellipse(self.obs_surface, self.obs_color, (x, y, width, height))
            elif shape_type == 4:
                # 绘制不重叠的菱形
                side_length = random.randrange(20, 81)
                x, y = self.get_non_overlapping_position(side_length, side_length)
                diamond_points = [(x + side_length // 2, y), (x + side_length, y + side_length // 2),
                                  (x + side_length // 2, y + side_length), (x, y + side_length // 2)]
                pygame.draw.polygon(self.obs_surface, self.obs_color, diamond_points)
            elif shape_type == 5:
                # 绘制不重叠的五角星
                side_length = random.randrange(20, 81)
                x, y = self.get_non_overlapping_position(side_length, side_length)
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
        self.get_obs_vertices()
        self.main_window.text_result.append("成功生成 %s 个随机障碍物" %count)




    #  随机多边形不重叠障碍物
    def random_graph_new(self, count):
        self.clear_map() # 重置地图
        obstacles = []
        max_retries = 200 # 障碍物最大寻址次数，保证每个障碍物不重叠

        # 检查一个障碍物是否与障碍物列表中的任何障碍物重叠
        def is_overlapping(x, y, width, height):
            for obstacle in obstacles:
                obstacle_x, obstacle_y, obstacle_width, obstacle_height = obstacle
                if x < obstacle_x + obstacle_width and x + width > obstacle_x and y < obstacle_y + obstacle_height and y + height > obstacle_y:
                    return True
            return False

        # 根据用户输入的数量输出障碍物
        for _ in range(count):
            retries = 0
            while retries < max_retries:
                shape_type = random.randrange(4)
                if shape_type == 0:
                    radius = random.randrange(10, 51)
                    x = random.randrange(radius, self.width - radius)
                    y = random.randrange(radius, self.height - radius)
                    if not is_overlapping(x - radius, y - radius, 2 * radius, 2 * radius):
                        obstacles.append((x - radius, y - radius, 2 * radius, 2 * radius))
                        pygame.draw.circle(self.obs_surface, self.obs_color, (x, y), radius)
                        break
                elif shape_type == 1:
                    width = random.randrange(20, 81)
                    height = random.randrange(20, 81)
                    x = random.randrange(0, self.width - width)
                    y = random.randrange(0, self.height - height)
                    if not is_overlapping(x, y, width, height):
                        obstacles.append((x, y, width, height))
                        pygame.draw.rect(self.obs_surface, self.obs_color, (x, y, width, height))
                        break
                # 添加椭圆形障碍物生成逻辑
                elif shape_type == 2:
                    width = random.randrange(20, 81)
                    height = random.randrange(20, 81)
                    x = random.randrange(0, self.width - width)
                    y = random.randrange(0, self.height - height)
                    if not is_overlapping(x, y, width, height):
                        obstacles.append((x, y, width, height))
                        pygame.draw.ellipse(self.obs_surface, self.obs_color, (x, y, width, height))
                        break
                # 添加正菱形障碍物生成逻辑
                elif shape_type == 3:
                    side_length = random.randrange(20, 81)
                    x = random.randrange(0, self.width - side_length)
                    y = random.randrange(0, self.height - side_length)
                    if not is_overlapping(x, y, side_length, side_length):
                        obstacles.append((x, y, side_length, side_length))
                        diamond_points = [(x + side_length // 2, y),
                                          (x + side_length, y + side_length // 2),
                                          (x + side_length // 2, y + side_length),
                                          (x, y + side_length // 2)]
                        pygame.draw.polygon(self.obs_surface, self.obs_color, diamond_points)
                        break
                retries += 1

        return obstacles

    # 根据参数生成障碍物
    def graph_setting(self,quantity, size, types, overlap):
        self.clear_map()  # 重置地图
        obstacles = []
        max_retries = 200  # 障碍物最大寻址次数，保证每个障碍物不重叠
        my_array = types
        if overlap == "F": # 不重叠障碍物
            # 检查一个障碍物是否与障碍物列表中的任何障碍物重叠
            def is_overlapping(x, y, width, height):
                for obstacle in obstacles:
                    obstacle_x, obstacle_y, obstacle_width, obstacle_height = obstacle
                    if x < obstacle_x + obstacle_width and x + width > obstacle_x and y < obstacle_y + obstacle_height and y + height > obstacle_y:
                        return True
                return False

            # 根据用户输入的数量输出障碍物
            for _ in range(int(quantity)):
                retries = 0
                while retries < max_retries:
                    shape_type = random.choice(my_array)
                    if shape_type == 0:
                        # radius = random.randrange(10, 51)
                        radius = int(size)//2 # 统一半径
                        x = random.randrange(radius, self.width - radius)
                        y = random.randrange(radius, self.height - radius)
                        if not is_overlapping(x - radius, y - radius, 2 * radius, 2 * radius):
                            obstacles.append((x - radius, y - radius, 2 * radius, 2 * radius))
                            pygame.draw.circle(self.obs_surface, self.obs_color, (x, y), radius)
                            self.get_obs_vertices()
                            break
                    elif shape_type == 1:
                        width = int(size)
                        height = int(size)
                        x = random.randrange(0, self.width - width)
                        y = random.randrange(0, self.height - height)
                        if not is_overlapping(x, y, width, height):
                            obstacles.append((x, y, width, height))
                            pygame.draw.rect(self.obs_surface, self.obs_color, (x, y, width, height))
                            self.get_obs_vertices()
                            break
                    # 添加椭圆形障碍物生成逻辑
                    elif shape_type == 2:
                        width = int(size)
                        height = int(size)//2
                        x = random.randrange(0, self.width - width)
                        y = random.randrange(0, self.height - height)
                        if not is_overlapping(x, y, width, height):
                            obstacles.append((x, y, width, height))
                            pygame.draw.ellipse(self.obs_surface, self.obs_color, (x, y, width, height))
                            self.get_obs_vertices()
                            break
                    # 添加正菱形障碍物生成逻辑
                    elif shape_type == 3:
                        side_length = int(size)
                        x = random.randrange(0, self.width - side_length)
                        y = random.randrange(0, self.height - side_length)
                        if not is_overlapping(x, y, side_length, side_length):
                            obstacles.append((x, y, side_length, side_length))
                            diamond_points = [(x + side_length // 2, y),
                                              (x + side_length, y + side_length // 2),
                                              (x + side_length // 2, y + side_length),
                                              (x, y + side_length // 2)]
                            pygame.draw.polygon(self.obs_surface, self.obs_color, diamond_points)
                            self.get_obs_vertices()
                            break
                    elif shape_type == 4:
                        width = int(size)
                        height = int(size)//2
                        x = random.randrange(0, self.width - width)
                        y = random.randrange(0, self.height - height)
                        if not is_overlapping(x, y, width, height):
                            obstacles.append((x, y, width, height))
                            pygame.draw.rect(self.obs_surface, self.obs_color, (x, y, width, height))
                            self.get_obs_vertices()
                            break
                    retries += 1

            return obstacles
        elif overlap == "T": # 重叠障碍物
            for _ in range(int(quantity)):
                shape_type = random.choice(my_array)  # 0表示圆形，1表示矩形
                if shape_type == 0:
                    radius = int(size)//2
                    x = random.randrange(radius, self.width - radius)
                    y = random.randrange(radius, self.height - radius)
                    pygame.draw.circle(self.obs_surface, self.obs_color, (x, y), radius)
                    self.get_obs_vertices()
                elif shape_type == 1:
                    width = int(size)
                    height = int(size)
                    color = (random.randrange(256), random.randrange(256), random.randrange(256))
                    x = random.randrange(0, self.width - width)
                    y = random.randrange(0, self.height - height)
                    pygame.draw.rect(self.obs_surface, self.obs_color, (x, y, width, height))
                    self.get_obs_vertices()
                elif shape_type == 2:
                    # 绘制椭圆
                    width = int(size)
                    height = int(size)//2
                    x = random.randrange(0, self.width - width)
                    y = random.randrange(0, self.height - height)
                    pygame.draw.ellipse(self.obs_surface, self.obs_color, (x, y, width, height))
                    self.get_obs_vertices()
                elif shape_type == 3:
                    # 绘制菱形
                    side_length = int(size)
                    x = random.randrange(0, self.width - side_length)
                    y = random.randrange(0, self.height - side_length)
                    diamond_points = [(x + side_length // 2, y), (x + side_length, y + side_length // 2),
                                      (x + side_length // 2, y + side_length), (x, y + side_length // 2)]
                    pygame.draw.polygon(self.obs_surface, self.obs_color, diamond_points)
                    self.get_obs_vertices()
                elif shape_type == 4:
                    width = int(size)
                    height = int(size)//2
                    color = (random.randrange(256), random.randrange(256), random.randrange(256))
                    x = random.randrange(0, self.width - width)
                    y = random.randrange(0, self.height - height)
                    self.get_obs_vertices()
                    pygame.draw.rect(self.obs_surface, self.obs_color, (x, y, width, height))
    # 生成迷宫
    def generate_maze(self,para):

        maze_size = para

        maze_width=int(920/int(maze_size))
        maze_height=int(390/int(maze_size))
        # 生成迷宫障碍物的函数
        maze_generator = MazeGenerator(maze_width,maze_height, 920, 390)
        # 使用MazeGenerator的方法
        maze = maze_generator.generate_maze()
        maze_generator.render_maze(maze,self.obs_surface,self.obs_color)
        self.get_obs_vertices()
        print(maze_width)
        # pygame.draw.circle(self.obs_surface, (255, 0, 0), self.end_point, self.obs_radius)
        # pygame.draw.circle(self.obs_surface, (0, 255, 0), self.start_point, self.obs_radius)




# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         # 设置窗口标题
#         self.setWindowTitle('Pygame in PyQt')
#
#         # 创建Pygame部件
#         self.pygame_widget = PygameWidget()
#
#         # 创建布局
#         layout = QVBoxLayout()
#         layout.addWidget(self.pygame_widget)
#
#         # 创建主窗口部件
#         main_widget = QWidget()
#         main_widget.setLayout(layout)
#         self.setCentralWidget(main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
