import pygame
import random

class MazeGenerator:
    def __init__(self, maze_width, maze_height, screen_width, screen_height):
        self.MAZE_WIDTH = maze_width
        self.MAZE_HEIGHT = maze_height
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        # 颜色定义
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # 初始化Pygame
        pygame.init()

        # 创建屏幕对象
        # self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Maze Generator")

    # 生成迷宫障碍物的函数
    def generate_maze(self):
        maze = [[1] * (self.MAZE_WIDTH + 2) for _ in range(self.MAZE_HEIGHT + 2)]  # 添加一圈边界墙壁

        # 设置起始点和目标点
        start_pos = (1, 1)

        # 生成迷宫障碍物
        def generate_obstacles(pos):
            maze[pos[0]][pos[1]] = 0  # 将当前位置设为通路

            directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]  # 上下左右四个方向
            random.shuffle(directions)  # 随机打乱方向顺序

            for direction in directions:
                next_pos = (pos[0] + direction[0], pos[1] + direction[1])
                if (
                    next_pos[0] > 0 and next_pos[0] <= self.MAZE_HEIGHT and
                    next_pos[1] > 0 and next_pos[1] <= self.MAZE_WIDTH and
                    maze[next_pos[0]][next_pos[1]] == 1
                ):
                    maze[pos[0] + direction[0] // 2][pos[1] + direction[1] // 2] = 0  # 将中间位置设为通路
                    generate_obstacles(next_pos)  # 递归生成路径

        generate_obstacles(start_pos)

        return maze[1:-1]  # 去除边界墙壁

    # 渲染迷宫
    def render_maze(self, maze,screen,color):
        cell_width = self.SCREEN_WIDTH // self.MAZE_WIDTH
        cell_height = self.SCREEN_HEIGHT // self.MAZE_HEIGHT

        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                color = self.WHITE if cell == 0 else self.BLACK
                pygame.draw.rect(screen , color, (x * cell_width, y * cell_height, cell_width, cell_height))


