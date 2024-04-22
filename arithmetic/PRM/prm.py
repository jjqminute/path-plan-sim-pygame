import math
import time
from random import random
import pygame
from PyQt5.QtWidgets import QApplication
from .Node import point
import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

def heuristic(a, b):
    # 启发式函数，用于估算节点a到目标节点b的距离
    # 这里使用欧几里得距离作为启发式函数
    return abs(a.x - b.x) + abs(a.y - b.y)

def a_star_search(graph, start, end):
    # graph是一个字典，键是节点，值是相邻的节点列表
    # start和end分别是起点和终点节点

    frontier = PriorityQueue()
    frontier.put((start, 0), 0)

    came_from = {}  # 记录每个节点是如何到达的
    cost_so_far = {}  # 记录从起点到当前节点的累积代价

    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == end:
            break

        for next in graph[current]:
            new_cost = cost_so_far[current] + graph[current][next]
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, end)
                frontier.put((next, priority), priority)
                came_from[next] = current

    return came_from, cost_so_far
class prm:
    def __init__(self,mapdata):
        self.start = point(mapdata.start_point[0], mapdata.start_point[1])
        self.end = point(mapdata.end_point[0], mapdata.end_point[1])
        self.result = []
        self.width = mapdata.width
        self.height = mapdata.height
        self.obstacle = mapdata.obs_surface
        self.max_point_num=200
        self.nodes=[self.start,self.end]
        self.edges=[]
        self.step=50

    def is_goal_reached(self, node, goal_point, tolerance):
        """
        检查当前节点是否已经接近目标点。

        Args:
        - node: 要检查的当前节点 (点)。
        - goal_point: 要检查的目标点 (x, y)。
        - tolerance: 用于判断是否达到目标的容差距离。

        Returns:
        - reached: 如果达到目标，则为True，否则为False。
        """
        distance_to_goal = self.dist((node.x, node.y), goal_point)
        return distance_to_goal <= tolerance

    def dist(self, p1, p2):
        #两点距离
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
        curr = src
        while self.dist(curr, dst) > 1:
            int_curr = int(curr.x), int(curr.y)
            if self.obstacle.get_at(int_curr) == (0, 0, 0):
                return True
            curr.x += vx
            curr.y += vy
        return False

    #方向向量
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
        return point(x,y)

    def is_obstacle(self,current):
        int_curr = int(current.x), int(current.y)
        if self.obstacle.get_at(int_curr) == (0, 0, 0):
            return True
        else:
            return False

    def connect_nodes(self):
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                if not self.collision(self.nodes[i], self.nodes[j]) and self.dist(self.nodes[j], self.nodes[i])<=self.step:
                    self.edges.append((self.nodes[i], self.nodes[j]))

    def plan(self,plan_surface):
        #生成随机点
        while len(self.nodes) <self.max_point_num:
            k=self.generate_random_points()
            if not self.is_obstacle(k):
                self.nodes.append(k)
                pygame.draw.circle(plan_surface, (0, 100, 255), (k.x, k.y), 2)
                QApplication.processEvents()
        self.connect_nodes()


        for k in self.edges:
            pygame.draw.line(plan_surface, (0, 0, 255), (k[0].x, k[0].y),
                             (k[1].x, k[1].y), 4)

        # 构建图表示，其中节点是self.nodes中的Node实例
        #graph = {}
        # 遍历所有节点
        # for node in self.nodes:
        #     # 获取当前节点的邻居节点列表
        #     neighbors = [
        #         other_node for other_node in self.nodes
        #         if node != other_node and self.collision(node, other_node) and self.dist(node,other_node)<=self.step
        #     ]
        #     # 将当前节点和它的邻居节点列表添加到graph字典中
        #     graph[node] = neighbors
        # start_index = self.nodes.index(self.start)
        # end_index = self.nodes.index(self.end)
        #
        # came_from, cost_so_far = a_star_search(graph, self.start, self.end)
        #
        # # 重建路径
        # path = [self.end]
        # while start_index != end_index:
        #     path.append(came_from[start_index])
        #     start_index = came_from[start_index]

        # path.reverse()  # 反转路径，使其从起点到终点
        # return path
