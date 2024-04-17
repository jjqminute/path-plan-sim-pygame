import geojson
import numpy as np
import matplotlib.pyplot as plt
import math

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from shapely import Polygon


def load_demo(fileName):
    """
    加载result_demo(路径规划问题结果类)
    :param fileName:
    :return:
    """
    with open(fileName, 'r') as file:
        geojson_str = file.read()
    geojson_obj = geojson.loads(geojson_str)
    obstacles = []
    for feature in geojson_obj['features']:
        geometry = feature['geometry']
        properties = feature['properties']
        if geometry['type'] == 'Point' and properties['name'] == "\u8d77\u59cb\u70b9":
            start_point = geometry['coordinates']
        if geometry['type'] == 'Point' and properties['name'] == "\u7ec8\u70b9":
            end_point = geometry['coordinates']
        elif geometry['type'] == 'Polygon':
            obstacles.append(Polygon(geometry['coordinates'][0]))
    time = geojson_obj['time']
    track = geojson_obj['track']
    smoothness = geojson_obj['smoothness']
    pathlen = geojson_obj['pathlen']
    return result_demo(start=start_point, end=end_point, time=time, obstacles=obstacles, track=track,
                       smoothness=smoothness, pathlen=pathlen)


class result_demo:
    """
    路径规划结果类
    """

    def __init__(self, start, end, time, obstacles, track, smoothness=None, pathlen=0):
        """
        路径规划的结果分析类
        :param start: 起点 [x,y]
        :param end: 终点 [x,y]
        :param time: 时间
        :param obstacles: 障碍物 Polygon[]
        :param track: 路径 [(x,y),(x,y)...]
        :param smoothness: 平滑度
        :param pathlen: 路径的长度
        """
        self.start = start
        self.end = end
        self.time = time
        self.obstacles = obstacles
        self.track = track
        self.smoothness = smoothness
        if smoothness is None:
            self.compute_smoothness()
        self.pathlen = pathlen
        if pathlen == 0:
            self.calculate_path_length()

    def draw_start(self):
        """
        画出起点
        :return:
        """
        plt.scatter(self.start[0], self.start[1], marker='o', color='blue', s=20)

    def draw_end(self):
        """
        画出终点
        :return:
        """
        plt.scatter(self.end[0], self.end[1], marker='*', color='red', s=20)

    def draw_obstacles(self):
        """
        画障碍物
        :return:
        """
        for polygon in self.obstacles:
            x, y = polygon.exterior.xy
            plt.plot(x, y, color='black')
            plt.fill(x, y, alpha=1, color='black')

    def draw_track(self):
        """
        画出路径
        :return:
        """
        figure = plt.figure()
        self.draw_end()
        self.draw_start()
        self.draw_obstacles()
        a = [x for (x, y) in self.track]
        b = [y for (x, y) in self.track]
        plt.gca().invert_yaxis()
        plt.gca().xaxis.tick_top()  # 将x轴刻度显示在上方
        plt.plot(a, b)
        return FigureCanvas(figure)

    # -----------------------计算路径平滑度-----------------------------------
    def compute_curvature(self, x, y):
        """计算曲率"""
        # 计算每个点前后两点之间的斜率
        slopes = np.diff(y) / np.diff(x)

        # 计算曲率，这里使用曲率的定义 k = |dy/dx| / (1 + (dy/dx)^2)^(3/2)
        curvature = np.abs(slopes) / np.sqrt(1 + slopes ** 2)
        return curvature

    def compute_smoothness(self):
        """计算路径平滑度"""
        path_x = [x for (x, y) in self.track]
        path_y = [y for (x, y) in self.track]
        # 计算曲率
        curvature = self.compute_curvature(path_x, path_y)

        # 计算平均曲率作为路径平滑度的指标
        average_curvature = np.mean(curvature)
        self.smoothness = average_curvature
        print(f"路径平滑度: {self.smoothness}")

    def draw_curvature(self):
        # 绘制曲率
        path_x = [x for (x, y) in self.track]
        path_y = [y for (x, y) in self.track]
        t = np.linspace(0, self.time, len(path_x))
        plt.plot(t[1:], self.compute_curvature(path_x, path_y), marker='o', color='r')

        plt.title("curvature")
        plt.xlabel("X")
        plt.ylabel("curvature")

        plt.tight_layout()
        plt.show()

    # -----------------------------------计算路径长度-------------------------------
    def calculate_path_length(self):
        # 计算路径长度

        for i in range(len(self.track) - 1):
            # 计算相邻两点之间的欧几里得距离
            dx = self.track[i + 1][0] - self.track[i][0]
            dy = self.track[i + 1][1] - self.track[i][1]
            distance = math.sqrt(dx * dx + dy * dy)
            # 累加到路径长度
            self.pathlen += distance
        print(f"路径长度为:{self.pathlen}")
