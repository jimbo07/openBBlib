from math import sqrt
from maya import cmds
import math


def closestTransform(transform, transformList):
    pos = cmds.xform(transform, q=1, ws=1, rp=1)
    srcPos = cmds.xform(transformList[0], q=1, ws=1, rp=1)
    trsIndex = 0
    lastTrsDist = sqrt((srcPos[0] - pos[0]) ** 2 + (srcPos[1] - pos[1]) ** 2 + (srcPos[2] - pos[2]) ** 2)
    # find the closest joint
    for i, each in enumerate(transformList):
        srcPos = cmds.xform(each, q=1, ws=1, rp=1)
        currTrsDist = sqrt((srcPos[0] - pos[0]) ** 2 + (srcPos[1] - pos[1]) ** 2 + (srcPos[2] - pos[2]) ** 2)
        if currTrsDist < lastTrsDist:
            trsIndex = i
            lastTrsDist = currTrsDist
    return transformList[trsIndex]


def distance(self, pos1, pos2):
    '''
    calculate distance between two 3d points
    '''
    pos1 = [float('{0:.4f}'.format(each)) for each in pos1]
    pos2 = [float('{0:.4f}'.format(each)) for each in pos2]
    return math.sqrt(math.pow(pos1[0] - float(pos2[0]), 2) + math.pow(pos1[1] - pos2[1], 2) + math.pow(pos1[2] - pos2[2], 2))


def getHierarchyByType(nodeList=None, nodeType='mesh', selectResult=False, fullPath=False):
    """
    from ooutdmaya.common.mesh import lib
    reload(lib)
    lib.getHierarchyByType(nodeList=cmds.ls(sl=1))
    """

    if not nodeList:
        nodeList = cmds.ls(sl=1, long=fullPath)

    meshTransformList = []
    for each in nodeList:
        # Search all descendents
        children = cmds.listRelatives(each, ad=1, children=1, f=1, type=nodeType, fullPath=fullPath)
        for node in children:
            parent = cmds.listRelatives(node, parent=1, fullPath=fullPath)[0]
            meshTransformList.append(parent)
        # Search the direct node itself
        if each in meshTransformList: continue
        children = cmds.listRelatives(each, children=1, f=1, type=nodeType);
        if children:
            meshTransformList.append(each)
            
    if selectResult: cmds.select(meshTransformList)
    return list(set(meshTransformList))
