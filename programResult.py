import sys
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import QTimer

class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super(PygameWidget, self).__init__(parent)

        # 设置窗口大小
        self.width, self.height = 920, 399
        self.setMinimumSize(self.width, self.height)

        # 初始化pygame
        pygame.init()

        # 创建一个空的障碍物列表
        self.obstacles = []

        # 创建一个定时器，用于更新界面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)  # 设置帧率为60

    # 鼠标点击生成障碍物
    def mousePressEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        # 将鼠标点击的位置对齐到网格上
        x = (x // 40) * 40
        y = (y // 40) * 40
        self.obstacles.append((x, y))

    # 绘制pygame界面
    def paintEvent(self, event):
        # 创建一个新的surface
        screen = pygame.Surface((self.width, self.height))

        # 设置颜色
        WHITE = (255, 255, 255)

        # 设置背景颜色
        screen.fill(WHITE)

        # 绘制障碍物
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, (0, 0, 0), (obstacle[0], obstacle[1], 40, 40), 0)

        # 将pygame surface转换为QImage
        image = QImage(screen.get_buffer(), self.width, self.height, QImage.Format_RGB32)

        # 将QImage转换为QPixmap
        pixmap = QPixmap.fromImage(image)

        # 使用QPainter绘制pixmap
        painter = QPainter(self)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

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
