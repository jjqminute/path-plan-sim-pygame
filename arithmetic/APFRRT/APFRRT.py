import math
import time
import random

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from shapely.geometry import Point, Polygon
import pygame
from shapely.ops import nearest_points

from arithmetic.APFRRT.Node import point


class APFRRT():
    def __init__(self, mapdata):
        self.start = point(mapdata.start_point[0], mapdata.start_point[1])  # 储存此次搜索的开始点
        self.end = point(mapdata.end_point[0], mapdata.end_point[1])  # 储存此次搜索的目的点
        # self.Map = mapdata.map  # 一个二维数组，为此次搜索的地图引用
        self.result = []  # 当计算完成后，将最终得到的路径写入到此属性中
        self.count = 0  # 记录此次搜索所搜索过的节点数
        self.width = mapdata.width
        self.height = mapdata.height
        self.obstacles = mapdata.obstacles  # 多边形障碍物顶点
        #全局障碍物信息
        self.obstacle = mapdata.obs_surface
        # APF参数
        self.attraction_coeff = 5.0  # 吸引力系数
        self.repulsion_coeff = 1000.0  # 斥力系数
        self.repulsion_threshold = 500  # 斥力作用距离阈值
        # 检测震荡参数
        self.position_history = []  # 用于存储历史位置的列表
        self.history_size = 100  # 检测震荡时的点是否大于这个值
        self.oscillation_detection_threshold = 3  # 震荡检测阈值
        # RRT参数
        #self.step = 10
        self.tree = []
        self.step = 15
        #最大迭代次数
        self.max_iterations = 10000
        #动态调整参数
        self.falsecount=0

    def distance(self, point1, point2):
        # 计算两点直接的距离
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def calculate_gradient(self, current_point):
        # 根据人工势场计算当前位置的梯度向量
        dx = self.end.x - current_point.x
        dy = self.end.y - current_point.y
        distance_to_goal = math.sqrt(dx ** 2 + dy ** 2)
        if distance_to_goal > 0:
            gradient_x = dx / distance_to_goal * self.attraction_coeff
            gradient_y = dy / distance_to_goal * self.attraction_coeff
        else:
            gradient_x = gradient_y = 0
        return gradient_x, gradient_y

    def calculate_repulsion(self, current_point):
        # 根据障碍物斥力计算当前位置的斥力向量
        force_x = force_y = 0.0
        closest_distance = float('inf')  # 初始化最近距离为无穷大
        for obstacle in self.obstacles:
            # 多边形
            obs = Polygon(obstacle)
            # 当前点
            pos = Point(current_point.x, current_point.y)
            # if obs.contains(pos):
            #     continue
            # 寻找最近的障碍物点
            nearest_pt = nearest_points(pos, obs)[1]
            # 计算障碍物距离
            distance_to_obstacle = pos.distance(obs)
            force=0
            # 如果距离小于障碍物影响范围
            if distance_to_obstacle < self.repulsion_threshold:
                if distance_to_obstacle < closest_distance:
                    closest_distance = distance_to_obstacle
                # 计算机器人当前位置指向障碍物边界的单位向量
                dx = nearest_pt.x - current_point.x
                dy = nearest_pt.y - current_point.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    force = self.repulsion_coeff * (1.0 / distance_to_obstacle - 1.0 / self.repulsion_threshold) / (
                        distance_to_obstacle ** 2)
                # 计算斥力的大小
                else:
                    force_x -= 0
                    force_y -= 0

                # 累积斥力的分量
                force_x -= force * dx
                force_y -= force * dy
        # if closest_distance < 20:
        #     self.step = max(8, self.step-1)  # 举例：减小步长
        # else:
        #     self.step = min(20, self.step + 5)  # 举例：增加步长
        return force_x, force_y

    def rand_point(self, current_point):
        # 根据人工势场梯度信息和斥力信息选择随机点
        gradient_x, gradient_y = self.calculate_gradient(current_point)
        repulsion_x, repulsion_y = self.calculate_repulsion(current_point)

        # 考虑势场影响和斥力影响，动态调整随机点的偏移量
        total_force_x = gradient_x + repulsion_x
        total_force_y = gradient_y + repulsion_y

        #print ("合力为：")
        #print (total_force_x, total_force_y)
        # 计算随机点的偏移量
        magnitude = math.sqrt(total_force_x ** 2 + total_force_y ** 2)
        if magnitude > 0 and (total_force_x >0.5or total_force_y >0.5):
            # 根据势场和斥力的合力方向调整随机点的偏移量
            offset_factor = 1.2
            #随机性更强
            #random_x = (current_point.x + offset_factor * total_force_x * random.uniform(0.5, 1.0))*self.step*0.2
            #random_y = (current_point.y + offset_factor * total_force_y * random.uniform(0.5, 1.0))*self.step*0.2
            #APF步长更大
            random_x = (current_point.x + offset_factor * total_force_x *self.step*0.1*random.uniform(0.5, 1.0))
            random_y = (current_point.y + offset_factor * total_force_y *self.step*0.1*random.uniform(0.5, 1.0))
            #random_x = (current_point.x + offset_factor * total_force_x * random.uniform(0.5, 1.0))
            #random_y = (current_point.y + offset_factor * total_force_y * random.uniform(0.5, 1.0))
        # 如果即将或已陷入局部极小值
        else:
            self.falsecount+=1
            #如果尝使的次数变多，增加步长
            # if(self.falsecount>=5):
            #     self.step+=5
            #     self.falsecount=0

            # 如果合力为0，随机选择一个点
            random_x = random.uniform(0,self.width)
            random_y = random.uniform(0,self.height)
        if self.collision((current_point.x,current_point.y),(random_x,random_y)):
            print ("随机点")
            self.falsecount += 1
            random_x ,random_y = self.random_nodes()
        return point(random_x, random_y)
    def random_nodes(self):
        random_x = random.uniform(self.width-self.end.x, self.width)
        random_y = random.uniform(0, self.height)
        return random_x, random_y
    def nearest_neighbor(self, tree, target_point):
        """
        在树中寻找最接近目标点的节点。

    Args:
    - tree: 表示树中节点的点列表。
    - target_point: 要查找最近邻节点的目标点 (x, y)。

    Returns:
    - nearest_node: 树中距离目标点最近的节点。
        """
        nearest_node = None
        min_distance = float('inf')
        for node in tree:
            distance = self.dist((node.x, node.y), target_point)
            if distance < min_distance:
                min_distance = distance
                nearest_node = node
        return nearest_node

    def dist(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def steer(self, nearest_node, target_point, max_distance):
        """
        从最近节点朝目标点直线扩展，直到最大距离。

        Args:
        - nearest_node: 最近节点到目标点。
        - target_point: 要朝向的目标点 (x, y)。
        - max_distance: 最大扩展距离。

        Returns:
        - new_node: 从最近节点到达的新节点。
        """
        distance = self.dist((nearest_node.x, nearest_node.y), target_point)
        if distance <= max_distance:

            return point(target_point[0], target_point[1])
        else:
            direction = self.normalize(target_point[0] - nearest_node.x, target_point[1] - nearest_node.y)
            new_x = nearest_node.x + direction[0] * max_distance
            new_y = nearest_node.y + direction[1] * max_distance
            return point(new_x, new_y)

    def normalize(self, vx, vy):
        """
        将输入向量标准化，并返回单位向量。

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

    def expand(self, tree, max_distance):
        """
        扩展 RRT 树，添加一个新节点。

        Args:
        - tree: 表示树中节点的点列表。
        - obstacles: 障碍物列表（如 pygame surfaces）。
        - max_distance: 从最近节点扩展的最大距离。

        Returns:
        - new_node: 添加到树中的新节点，如果扩展失败则返回None。
        """
        current_node =tree[-1]
        # 1. 随机抽样一个点
        random_point = self.rand_point(current_node)

        # 2. 找到树中距离随机点最近的节点
        nearest_node = self.nearest_neighbor(tree, (random_point.x, random_point.y))

        # 3. 从最近节点向随机点扩展
        new_node = self.steer(nearest_node, (random_point.x, random_point.y), max_distance)
        new_node.father = nearest_node
        # 4. 检查是否与障碍物发生碰撞
        if not self.collision((nearest_node.x, nearest_node.y), (new_node.x, new_node.y)):
            # 如果没有碰撞，则将新节点添加到树中
            tree.append(new_node)
            return new_node
        else:
            # 如果发生碰撞，则返回 None 表示扩展失败

            return None

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
        vx, vy = self.normalize(dst[0] - src[0], dst[1] - src[1])
        curr = list(src)
        if curr[0]<0 or curr[0]>=self.width or curr[1]<0 or curr[1]>=self.height:
            return True
        while self.dist(curr, dst) > 1:
            int_curr = int(curr[0]), int(curr[1])
            if int_curr[0] < 0 or int_curr[0] >= self.width or int_curr[1] < 0 or int_curr[1] >= self.height:
                return True
            if self.obstacle.get_at(int_curr) == (0, 0, 0):
                print("障碍物！！！！！！！！！！！！")
                return True
            curr[0] += vx
            curr[1] += vy
        return False

    def cubic_bezier(self,p0, p1, p2, p3, t):
        """
        计算三次贝塞尔曲线上的一个点。
        """
        x = (1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t ** 2 * p2.x + t ** 3 * p3.x
        y = (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t ** 2 * p2.y + t ** 3 * p3.y
        return point(x, y)

    def smooth_path_bezier(self,original_path, num_points=100):
        """
        对给定路径应用三次贝塞尔曲线平滑。
        """
        if len(original_path) < 4:
            raise ValueError("Path must contain at least 4 points for cubic bezier curve smoothing.")

        smoothed_path = []
        # 将路径分为多个段，每四个点为一组来定义一个贝塞尔曲线
        for i in range(0, len(original_path) - 3, 3):
            p0, p1, p2, p3 = original_path[i:i + 4]
            for t in np.linspace(0, 1, num_points):
                bezier_point = self.cubic_bezier(p0, p1, p2, p3, t)
                smoothed_path.append(bezier_point)

        return smoothed_path

    def plan(self, plan_surface):
        """
        执行 RRT 算法，寻找从起点到目标点的路径。

        Args:
        - obstacles: 障碍物列表（如 pygame surfaces）。
        - max_iterations: 运行 RRT 算法的最大迭代次数。
        - max_distance: 从最近节点扩展的最大距离。

        Returns:
        - path: 表示 RRT 算法找到的路径的点列表，如果找不到路径则返回空列表。
        """
        start = time.time()
        # 使用起始节点初始化树
        tree = [self.start]
        max_iterations = self.max_iterations
        max_distance = self.step
        # 执行 RRT 迭代
        for i in range(max_iterations):
            # 1. 扩展树，添加一个新节点
            if i == max_iterations-1:
                print("Maximum达到迭代上限！！！！！！")
                break
            new_node = self.expand(tree, max_distance)
            current_node = new_node
            if current_node:
                pygame.draw.circle(plan_surface, (0, 100, 255), (current_node.x, current_node.y), 2)
                QApplication.processEvents()
            # 2. 检查是否达到目标点
            if new_node and self.is_goal_reached(new_node, (self.end.x, self.end.y), max_distance):

                path = [self.end]  # 确保路径以目标点结束

                while current_node is not None:
                    path.append(current_node)
                    pygame.draw.line(plan_surface, (255, 0, 0), (current_node.x, current_node.y),
                                     (current_node.x, current_node.y), 4)
                    current_node = current_node.father


                path.append(self.start)  # 确保路径以起始点开始
                path.reverse()
                middtimer = time.time()
                print("路径规划花费时间为")
                print(middtimer - start)
                smoothed_path = self.smooth_path_bezier(path, 100)
                smoothed_path.append(self.end)
                for k in smoothed_path:
                    pygame.draw.circle(plan_surface, (255, 100, 255), (k.x, k.y), 2)
                QApplication.processEvents()
                # 如果达到目标，则构建并返回路径
                # path = [new_node]
                # current_node = new_node
                # print(new_node)
                #
                # pygame.draw.circle(plan_surface, (0, 100, 255), (current_node.x, current_node.y), 2)
                # pygame.draw.line(plan_surface, (255, 0, 0), (current_node.x, current_node.y),
                #                  (self.end.x, self.end.y), 4)
                # QApplication.processEvents()
                #
                # while current_node != self.start:
                #     # 最终节点回溯整条路径
                #     parent = current_node.father
                #
                #     pygame.draw.line(plan_surface, (255, 0, 0), (parent.x, parent.y),
                #                      (current_node.x, current_node.y), 4)
                #     QApplication.processEvents()
                #
                #     path.append(parent)
                #     current_node = parent

                path.reverse()
                end = time.time()
                print("总花费时间为")
                print(end - start)
                return path,middtimer - start

            # 绘制过程中的点和线
            if new_node:
                pygame.draw.circle(plan_surface, (0, 100, 255), (new_node.x, new_node.y), 2)
                pygame.draw.line(plan_surface, (0, 100, 255), (new_node.father.x, new_node.father.y),
                                 (new_node.x, new_node.y), 2)
                QApplication.processEvents()  # 强制Qt处理事件队列（重绘）
        # 如果最大迭代次数后仍未找到路径，则返回空路径
        print("未找到路径！！！")
        endtime=time.time()
        return [],start-endtime
