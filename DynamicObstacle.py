# 动态障碍物数据结构
import math

from shapely import Point


class DynamicObstacle:
    def __init__(self, shape, position, direction, speed, size):
        """
        :param shape: str, 形状类型（如 '圆形', '正方形', '椭圆' 等）
        :param position: tuple(float, float), 障碍物中心位置 (x, y)
        :param direction: tuple(float, float), 方向向量 (dx, dy)
        :param speed: float, 运动速度
        :param size: float, 障碍物大小（半径或边长）
        """
        self.shape = shape
        self.position = position
        self.direction = direction
        self.speed = speed
        self.size = size

    def predict_future_position(self, time_delta):
        """根据速度和时间预测未来的位置"""
        # 计算速度向量 (velocity)
        velocity_x = self.direction[0] * self.speed
        velocity_y = self.direction[1] * self.speed

        # 计算未来位置
        future_x = self.position[0] + velocity_x * time_delta
        future_y = self.position[1] + velocity_y * time_delta
        return Point(future_x, future_y)  # 返回预测的点
    def to_polygon(self):
        """
        将障碍物转换为多边形形式，便于碰撞检测。
        """
        x, y = self.position
        if self.shape == "圆形":
            # 将圆形近似为多边形（例如正十二边形）
            num_segments = 12  # 分段数量
            return [
                (
                    x + self.size * math.cos(2 * math.pi * i / num_segments),
                    y + self.size * math.sin(2 * math.pi * i / num_segments),
                )
                for i in range(num_segments)
            ]
        elif self.shape == "正方形":
            half_size = self.size / 2
            return [
                (x - half_size, y - half_size),
                (x + half_size, y - half_size),
                (x + half_size, y + half_size),
                (x - half_size, y + half_size),
            ]
        else:
            raise ValueError(f"未知形状: {self.shape}")

