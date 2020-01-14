from ooutdmaya.common import transform
from ooutdmaya.common.util import maths

reload(transform)
reload(maths)

from maya import cmds
import maya.api.OpenMaya as om

def deleteIntermediateShapes(source, info=False):
    """
    from ooutdmaya.common.mesh import lib
    reload(lib)
    for each in cmds.ls(sl=1):
        lib.deleteIntermediateShapes(each, info=1)
    """
    children = cmds.listRelatives(source, children=1, type='mesh', fullPath=True)
    if not children:
        return
    for child in children:
        if cmds.getAttr('{0}.intermediateObject'.format(child)):
            if info: print('\tmesh "{0}" is intermediateObject, deleting...'.format(child))
            cmds.delete(child)
            continue


def getMeshShape(source, info=False, fullPath=False):
    """
    """
    if cmds.objectType(source) == 'mesh':
        mesh = source
    else:
        children = cmds.listRelatives(source, children=1, type='mesh', fullPath=fullPath)
        mesh = children[0]
        for child in children:
            if cmds.getAttr('{0}.intermediateObject'.format(child)):
                if info: print('\tskippingmesh "{0}" is intermediateObject'.format(child))
                continue
            mesh = child
    return mesh


def getHierarchyByType(nodeList=None, nodeType='mesh', selectResult=False):
    """
    from ooutdmaya.common.mesh import lib
    reload(lib)
    lib.getHierarchyByType(nodeList=cmds.ls(sl=1))
    """
    print transform.__file__
    transform.lib.getHierarchyByType(nodeList=nodeList, nodeType=nodeType, selectResult=selectResult)


def vtxInRange(mesh, pos, dist):
    '''
    returns a list of vertices which are near the
    supplied position within the given distance param
    '''
    vtxList = []
    for i in range(0, cmds.polyEvaluate(mesh, vertex=True)):
        vtxPos = cmds.xform('{}.vtx[{}]'.format(mesh, i), q=True, ws=True, t=True)
        currDist = self.distance(vtxPos, pos)
        if currDist > dist: continue
        vtxList.append(i)
    return vtxList
