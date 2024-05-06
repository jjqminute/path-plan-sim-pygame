class point:  # 点类（每一个唯一坐标只有对应的一个实例）
    _list = []  # 储存所有的point类实例
    _tag = True  # 标记最新创建的实例是否为_list中的已有的实例，True表示不是已有实例

    # def __new__(cls, x, y):  # 重写new方法实现对于同样的坐标只有唯一的一个实例
    #     for i in point._list:
    #         if i.x == x and i.y == y:
    #             point._tag = False
    #             return i
    #     nt = super(point, cls).__new__(cls)
    #     point._list.append(nt)
    #     return nt

    def __init__(self, x, y):
        if point._tag:
            self.x = x
            self.y = y
            self.parent = None
        else:
            point._tag = True

    @classmethod
    def clear(cls):  # clear方法，每次搜索结束后，将所有点数据清除，以便进行下一次搜索的时候点数据不会冲突。
        point._list = []

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, point) and self.x == other.x and self.y == other.y

    def __str__(self):
        return '(%d,%d)[father:(%s)]' % (self.x, self.y,  str(
            (self.parent.x, self.parent.y)) if self.parent != None else 'null')
