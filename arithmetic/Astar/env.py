import pygame
import sys
import math
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os

screen = pygame.display.set_mode((800,800))

class spot:
    def __init__(self,x,y):
        #坐标
        self.i = x
        self.j = y
        #分数
        self.f = 0
        self.g = 0
        self.h = 0
        #父节点
        self.previous = None
        #是不是障碍
        self.obs = False
        #选择状态
        self.closed = False
        #权
        self.value = 1
        #相邻节点
        self.neighbors = []

    def show(self,color,st):
        if self.closed == False:
            pygame.draw.rect(screen,color,(self.i*w,self.j*h,w,h),st)
            pygame.display.update()

    def path(self,color,st):
            pygame.draw.rect(screen,color,(self.i*w,self.j*h,w,h),st)
            pygame.display.update()

    def addNeighbors(self):
        i = self.i
        j = self.j
        if i < rows-1 and grid[i+1][j].obs == False:
            self.neighbors.append(grid[i+1][j])
        if i > 0 and grid[i-1][j].obs == False:
            self.neighbors.append(grid[i-1][j])
        if j < cols-1 and grid[i][j+1].obs == False:
            self.neighbors.append(grid[i][j+1])
        if j > 0 and grid[i][j-1].obs == False:
            self.neighbors.append(grid[i][j-1])

#行列数
cols = 50
rows = 50



#颜色
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
grey = (220,220,220)

#格子长宽
w = 800/cols
h = 800/rows

#父节点列表
cameFrom = []

#创建节点
grid = [0 for i in range(cols)]
for i in range(cols):
    grid[i] = [0 for i in range(rows)]

for i in range(rows):
    for j in range(cols):
        grid[i][j] = spot(i,j)

#默认起点、终点
start = grid[5][5]
end = grid[7][19]



#画界面
for i in range(rows):
    for j in range(cols):
        grid[i][j].show((255,255,255),1)

#画围墙
for i in range(rows):
    grid[i][0].show(grey,0)
    grid[i][cols-1].show(grey,0)
    grid[0][i].show(grey,0)
    grid[cols-1][i].show(grey,0)
    grid[i][0].show(grey,0)
    grid[i][cols-1].show(grey,0)
    grid[0][i].show(grey,0)
    grid[cols-1][i].show(grey,0)
    grid[i][0].obs = True
    grid[i][cols-1].obs = True
    grid[0][i].obs = True
    grid[cols-1][i].obs = True
    grid[i][0].obs = True
    grid[i][cols-1].obs = True
    grid[0][i].obs = True
    grid[cols-1][i].obs = True

def onsubmit():
    global start
    global end
    st = startBox.get().split(',')
    ed = endBox.get().split(',')
    start = grid[int(st[0])][int(st[1])]
    end = grid[int(ed[0])][int(ed[1])]
    window.quit()
    window.destroy()

#输入界面
window = Tk()
window.title('请输入')
label_1 = Label(window,text = '起点坐标(x,y): ')
startBox = Entry(window)
label_2 = Label(window,text = '终点坐标(x,y): ')
endBox = Entry(window)
var = IntVar()
showPath = ttk.Checkbutton(window,text = '显示每一步',onvalue=1,offvalue=0,variable=var)
submit = Button(window,text='提交',command=onsubmit)

#布局
label_1.grid(row = 0,column = 0,pady = 3)
label_2.grid(row = 1,column = 0,pady = 3)
startBox.grid(row = 0,column = 1,pady = 3)
endBox.grid(row = 1,column = 1,pady = 3)
showPath.grid(columnspan = 2,row = 2)
submit.grid(columnspan = 2,row = 3)

#启动输入界面
mainloop()

#两个表
openSet = [start]
closeSet = []

#显示起点终点
start.show((255,8,127),0)
end.show((255,8,127),0)

#监听鼠标位置
def mousePress(x):
    t = x[0]
    w = x[1]
    #判断在第几个格子
    g1 = t//(800//cols)
    g2 = w//(800//rows)
    #设置障碍
    set_obs = grid[g1][g2]
    if set_obs != start and set_obs!= end:
        set_obs.obs = True
        set_obs.show(grey,0)

#画障碍
loop = True
while loop:
    ev = pygame.event.poll()
    if pygame.mouse.get_pressed()[0]:
        try:
            pos = pygame.mouse.get_pos()
            mousePress(pos)
        except AttributeError:
            pass
    if ev.type == pygame.QUIT:
        pygame.quit()
    elif ev.type == pygame.KEYDOWN:
        if ev.key == pygame.K_SPACE:
            loop = False

#画好障碍后，初始邻接节点列表
for i in range(rows):
    for j in range(cols):
        grid[i][j].addNeighbors()

#启发式方法
def heurisitic(n,e):
    d = math.sqrt((n.i - e.i)**2 + (n.j - e.j)**2)
    return d

def main():
    #openSet初始化时已经包含起点
    #从中选择f分数最小的
    if(len(openSet) > 0):
        lowestIndex = 0
        for i in range(len(openSet)):
            if(openSet[i].f < openSet[lowestIndex].f):
                lowestIndex = i

    #对当前节点操作
        current = openSet[lowestIndex]
        #找到 打印路径
        if current == end:
            temp = current.f
            while current != start:
                current.closed = False
                current.show(blue, 0)
                current = current.previous
            end.show(red, 0)

            Tk().wm_withdraw()
            result = messagebox.askokcancel('Program Finished', ('The program finished, the shortest distance \n to the path is ' + str(temp) + ' blocks away, \n would you like to re run the program?'))
            if result == True:
                os.execl(sys.executable,sys.executable, *sys.argv)
            else:
                ag = True
                while ag:
                    ev = pygame.event.get()
                    for event in ev:
                        if event.type == pygame.KEYDOWN:
                            ag = False
                            break
            pygame.quit()

        openSet.pop(lowestIndex)
        closeSet.append(current)

        neighbors = current.neighbors
        for i in range(len(neighbors)):
            neighbor = neighbors[i]
            if neighbor not in closeSet:
                tmpG = current.g + current.value
                if neighbor in openSet:
                    if neighbor.g > tmpG:
                        neighbor.g = tmpG
                        neighbor.previous = current
                else:
                    neighbor.g = tmpG
                    openSet.append(neighbor)
                    neighbor.previous = current

            neighbor.h = heurisitic(neighbor,end)
            neighbor.f = neighbor.g + neighbor.h

    if var.get():
        for i in range(len(openSet)):
            openSet[i].show(green,0)

        for i in range(len(closeSet)):
            if closeSet[i] != start:
                closeSet[i].show(red,0)
    current.closed = True



while True:
    ev = pygame.event.poll()
    if ev.type == pygame.QUIT:
        pygame.quit()
    main()

