import sys
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtCore import QTimer
import random
import time
# from pygame import time

from arithmetic.Astar.Map import Map
from arithmetic.Astar.astar import astar

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class PygameWidget(QWidget):
    BACK_COLOR = WHITE
    OBS_COLOR = BLACK
    OBS_RADIUS = 10

    def __init__(self, main_window, parent=None):
        super(PygameWidget, self).__init__(parent)

        # 设置窗口大小
        self.width, self.height = 920, 390
        self.setMinimumSize(self.width, self.height)

        # 障碍物以及起始点大小
        self.cell_size = 10

        # 初始化pygame
        pygame.init()

        # 设置主平面 设置主平面，障碍物平面和路径规划平面
        self.surface = pygame.Surface((self.width, self.height))
        self.obs_surface = pygame.Surface((self.width, self.height))
        self.plan_surface = pygame.Surface((self.width, self.height))

        # 设置障碍物平面和路径规划平面的透明色
        self.obs_surface.set_colorkey(self.BACK_COLOR)
        self.plan_surface.set_colorkey(self.BACK_COLOR)
        self.obs_surface.fill(self.BACK_COLOR)
        self.plan_surface.fill(self.BACK_COLOR)

        # 创建一个空的绘制障碍物列表
        self.obstacles = []

        # 障碍物列表
        self.block_map = []
        # 地图列表
        self.rows = self.width // self.cell_size
        self.cols = self.height // self.cell_size

        # 初始化地图
        self.map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        # 起始点和终点
        self.start_point = None
        self.end_point = None

        # 创建一个定时器，用于更新界面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)  # 设置帧率为60
        self.win_main = main_window
        self.result = None
        self.search = None

    def startPath(self):
        self.result = None
        self.obs_surface.fill(PygameWidget.BACK_COLOR)
        self.search = astar(self)
        self.result = self.search.process()
        # self.plan_surface=self.search.process()()[1]

    # 鼠标点击事件处理
    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.obs_surface.fill(PygameWidget.BACK_COLOR)
        if event.button() == Qt.LeftButton:  # 鼠标左键
            if (x, y) != self.start_point and (x, y) != self.end_point:
                # 将鼠标点击的位置对齐到网格上
                x = (x // self.cell_size) * self.cell_size
                y = (y // self.cell_size) * self.cell_size
                if (x, y) not in self.obstacles:
                    self.obstacles.append((x, y))
                    self.map[x // self.cell_size][y // self.cell_size] = 1
                    print(self.map)
                    self.win_main.printf("设置障碍物", x // self.cell_size, y // self.cell_size)
                    self.update()
                else:
                    self.obstacles.remove((x, y))
                    self.map[x // self.cell_size][y // self.cell_size] = 0
                    print(self.map)
                    self.win_main.printf("取消障碍物", x // self.cell_size, y // self.cell_size)
                    self.update()
        elif event.button() == Qt.RightButton:  # 鼠标右键
            # 将鼠标点击的位置对齐到网格上
            x = (x // self.cell_size) * self.cell_size
            y = (y // self.cell_size) * self.cell_size
            if self.start_point is None:
                if (x, y) not in self.obstacles:
                    self.start_point = (x, y)
                    print(self.start_point)
                    self.win_main.printf("设置起点", x // self.cell_size, y // self.cell_size)
            else:
                if self.start_point != (x, y) and self.end_point == None:
                    if (x, y) not in self.obstacles:
                        self.end_point = (x, y)
                        print(self.end_point)
                        self.win_main.printf("设置终点", x // self.cell_size, y // self.cell_size)

    # 绘制pygame界面
    def paintEvent(self, event):
        # 创建一个新的surface
        # screen = pygame.Surface((self.width, self.height))
        #
        # # 设置颜色
        # WHITE = (255, 255, 255)
        #
        # # 设置背景颜色
        # screen.fill(WHITE)

        if self.result is not None:
            for k in self.result:
                pygame.draw.rect(self.obs_surface, (0, 100, 255), (k.x, k.y, self.cell_size, self.cell_size), 0)
        # 绘制障碍物
        for obstacle in self.obstacles:
            pygame.draw.rect(self.obs_surface, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)

        # 绘制起始点和终点
        if self.start_point:
            pygame.draw.rect(self.obs_surface, (0, 255, 0),
                             (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
        if self.end_point:
            pygame.draw.rect(self.obs_surface, (255, 0, 0),
                             (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)
        self.surface.fill(PygameWidget.BACK_COLOR)
        self.surface.blit(self.plan_surface, (0, 0))
        self.surface.blit(self.obs_surface, (0, 0))
        # if openList:
        #     for k in openList:
        #         pygame.draw.rect(screen, (150, 0, 0), (k.x, k.y, self.cell_size, self.cell_size), 0)
        # if closeList:
        #     for k in closeList:
        #         pygame.draw.rect(screen, (150, 150, 150), (k.x, k.y, self.cell_size, self.cell_size), 0)

        # print(k[0],k[1])
        # 将pygame surface转换为QImage
        buffer = self.surface.get_buffer()
        img_data = buffer.raw
        del buffer
        image = QImage(img_data, self.width, self.height, QImage.Format_RGB32)

        # 将QImage转换为QPixmap
        pixmap = QPixmap.fromImage(image)

        # 使用QPainter绘制pixmap
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

    def paintAstar(self, openList, closeList):
        # 创建一个新的surface
        self.plan_surface = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        self.plan_surface.fill(WHITE)
        print("进入绘制")
        # 绘制障碍物
        if openList:
            # print(openList)
            for k in openList:
                pygame.draw.rect(self.plan_surface, (150, 0, 0), (k.x, k.y, self.cell_size, self.cell_size), 0)
        if closeList:
            # print(closeList)
            for k in closeList:
                pygame.draw.rect(self.plan_surface, (150, 150, 150), (k.x, k.y, self.cell_size, self.cell_size), 0)
        self.surface.blit(self.plan_surface, (0, 0))
        QWidget().repaint()
        #time.sleep(0.1)
    # 画起始点
    def painting_ori(self, x, y):
        # 绘画起点 这个和点击画起始点功能冲突 暂时分隔这两个功能，假设输入起始点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)
        self.start_point = (x, y)
        self.win_main.printf("设置起点", x, y)
        if self.start_point:
            pygame.draw.rect(screen, (0, 255, 0),
                             (self.start_point[0], self.start_point[1], self.cell_size, self.cell_size), 0)
            image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

            # 将QImage转换为QPixmap
            pixmap = QPixmap.fromImage(image)

            # 使用QPainter绘制pixmap
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            # grid_widget.painting_ori(x,y)

    def painting_end(self, x1, y1):
        # 绘画终点 假设输入终止点前地图为空，所以直接填色即可
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)
        self.end_point = (x1, y1)
        self.win_main.printf("设置终点", x1, y1)
        if self.end_point:
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.end_point[0], self.end_point[1], self.cell_size, self.cell_size), 0)
            image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

            # 将QImage转换为QPixmap
            pixmap = QPixmap.fromImage(image)

            # 使用QPainter绘制pixmap
            painter = QPainter(self)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            # grid_widget.painting_end(x1,y1)

    def random_obstacles(self, x1, y1, x2, y2):
        # 随机生成连续障碍物点
        for i in range(3):
            x = random.randint(x1, x2)
            y = random.randint(y1, y2)
            z = random.randint(10, 15)
            for j in range(z):
                if (x, y) != self.start_point and (x, y) != self.end_point:
                    if (x, y) not in self.obstacles:
                        self.obstacles.append((x, y))
                        x = x + 1
        for i in range(4):
            x = random.randint(x1, x2)
            y = random.randint(y1, y2)
            z = random.randint(10, 15)
            for j in range(z):
                if (x, y) != self.start_point and (x, y) != self.end_point:
                    if (x, y) not in self.obstacles:
                        self.obstacles.append((x, y))
                        y = y + 1
        self.paint_block(x1, y1, x2, y2)

    def paint_block(self, x1, y1, x2, y2):

        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)

        for obstacle in self.obstacles:
            pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], self.cell_size, self.cell_size), 0)

        # 将pygame surface转换为QImage
        image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

        # 将QImage转换为QPixmap
        pixmap = QPixmap.fromImage(image)

        # 使用QPainter绘制pixmap
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        # grid_widget.paint_block(x1, y1, x2, y2)

    # 修改地图分辨率
    def modifyMap(self, size):
        if self.start_point is None and self.end_point is None and len(self.obstacles) == 0:
            if isinstance(size, str) != True:
                self.win_main.printf("请输入正确的分辨率！", None, None)
                if int(size) > 0:
                    new_size = int(size)
                    self.cell_size = new_size
                    self.update()
                    self.win_main.printf("分辨率调整成功！", None, None)
                else:
                    self.win_main.printf("请输入正确的分辨率！", None, None)
        else:
            self.win_main.printf("当前地图已起始点或障碍点不可调整地图分辨率，请清空地图后再次调整分辨率！", None, None)

    # 默认地图
    def defaultMap(self):
        if self.start_point is None and self.end_point is None and len(self.obstacles) == 0:
            if self.cell_size == 10:
                self.win_main.printf("该地图已经是默认地图！", None, None)
            else:
                self.cell_size = 10
                self.win_main.printf("分辨率调整成功！", None, None)
                self.update()
        else:
            self.win_main.printf("当前地图已规划结果不可调整地图分辨率,请清空地图后再次操作", None, None)

    # 随机起始点方法
    def generateRandomStart(self):
        if self.start_point is None:
            # 生成随机的x和y坐标
            x = random.choice(range(0, self.width - 1, 5))
            y = random.choice(range(0, self.height - 1, 5))
            if (x, y) not in self.obstacles:
                self.start_point = (x, y)
                self.win_main.printf("添加起始点：", x, y)
                self.update()
        else:
            self.win_main.printf("error: 已经设置起点！", None, None)

        if self.end_point is None and self.end_point != self.start_point:
            # 生成随机的x和y坐标
            x_1 = random.choice(range(0, self.width - 1, 5))
            y_1 = random.choice(range(0, self.height - 1, 5))
            if (x_1, y_1) not in self.obstacles:
                self.end_point = (x_1, y_1)
                self.win_main.printf("添加终点：", y_1, x_1)
                self.update()
        else:
            self.win_main.printf("error: 已经设置终点！", None, None)
        self.update()

    # 清空地图方法
    def clear_map(self):

        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.obstacles = []  # 清空障碍物列表
        self.map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.result = None
        self.win_main.printf("已经清空地图", None, None)
        self.surface.fill(PygameWidget.BACK_COLOR)
        self.obs_surface.fill(PygameWidget.BACK_COLOR)
        self.plan_surface.fill(PygameWidget.BACK_COLOR)
        self.update()  # 更新界面

    # 清空地图起始点
    def clearStartAndEnd(self):
        self.start_point = None  # 清除起点
        self.end_point = None  # 清除终点
        self.win_main.printf("已经清空起始点", None, None)
        self.update()  # 更新界面


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle('Pygame in PyQt')

        # 创建Pygame部件
        self.pygame_widget = PygameWidget()

        # 创建布局
        layout = QVBoxLayout()
        layout.addWidget(self.pygame_widget)

        # 创建主窗口部件
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
