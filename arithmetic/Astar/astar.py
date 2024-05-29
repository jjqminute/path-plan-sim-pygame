# 姓名：高翔
# 2024/1/29 11:40
import math
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from .Node import point
import pygame
from shapely.geometry import Point, Polygon, LineString




class astar:  # 核心部分，寻路类
    def __init__(self, mapdata):
        self.start = point(mapdata.start_point[0], mapdata.start_point[1])  # 储存此次搜索的开始点
        self.end = point(mapdata.end_point[0], mapdata.end_point[1])  # 储存此次搜索的目的点
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 当计算完成后，将最终得到的路径写入到此属性中
        self.count = 0  # 记录此次搜索所搜索过的节点数
        self.useTime = 0  # 记录此次搜索花费的时间--在此演示中无意义，因为process方法变成了一个逐步处理的生成器，统计时间无意义。
        self.open.append(self.start)
        self.width = mapdata.width
        self.surface = mapdata.surface
        self.height = mapdata.height
        self.radius = mapdata.obs_radius
        self.cell_size = 10
        self.obstacles = [Polygon(obstacle) for obstacle in mapdata.obstacles]
        self.mapdata = mapdata
        self.screen = mapdata.plan_surface
        # 膨胀障碍物




    # 计算F值
    def cal_F(self, loc):
        print('计算值：', loc)
        G = loc.father.G + loc.cost
        H = self.getEstimate(loc)
        F = G + H
        print("F=%d G=%d H=%d" % (F, G, H))
        return {'G': G, 'H': H, 'F': F}

    def F_Min(self):  # 搜索open列表中F值最小的点并将其返回，同时判断open列表是否为空，为空则代表搜索失败
        if len(self.open) <= 0:
            return None
        t = self.open[0]
        for i in self.open:
            if i.F < t.F:
                t = i
        return t

    def line_intersects_obstacles(self, p1, p2):
        line = LineString([(p1.x, p1.y), (p2.x, p2.y)])
        return any(line.intersects(ob) for ob in self.obstacles)
    def getAroundPoint(self, loc):  # 获取指定点周围所有可通行的点，并将其对应的移动消耗进行赋值。
        directions = [
            (loc.x, loc.y + self.cell_size, 10),
            (loc.x + self.cell_size, loc.y + self.cell_size, 14),
            (loc.x + self.cell_size, loc.y, 10),
            (loc.x + self.cell_size, loc.y - self.cell_size, 14),
            (loc.x, loc.y - self.cell_size, 10),
            (loc.x - self.cell_size, loc.y - self.cell_size, 14),
            (loc.x - self.cell_size, loc.y, 10),
            (loc.x - self.cell_size, loc.y + self.cell_size, 14)
        ]

        valid_points = []
        for direction in directions:
            x, y, cost = direction
            if 0 <= x < self.width and 0 <= y < self.height:
                p = Point(x, y)
                if not any(ob.contains(p) for ob in self.obstacles) and not self.line_intersects_obstacles(loc,p):
                    nt = point(x, y)
                    nt.cost = cost
                    valid_points.append(nt)
        return valid_points

    def distance(self, AS, point2):
        return math.sqrt((AS[0] - point2[0]) ** 2 + (AS[1] - point2[1]) ** 2)

    def check_circle_obstacles(self, center, radius, obstacles):
        valid_points = []
        for obstacle in obstacles:
            # 检查每个障碍物是否在圆形区域内
            if self.distance(center, obstacle) <= radius:
                return False
        return True

    def is_point_in_obstacles(self, p):
        point_obj = Point(p.x, p.y)
        return any(ob.contains(point_obj) for ob in self.obstacles)
    # 此次判断的点周围的可通行点加入到open列表中，如此点已经在open列表中则对其进行判断，如果此次路径得到的F值较之之前的F值更小，
    # 则将其父节点更新为此次判断的点，同时更新F、G值。
    def addToOpen(self, l,
                  father):
        for i in l:
            if i not in self.open:
                if i not in self.close:
                    i.father = father
                    self.open.append(i)
                    r = self.cal_F(i)
                    i.G = r['G']
                    i.F = r['F']
            else:
                tf = i.father
                i.father = father
                r = self.cal_F(i)
                if i.F > r['F']:
                    i.G = r['G']
                    i.F = r['F']
                # i.father=father
                else:
                    i.father = tf

    def getEstimate(self, loc):  # H :从点loc移动到终点的预估花费
        return (abs(loc.x - self.end.x) + abs(loc.y - self.end.y))

    def draw(self, current, open, close):
        self.screen.fill((255, 255, 255))
        path = [current]
        while True:
            current = current.father
            if current != None:
                path.append(current)
            else:
                break
        tagx = True
        if path:
            for k in path:
                # 路径颜色
                tagx = False
                pygame.draw.rect(self.screen, (0, 100, 255), (k.x, k.y, self.cell_size, self.cell_size), 0)
        if tagx:
            tag = True
            for k in open:
                tag = False
                pygame.draw.rect(self.screen, (150, 0, 0), (k.x, k.y, self.cell_size, self.cell_size), 0)
            if tag:
                for k in close:
                    pygame.draw.rect(self.screen, (150, 150, 150), (k.x, k.y, self.cell_size, self.cell_size), 0)
                    break

    def process(self, plan_surface):  # 使用yield将process方法变成一个生成器，可以逐步的对搜索过程进行处理并返回关键数据
        start = time.time()
        print("起点为", self.start)
        print("障碍物", self.obstacles)
        while True:
            self.count += 1
            tar = self.F_Min()  # 先获取open列表中F值最低的点tar
            if tar == None:
                self.result = None
                self.count = -1
                break
            else:
                aroundP = self.getAroundPoint(tar)  # 获取tar周围的可用点列表aroundP
                self.addToOpen(aroundP, tar)  # 把aroundP加入到open列表中并更新F值以及设定父节点
                self.open.remove(tar)  # 将tar从open列表中移除
                self.close.append(tar)  # 已经迭代过的节点tar放入close列表中
                if self.end in self.open or self.getEstimate(tar) < 15:  # 判断终点是否已经处于open列表中
                    e = self.end
                    e.father = tar
                    self.result.append(e)
                    pygame.draw.circle(plan_surface, (0, 100, 255), (e.x, e.y), 2)
                    while True:

                        e = e.father
                        if e == None:
                            break

                        self.result.append(e)
                    # self.mapdata.paintAstar(self.open,self.close)
                    # self.save()
                    # print(result)
                    # yield (tar, self.open, self.close)
                    break
            # self.draw(tar, self.open, self.close)
            # self.mapdata.paintAstar(self.open, self.close)
            # time.sleep(1)  # 暂停
        end = time.time()
        print("花费时间为")
        print(end - start)
        return self.result, end - start
        # self.repaint()
        # print('返回')

        # yield (tar, self.open, self.close)
        # time.sleep(1)  # 暂停
        # self.useTime = time2 - time1
