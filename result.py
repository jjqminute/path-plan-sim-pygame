import json
import os

import geojson
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

from geojson import Feature, FeatureCollection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from shapely import Polygon, Point


def load_demo(file_name):
    """
    加载result_demo(路径规划问题结果类)
    :param file_name:
    :return:
    """
    with open(file_name, 'r') as file:
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
    return Result_Demo(start=start_point, end=end_point, time=time, obstacles=obstacles, track=track,
                       smoothness=smoothness, pathlen=pathlen)


class Result_Demo:
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
        self.time = round(time, 2)
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
        :return:figure
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
        return figure

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
        self.smoothness = round(average_curvature, 2)

    def draw_curvature(self):
        """
        绘制曲率
        :return:figure
        """
        figure = plt.figure()
        path_x = [x for (x, y) in self.track]
        path_y = [y for (x, y) in self.track]
        t = np.linspace(0, self.time, len(path_x))
        plt.plot(t[1:], self.compute_curvature(path_x, path_y), marker='o', color='r')

        plt.title("curvature")
        plt.xlabel("X")
        plt.ylabel("curvature")

        plt.tight_layout()
        return figure

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
        self.pathlen = round(self.pathlen, 2)
        print(f"路径长度为:{self.pathlen}")


class Category_Demo:
    """
    多结果分析:同地图同算法运行多次
    画图:1)路径比较2)平滑度比较
    数据：1)计算平滑度2)计算平均路径长度3)平均用时
    """
    def __init__(self):
        """
        初始化
        """
        self.results = []  # 定义数组类型
        self.file_name = []
        self.name = None
        self.ave_smooth = None
        self.ave_path_length = 0
        self.ave_time = 0
        self.start = []
        self.end = []
        self.obstacles = []

    def read(self, path):
        """
        已知完整路径,从文件中读取category,在category_compare中使用
        :param path:完整路径
        :return:None
        """
        with open(path, 'r') as file:
            geojson_str = file.read()
        geojson_obj = geojson.loads(geojson_str)
        self.name = geojson_obj['name']
        self.ave_smooth = geojson_obj['ave_smooth']
        self.ave_path_length = geojson_obj['ave_path_length']
        self.ave_time = geojson_obj['ave_time']

    def read_file(self, path):
        """
        读取文件，从多个结果文件生成一个category
        :param path: 文件夹的路径
        :return: None
        """
        files = os.listdir(path)
        for file in files:
            self.results.append(load_demo(os.path.join(path, file)))  # 读取结果
            self.file_name.append(file)  # 保存文件名
        # 检查是否在同一地图,此时已经读入,比较起点(point)、终点(point)、障碍物(polygon)
        self.start = self.results[0].start
        self.end = self.results[0].end
        self.obstacles = self.results[0].obstacles
        for result in self.results[1:]:
            if self.start != result.start or self.end != result.end:  # 比较起始点
                raise ValueError("起点或终点不同！")  # 抛出异常
            sorted_group1 = sorted(self.obstacles, key=lambda p: tuple(p.exterior.coords))
            sorted_group2 = sorted(result.obstacles, key=lambda p: tuple(p.exterior.coords))
            if not all(p1.equals(p2) for p1, p2 in zip(sorted_group1, sorted_group2)):
                raise ValueError("障碍物不同！")  # 抛出异常
        self.calculate()

    def save_file(self, file_path, name):
        """
        保存category文件:1)地图 2)算法名 3)平均平滑度 4)平均路径长度 5)平均用时
        :param name: 算法的名称
        :param file_path: 保存的路径
        :return: None
        """
        # 1)地图都是一样的,就直接取出results[0]的就可以,保存地图是为了检验是否在同地图下运行的结果
        obstacles = self.results[0].obstacles
        start_point = self.results[0].start
        end_point = self.results[0].end
        # 2)算法名:name
        self.name = name
        # 3)平均平滑度：self.ave_smooth
        # 4)平均路径长度: self.ave_path_length
        # 5)平均用时：self.ave.time
        features = []
        if obstacles is not None:
            for obstacle in obstacles:
                features.append(
                    geojson.Feature(geometry=obstacle, properties={"name": "障碍物"}))
        if start_point is not None and end_point is not None:
            features.append(Feature(geometry=Point(start_point), properties={"name": "起始点"}))
            features.append(Feature(geometry=Point(end_point), properties={"name": "终点"}))
        feature_collection = FeatureCollection(features)
        # 先封装经过计算再存入文件
        js2 = json.loads(str(feature_collection))
        js = dict(name=name, ave_smooth=self.ave_smooth, ave_path_length=self.ave_path_length, ave_time=self.ave_time)
        js2.update(js)
        # 将FeatureCollection保存为GeoJSON格式的字符串
        geojson_str = json.dumps(js2, indent=4)
        with open(file_path, 'w') as file:
            file.write(geojson_str)

    def track_compare(self):
        """
        绘制不同路径的对比
        :return: figure
        """
        figure = plt.figure()
        self.results[0].draw_obstacles()
        self.results[0].draw_end()
        self.results[0].draw_start()
        plt.gca().invert_yaxis()
        plt.gca().xaxis.tick_top()  # 将x轴刻度显示在上方
        for r, n in zip(self.results, self.file_name):
            a = [x for (x, y) in r.track]
            b = [y for (x, y) in r.track]
            plt.plot(a, b, label=n)
        plt.legend(loc='upper right')
        return figure

    def calculate(self):
        """
        计算
        :return: None
        """
        self.calculate_average_time()
        self.calculate_average_smoothness()
        self.calculate_average_length()

    def calculate_average_smoothness(self):
        """
        求多个结果的平均路径平滑度(保留两位小数)
        :return:None
        """
        total_smoothness = 0
        result_count = len(self.results)
        for r in self.results:
            total_smoothness += r.smoothness
        self.ave_smooth = round(total_smoothness/result_count, 2)

    def calculate_average_length(self):
        """
        求多个结果的平均路径长度(保留两位小数)
        :return:None
        """
        total_length = 0
        result_count = len(self.results)
        for r in self.results:
            total_length += r.pathlen
        self.ave_path_length = round(total_length / result_count, 2)

    def calculate_average_time(self):
        """
        求平均用时(保留两位小数)
        :return:None
        """
        times = [r.time for r in self.results]
        self.ave_time = round(sum(times) / len(times), 2)


class Category_Compare:
    def __init__(self):
        self.category = []
        self.df = None  # 生成的数据表格
        self.start = []
        self.end = []
        self.obstacles = []

    def read_category(self, files):
        """
        读取一系列category文件
        :param files: 完整路径数组
        :return:None
        """
        for file in files:
            category = Category_Demo()
            category.read(file)
            self.category.append(category)
        # 检查是否是同一地图
        self.start = self.category[0].start
        self.end = self.category[0].end
        self.obstacles = self.category[0].obstacles
        for result in self.category[1:]:
            if self.start != result.start or self.end != result.end:  # 比较起始点
                raise ValueError("起点或终点不同！")  # 抛出异常
            sorted_group1 = sorted(self.obstacles, key=lambda p: tuple(p.exterior.coords))
            sorted_group2 = sorted(result.obstacles, key=lambda p: tuple(p.exterior.coords))
            if not all(p1.equals(p2) for p1, p2 in zip(sorted_group1, sorted_group2)):
                raise ValueError("障碍物不同！")  # 抛出异常
        data = {
            'name': [c.name for c in self.category],
            'average time': [c.ave_time for c in self.category],
            'average path length': [c.ave_path_length for c in self.category],
            'average smoothness': [c.ave_smooth for c in self.category]
        }
        self.df = pd.DataFrame(data)

    def save_image(self, file_path):
        df = self.df
        # 创建一个figure和axes对象
        fig, ax = plt.subplots()
        # 去掉x轴和y轴的刻度
        ax.set_xticks([])
        ax.set_yticks([])
        # 使用table函数将DataFrame绘制到axes对象上
        the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        # 自动调整列宽
        the_table.auto_set_column_width(col=list(range(len(df.columns))))
        # 自动调整行高
        the_table.scale(1, 1.5)
        # 隐藏坐标轴
        ax.axis('off')
        # 将figure保存为图片
        canvas = FigureCanvas(fig)
        canvas.print_figure(file_path, dpi=300)

    def save_csv(self, file_path):
        self.df.to_csv(file_path, index=False, encoding='utf-8-sig')
