import math
from numpy import random
import time
import pygame
from PyQt5.QtWidgets import QApplication
from scipy.spatial import KDTree
import copy
from .Node import point
import heapq
from .prm import prm


class iprm(prm):
    def __init__(self, mapdata):
        super().__init__(mapdata)
        D_MIN = 10
        MAX_RAD_POINT_NUM = 10
        self.D_MIN = D_MIN
        self.max_rad_point_num = MAX_RAD_POINT_NUM
    

    def rand_point_radius(self, center, radius):
        theta = random.uniform(0, 2*math.pi)
        r = random.uniform(0, radius)
        x = center.x + r * math.cos(theta)
        y = center.y + r * math.sin(theta)
        x = min(max(x, 0), self.width - 1)
        y = min(max(y, 0), self.height - 1)
        rand_point = point(x, y)
        return rand_point

        
    def visualize_path(self, path, plan_surface):
        if not path:
            return
        for i in range(len(path) - 1):
            pygame.draw.line(plan_surface, (255, 0, 0), (path[i].x, path[i].y), (path[i + 1].x, path[i + 1].y), 2)

    def plan(self, plan_surface):
        start_time=time.time()
        # 生成随机点
        while len(self.nodes) < self.max_point_num:
            k = self.generate_random_points()
            if not self.is_obstacle(k):
                self.nodes.append(k)
                pygame.draw.circle(plan_surface, (0, 100, 255), (int(k.x), int(k.y)), 2)
                QApplication.processEvents()
            else:
                # 在障碍物内部时，以此随机点为中心选点
                # rad_nodes = []
                # while len(rad_nodes) < self.max_rad_point_num:
                d = self.D_MIN
                while True:
                    k = self.rand_point_radius(k, d)
                    if not self.is_obstacle(k):
                        self.nodes.append(k)
                        pygame.draw.circle(plan_surface, (0, 100, 255), (int(k.x), int(k.y)), 2)
                        QApplication.processEvents()
                        break
                    else:
                        d *= 2
                
        # 确保起始点和终点在节点集合中
        if self.start not in self.nodes:
            self.nodes.append(self.start)
        if self.end not in self.nodes:
            self.nodes.append(self.end)
        self.connect_nodes()
        for edge in self.edges:
            pygame.draw.line(plan_surface, (0, 255, 0), (edge[0].x, edge[0].y), (edge[1].x, edge[1].y), 1)
        # distances = self.dijkstra()
        # self.visualize_path(distances, plan_surface)
        path = self.a_star()
        end_time=time.time()
        print("时间为",end_time-start_time)
        if path is None:
            print("未找到可行路径！！！！")

        # for i in path:
        #     print(i)
        self.visualize_path(path, plan_surface)
        return path,end_time-start_time

