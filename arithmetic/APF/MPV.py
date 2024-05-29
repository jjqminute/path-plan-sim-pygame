import math
import time
import random
import queue

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from shapely.geometry import Point, Polygon, LineString
import pygame
from shapely.ops import nearest_points

from arithmetic.APF.Node import point


class Mpv:
    def __init__(self, mapdata):
        super().__init__()
        self.start_point = Point(list(mapdata.start_point))  # 储存此次搜索的开始点
        self.end_point = Point(list(mapdata.end_point))  # 储存此次搜索的目的点
        self.width = mapdata.width
        self.height = mapdata.height
        # self.obstacles = mapdata.obstacles
        self.obs_surface = mapdata.obs_surface
        self.plan_surface = mapdata.plan_surface
        self.boundaries = [LineString([(0, 0), (self.width, 0)]),
                           LineString([(self.width, 0), (self.width, self.height)]),
                           LineString([(self.width, self.height), (0, self.height)]),
                           LineString([(0, self.height), (0, 0)])]
        self.obstacles = mapdata.obstacles
        self.a = queue.Queue()
        self.f = queue.Queue()
        self.f.put(self.start_point)
        self.f.put(self.end_point)
        self.s = queue.Queue()

        self.grid_spacing = 10

    def plan(self, plan_surface):
        while True:
            try:
                item = self.f.get_nowait()
            except queue.Empty:
                break

            # 做最小圆
            # 找最小半径
            min_radius = float("inf")
            for i in self.obstacles:
                distance = item.distance(Polygon(i))
                if distance < min_radius:
                    min_radius = distance
            for i in self.boundaries:
                distance = item.distance(i)
                if distance < min_radius:
                    min_radius = distance
            # pygame.draw.circle(plan_surface, (0, 100, 255), (item.x, item.y), min_radius)

            # 计算并绘制网格点
            for x in range(item.x - min_radius, item.x + min_radius + 1, self.grid_spacing):
                for y in range(item.y - min_radius, item.y + min_radius + 1, self.grid_spacing):
                    # 检查点是否在圆内
                    if math.sqrt((x - item.x) ** 2 + (y - item.y) ** 2) <= min_radius:
                        pygame.draw.circle(plan_surface, (0, 100, 255), (x, y), 1)

        QApplication.processEvents()  # 强制qt处理绘图事件
