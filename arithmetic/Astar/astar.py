# 姓名：高翔
# 2024/1/29 11:40
import time

from .Node import Node
import pygame

def getKeyforSort(element: Node):
    return element.f  # element#不应该+element.h，否则会穿墙


def astar(workMap):
    height=workMap.height
    width=workMap.width

    start_point = workMap.start_point
    print(start_point[0])
    end_point = workMap.end_point
    startx, starty = start_point[0], start_point[1]
    endx, endy = end_point[0], end_point[1]
    startNode = Node(startx, starty, 0, 0, None)
    openList = []
    lockList = []
    lockList.append(startNode)
    currNode = startNode
    result = []
    screen=workMap.plan_surface
    while (endx, endy) != (currNode.x, currNode.y):
        # 查找临近节点
        print(currNode.x, currNode.y)
        workList = currNode.getNeighbor(workMap, endx, endy)
        for i in workList:
            if i not in lockList:
                # 如果在openList中，则重新计算G,如果不在则加入
                if i.hasNode(openList):
                    i.changeG(openList)
                else:
                    openList.append(i)
        openList.sort(key=getKeyforSort)  # 关键步骤
        currNode = openList.pop(0)
        lockList.append(currNode)
        if openList:
            #print(openList)
            for k in openList:
                pygame.draw.rect(screen, (150, 0, 0), (k.x, k.y, workMap.cell_size, workMap.cell_size), 0)

        if lockList:
            for k in lockList:
                pygame.draw.rect(screen, (150, 150, 150), (k.x, k.y, workMap.cell_size, workMap.cell_size), 0)


    while currNode.father != None:
        result.append((currNode.x, currNode.y))
        currNode = currNode.father
    result.append((currNode.x, currNode.y))
    workMap.paintAstar(openList, lockList,result)
    return result,screen
