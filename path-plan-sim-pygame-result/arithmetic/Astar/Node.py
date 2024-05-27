'''
    Node.py主要是描述对象Node
'''
import pygame

class point:  # 点类（每一个唯一坐标只有对应的一个实例）
    _list = []  # 储存所有的point类实例
    _tag = True  # 标记最新创建的实例是否为_list中的已有的实例，True表示不是已有实例

    def __new__(cls, x, y):  # 重写new方法实现对于同样的坐标只有唯一的一个实例
        for i in point._list:
            if i.x == x and i.y == y:
                point._tag = False
                return i
        nt = super(point, cls).__new__(cls)
        point._list.append(nt)
        return nt

    def __init__(self, x, y):
        if point._tag:
            self.x = x
            self.y = y
            self.father = None
            self.F = 0  # 当前点的评分  F=G+H
            self.G = 0  # 起点到当前节点所花费的消耗
            self.cost = 0  # 父节点到此节点的消耗
        else:
            point._tag = True

    @classmethod
    def clear(cls):  # clear方法，每次搜索结束后，将所有点数据清除，以便进行下一次搜索的时候点数据不会冲突。
        point._list = []

    def __eq__(self, T):  # 重写==运算以便实现point类的in运算
        if type(self) == type(T):
            return (self.x, self.y) == (T.x, T.y)
        else:
            return False

    def __str__(self):
        return '(%d,%d)[F=%d,G=%d,cost=%d][father:(%s)]' % (self.x, self.y, self.F, self.G, self.cost, str(
            (self.father.x, self.father.y)) if self.father != None else 'null')


class Node(object):
    '''
        初始化节点信息
    '''

    def __init__(self, x, y, g, h, father):
        self.x = x
        self.y = y
        self.g = g
        self.h = h
        self.f = self.g + self.h
        self.father = father

    '''
        处理边界和障碍点
    '''

    def getNeighbor(self, mapdata, endx, endy):
        x = self.x
        y = self.y
        result = []
        # 先判断是否在上下边界
        # if(x!=0 or x!=len(mapdata)-1):
        # 上
        # Node(x,y,g,h,father)
        if x != 0 and (x - 10, y) not in mapdata.obstacles:
            upNode = Node(x - 10, y, self.g + 10, (abs(x - 10 - endx) + abs(y - endy)) * 10, self)
            result.append(upNode)
        # 下
        if x != len(mapdata.map) - 1 and (x + 10, y) not in mapdata.obstacles:
            downNode = Node(x + 10, y, self.g + 10, (abs(x + 10 - endx) + abs(y - endy)) * 10, self)
            result.append(downNode)
        # 左
        if y != 0 and (x, y - 10) not in mapdata.obstacles:
            leftNode = Node(x, y - 10, self.g + 10, (abs(x - endx) + abs(y - 10 - endy)) * 10, self)
            result.append(leftNode)
        # 右
        if y != len(mapdata.map[0]) - 1 and (x, y + 10) not in mapdata.obstacles:
            rightNode = Node(x, y + 10, self.g + 10, (abs(x - endx) + abs(y + 10 - endy)) * 10, self)
            result.append(rightNode)
        # 西北  14
        if x != 0 and y != 0 and (x - 10, y - 10) not in mapdata.obstacles:
            wnNode = Node(x - 10, y - 10, self.g + 14, (abs(x - 10 - endx) + abs(y - 10 - endy)) * 10, self)
            result.append(wnNode)
        # 东北
        if x != 0 and y != len(mapdata.map[0]) - 1 and (x - 10, y - 10) not in mapdata.obstacles:
            enNode = Node(x - 10, y + 10, self.g + 14, (abs(x - 10 - endx) + abs(y + 10 - endy)) * 10, self)
            result.append(enNode)
        # 西南
        if x != len(mapdata.map) - 1 and y != 0 and (x + 10, y - 10) not in mapdata.obstacles:
            wsNode = Node(x + 10, y - 10, self.g + 14, (abs(x + 10 - endx) + abs(y - 10 - endy)) * 10, self)
            result.append(wsNode)
        # 东南
        if x != len(mapdata.map) - 1 and y != len(mapdata.map[0]) - 1 and (x + 10, y + 10) not in mapdata.obstacles:
            esNode = Node(x + 10, y + 10, self.g + 14, (abs(x + 10 - endx) + abs(y + 10 - endy)) * 10, self)
            result.append(esNode)
        # #如果节点在关闭节点 则不进行处理
        # finaResult = []
        # for i in result:
        #     if(i not in lockList):
        #         finaResult.append(i)
        # result = finaResult
        return result

    def hasNode(self, worklist):
        for i in worklist:
            if i.x == self.x and i.y == self.y:
                return True
        return False

    # 在存在的前提下
    def changeG(self, worklist):
        for i in worklist:
            if i.x == self.x and i.y == self.y:
                if i.f > self.f:
                    i.g = self.g
                    i.f = i.g + i.h