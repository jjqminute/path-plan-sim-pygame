import math
import time
from random import random
import pygame
from PyQt5.QtWidgets import QApplication
from scipy.spatial import KDTree
import copy
from .Node import point
import heapq




class prm:
    def __init__(self, mapdata):
        self.start = point(mapdata.start_point[0], mapdata.start_point[1])
        self.end = point(mapdata.end_point[0], mapdata.end_point[1])
        self.result = []
        self.width = mapdata.width
        self.height = mapdata.height
        self.obstacle = mapdata.obs_surface
        self.max_point_num = 1000
        self.nodes = [self.start, self.end]
        self.edges = []
        self.step = 30



    def dist(self, p1, p2):
        # 两点距离
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def collision(self, src, dst):
        """
            检查从源点到目标点的线段是否与障碍物发生碰撞。

            Args:
            - src: 源点的坐标 (x1, y1)。
            - dst: 目标点的坐标 (x2, y2)。
            - obstacles: 障碍物表面（如 pygame surface）。

            Returns:
            - collided: 如果发生碰撞，则为 True，否则为 False。
            """
        vx, vy = self.normalize(dst.x - src.x, dst.y - src.y)
        curr = copy.deepcopy(src)
        while self.dist(curr, dst) > 1:
            int_curr = int(curr.x), int(curr.y)
            if self.obstacle.get_at(int_curr) == (0, 0, 0):
                return True
            curr.x += vx
            curr.y += vy
        return False

    # 方向向量
    def normalize(self, vx, vy):
        """
        将输入向量标准化，并返回其坐标。

        Args:
        - vx: 向量的 x 坐标分量。
        - vy: 向量的 y 坐标分量。

        Returns:
        - normalized_vx: 标准化后的 x 坐标分量。
        - normalized_vy: 标准化后的 y 坐标分量。
        """
        norm = math.sqrt(vx * vx + vy * vy)
        if norm > 1e-6:
            normalized_vx = vx / norm
            normalized_vy = vy / norm
        else:
            normalized_vx = 0
            normalized_vy = 0
        return normalized_vx, normalized_vy

    def generate_random_points(self):
        x = random() * self.width
        y = random() * self.height
        return point(x, y)

    def is_obstacle(self, current):
        int_curr = int(current.x), int(current.y)
        if self.obstacle.get_at(int_curr) == (0, 0, 0):
            return True
        else:
            return False

    def connect_nodes(self):
        # 使用KD树快速搜索最近邻节点
        kdtree = KDTree([(node.x, node.y) for node in self.nodes])
        for node in self.nodes:

            # 搜索与当前节点距离小于等于 self.step 的节点,返回索引值
            neighbors = kdtree.query_ball_point((node.x, node.y), self.step)
            for neighbor_idx in neighbors:
                #print("节点",node)
                neighbor = self.nodes[neighbor_idx]
                if not self.collision(node, neighbor):
                    #print("节点", node)
                    self.edges.append((node, neighbor))
                    #print("Edge:", node, "->", neighbor)
            #print("-----------------------------------------------------------------")  # 打印边

    def dijkstra(self):
        # 使用 Dijkstra 算法找到最短路径
        distances = {node: float('inf') for node in self.nodes}
        distances[self.start] = 0
        queue = [(0, self.start)]  # (distance, node)
        while queue:
            dist, current = heapq.heappop(queue)
            if dist > distances[current]:
                continue
            for neighbor in self.get_neighbors(current):
                new_dist = distances[current] + self.dist(current, neighbor)
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    neighbor.parent = current  # 记录路径上的父节点
                    heapq.heappush(queue, (new_dist, neighbor))

        # 构建路径节点列表
        path = []
        current = self.end
        while current != self.start:
            path.append(current)
            current = current.parent
        path.append(self.start)
        path.reverse()
        return path

    def get_neighbors(self, node):
        neighbors = []
        for edge in self.edges:
            if edge[0] == node:
                neighbors.append(edge[1])
            elif edge[1] == node:
                neighbors.append(edge[0])
        return neighbors

    def a_star(self):
        # 使用 A* 算法找到最短路径
        open_set = {self.start}  # 未考虑的节点
        came_from = {}  # 节点的父节点
        g_score = {node: float('inf') for node in self.nodes}
        g_score[self.start] = 0
        f_score = {node: float('inf') for node in self.nodes}
        f_score[self.start] = self.dist(self.start, self.end)

        while open_set:
            current = min(open_set, key=lambda node: f_score[node])
            if current == self.end:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            open_set.remove(current)
            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + self.dist(current, neighbor)
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.dist(neighbor, self.end)
                    if neighbor not in open_set:
                        open_set.add(neighbor)

        return []  # 没有找到路径

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
    def plan_test(self, plan_surface):
        start_time=time.time()
        # 生成随机点
        while len(self.nodes) < self.max_point_num:
            k = self.generate_random_points()
            if not self.is_obstacle(k):
                self.nodes.append(k)
                # QApplication.processEvents()
            # 确保起始点和终点在节点集合中
        if self.start not in self.nodes:
            self.nodes.append(self.start)
        if self.end not in self.nodes:
            self.nodes.append(self.end)
        self.connect_nodes()
        # distances = self.dijkstra()
        # self.visualize_path(distances, plan_surface)
        path = self.a_star()
        end_time=time.time()
        print("时间为",end_time-start_time)
        if path is None:
            print("未找到可行路径！！！！")

        # for i in path:
        #     print(i)
        # self.visualize_path(path, plan_surface)
        return path,end_time-start_time
