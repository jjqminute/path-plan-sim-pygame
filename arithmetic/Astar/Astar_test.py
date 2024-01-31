import time, sys
import json


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


class A_Search:  # 核心部分，寻路类
    def __init__(self, arg_start, arg_end, arg_map):
        self.start = arg_start  # 储存此次搜索的开始点
        self.end = arg_end  # 储存此次搜索的目的点
        self.Map = arg_map  # 一个二维数组，为此次搜索的地图引用
        self.open = []  # 开放列表：储存即将被搜索的节点
        self.close = []  # 关闭列表：储存已经搜索过的节点
        self.result = []  # 当计算完成后，将最终得到的路径写入到此属性中
        self.count = 0  # 记录此次搜索所搜索过的节点数
        self.useTime = 0  # 记录此次搜索花费的时间--在此演示中无意义，因为process方法变成了一个逐步处理的生成器，统计时间无意义。
        # 开始进行初始数据处理
        self.open.append(arg_start)
    #将结果保存至txt文本中
    def save(self):
        print("进入save!!!")
        result = self.result
        if result is None:
            print("result=None")
        with open('result.txt', 'w') as f:
            for p in result:
                print(p.x, p.y)
                f.write(f'{p.x},{p.y}\n')
            f.close()

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

    def getAroundPoint(self, loc):  # 获取指定点周围所有可通行的点，并将其对应的移动消耗进行赋值。
        # 上 下 左 右 斜 八个 方向
        l = [(loc.x, loc.y + 1, 10), (loc.x + 1, loc.y + 1, 14), (loc.x + 1, loc.y, 10), (loc.x + 1, loc.y - 1, 14),
             (loc.x, loc.y - 1, 10), (loc.x - 1, loc.y - 1, 14), (loc.x - 1, loc.y, 10), (loc.x - 1, loc.y + 1, 14)]
        # 全列表倒序查询
        for i in l[::-1]:
            # i[0]是x值，i[1]是y值 检测是否过界
            if i[0] < 0 or i[0] >= config.HEIGHT or i[1] < 0 or i[1] >= config.WIDTH:
                l.remove(i)
        nl = []
        for i in l:
            if self.Map[i[0]][i[1]] == 0:
                nt = point(i[0], i[1])
                nt.cost = i[2]
                nl.append(nt)
        return nl

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
        return (abs(loc.x - self.end.x) + abs(loc.y - self.end.y)) * 10

    def DisplayPath(self):  # 在此演示中无意义
        print('搜索花费的时间:%.2fs.迭代次数%d,路径长度:%d' % (self.useTime, self.count, len(self.result)))
        if self.result != None:
            for i in self.result:
                self.Map[i.x][i.y] = 8
            for i in self.Map:
                for j in i:
                    if j == 0:
                        print('%s' % '□', end='')
                    elif j == 1:
                        print('%s' % '▽', end='')
                    elif j == 8:
                        print('%s' % '★', end='')
                print('')
        else:
            print('搜索失败，无可通行路径')

    def process(self):  # 使用yield将process方法变成一个生成器，可以逐步的对搜索过程进行处理并返回关键数据
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
                if self.end in self.open:  # 判断终点是否已经处于open列表中
                    e = self.end
                    self.result.append(e)
                    while True:
                        e = e.father
                        if e == None:
                            break
                        self.result.append(e)
                        print("111111")
                        self.save()
                        # print(result)
                    yield (tar, self.open, self.close)
                    break

            # self.repaint()
            # print('返回')
            yield (tar, self.open, self.close)
            time.sleep(1)  # 暂停
