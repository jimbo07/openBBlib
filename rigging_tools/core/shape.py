
from collections import OrderedDict 

import maya.cmds as cmds

from ooutdmaya.rigging.core.util import tag
from ooutdmaya.common import curve
import json
# import maya.OpenMaya as om

def write(nodeList, filePath, info=False, fullPath=False):
    """Exports shape data for the specified list of nodes
    
    Note:
        Currently only supports Nurbs Curves, also currently expects unique names
    
    Args:
        nodeList (str): List of nodes to store data from
        filePath (str): Path to write the information to
    
    Example:
        from ooutdmaya.rigging.core import util
        util.IO.shape.write(nodeList=['myNurbsCrv1'], filePath='/tmp/tmp.json')
        
    """
    if not nodeList or not filePath:
        raise ValueError("Topnode or filePath was not specified")
    
    nrbCrvList = curve.nurbsCurveShapes(nodeList, f=fullPath)
    if info: print 'nrbCrvList = {0}'.format(nrbCrvList)
    # prep dict
    dataDict = dict()
    
    # Populate dict with curve info
    # nrbCrvList = [u'r_legFingerFk_ctlShape', u'l_legFingerFk_ctlShape', u'neckBaseFk_ctlShape']
    for crv in nrbCrvList:
        dataDict[crv] = cmds.getAttr('{0}.cv[*]'.format(crv))
        '''
        curveSel = om.MSelectionList()
        om.MGlobal.getSelectionListByName(crv, curveSel)
        curvePath = om.MDagPath()
        curveSel.getDagPath(0, curvePath)
        curveFn = om.MFnNurbsCurve(curvePath)
        numCVs = curveFn.numCVs()
        '''
        '''
        numCVs = cmds.getAttr('{0}.cp'.format(crv), s=1)
        cvPosList = []
        for i in range(0, numCVs):
            pos = cmds.xform('{0}.cp[{1}]'.format(crv, i), ws=1, t=1, q=1)
            cvPosList.append(pos)
        dataDict[crv] = cvPosList
        '''
            
    j = json.dumps(dataDict, indent=4)
    f = open(filePath, 'w')
    print >> f, j
    f.close()

    if info: tag.printDict(dataDict, lvl=0)
    
    
def read(filePath):
    """Loads shape data from specified file
    
    Args:
        filePath (str): fullpath to the json file containing the constraint information
    
    Example:
        from ooutdmaya.rigging.core import util
        util.IO.shape.read('/tmp/tmp.json')
    """
    with open(filePath) as jd:
        dataDict = json.loads(jd.read())
    
    for crv in dataDict:
        if not cmds.objExists(crv):
            continue
        if cmds.objectType(crv) != 'nurbsCurve':
            continue
        for cv in range(0, len(dataDict[crv])):
            cmds.xform('{0}.cp[{1}]'.format(crv, cv), t=dataDict[crv][cv])
    
    
