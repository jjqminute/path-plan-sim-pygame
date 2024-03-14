import math
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from shapely.geometry import Point, Polygon
import pygame
from shapely.ops import nearest_points

from arithmetic.APF.Node import point


class apf:
    def __init__(self, mapdata):
        self.start = point(mapdata.start_point[0], mapdata.start_point[1])  # 储存此次搜索的开始点
        self.end = point(mapdata.end_point[0], mapdata.end_point[1])  # 储存此次搜索的目的点
        # self.Map = mapdata.map  # 一个二维数组，为此次搜索的地图引用
        self.result = []  # 当计算完成后，将最终得到的路径写入到此属性中
        self.count = 0  # 记录此次搜索所搜索过的节点数
        self.width = mapdata.width
        self.height = mapdata.height
        self.obstacles = mapdata.obstacles
        # 参数
        self.attraction_coeff = 3.0  # 吸引力系数
        self.repulsion_coeff = 300.0  # 斥力系数
        self.repulsion_threshold = 500 # 斥力作用距离阈值
        self.obstacle = mapdata.obs_surface

    def distance(self, point1, point2):
        # 计算两点直接的距离
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def calculate_attraction(self, current_point):
        # 计算吸引力向量
        dx = self.end.x - current_point.x
        dy = self.end.y - current_point.y
        distance_to_goal = self.distance(current_point, self.end)

        if distance_to_goal > 0:
            # 向目标的单位向量乘以吸引力系数
            force_x = (dx / distance_to_goal) * self.attraction_coeff
            force_y = (dy / distance_to_goal) * self.attraction_coeff
        else:
            force_x = force_y = 0
        # 返回受到的引力的向量
        return force_x, force_y

    def calculate_repulsion(self, current_point):
        # 计算斥力
        force_x = force_y = 0.0
        for obstacle in self.obstacles:
            obs = Polygon(obstacle)
            pos = Point(current_point.x, current_point.y)
            nearest_pt = nearest_points(pos, obs)[1]
            # 计算障碍物距离
            distance_to_obstacle = pos.distance(obs)
            d0 = self.repulsion_threshold  # 斥力作用距离阈值
            # 如果距离小于障碍物影响范围
            if distance_to_obstacle < self.repulsion_threshold:
                force = self.repulsion_coeff * (1.0 / distance_to_obstacle - 1.0 / self.repulsion_threshold) / (
                            distance_to_obstacle ** 2)
                # 角度
                angle = math.atan2(nearest_pt.y - current_point.y, nearest_pt.x - current_point.x)
                # 累计获得总的方向斥力
                force_x -= force * math.cos(angle)
                force_y -= force * math.sin(angle)
        return force_x, force_y

    def plan(self):
        # 寻找路径的方法
        current_point = self.start
        start_time = time.time()
        while self.distance(current_point, self.end) > 1:
            # 吸引力向量
            attraction_x, attraction_y = self.calculate_attraction(current_point)
            # 斥力向量
            repulsion_x, repulsion_y = self.calculate_repulsion(current_point)

            # 合力向量
            total_force_x = attraction_x + repulsion_x
            total_force_y = attraction_y + repulsion_y

            # 确定下一步的位置
            next_x = current_point.x + total_force_x
            next_y = current_point.y + total_force_y
            next_point = point(next_x, next_y)

            self.result.append((next_point.x, next_point.y))
            current_point = next_point
            self.count += 1

            if self.count > 10000:  # 避免无限循环
                print("没有可行路径或陷入局部极小值点！！！！！！！")
                break;
        end_time = time.time();
        print("花费时间为")
        print(end_time - start_time)
        return self.result;
