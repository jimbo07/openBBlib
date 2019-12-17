"""
"""
from maya import cmds, OpenMaya
# import math

from ooutdmaya.rigging.core import util
from ooutdmaya.rigging.core.util import easy
from ooutdmaya.common.util import maths

    
def getJntHierarchy(jnt, fullPath=False):
    returnList = [jnt]
    children = cmds.listRelatives(jnt, children=1, type='joint', fullPath=fullPath)
    if children:
        for child in children:
            returnList = returnList + getJntHierarchy(child, fullPath=fullPath)
    return returnList


def orient(jointList=None):
    """
    from ooutdmaya.rigging.core.util.joint import orient
    orient(jointList=cmds.ls(sl=1))
    """
    jointList = jointList or cmds.ls(sl=1)
     
    for jnt in jointList: 
        rot = cmds.xform(jnt, q=1, ws=1, ro=1)
        cmds.setAttr('{0}.jointOrient'.format(jnt), 0, 0, 0)
        cmds.xform(jnt, ro=rot, ws=1)
        rotate = cmds.getAttr('{0}.rotate'.format(jnt))[0]
        cmds.setAttr('{0}.rotate'.format(jnt), 0, 0, 0)
        cmds.setAttr('{0}.jointOrient'.format(jnt), rotate[0], rotate[1], rotate[2]) 


def duplicateSegment(chain, suffix=None, searchReplaceSetList=None, info=False):
    """
    sChain = ['skeleton_:jnt_spine1',
     'skeleton_:jnt_spine2',
     'skeleton_:jnt_spine3',
     'skeleton_:jnt_spine4',
     'skeleton_:jnt_chest']
    chain = joint.duplicateSegment(sChain)
    # Result: [u'jnt_spine1', u'jnt_spine2', u'jnt_spine3', u'jnt_spine4', u'jnt_chest'] # 
    """
    dupl = cmds.duplicate(chain, renameChildren=1)
    if len(dupl) > len(chain):
        cmds.delete(dupl[len(chain):])
    cleanDupList = [dupl[i] for i in xrange(0, len(chain))]
    if suffix:
        ret = []
        for i, jnt in enumerate(cleanDupList):
            newName = util.names.addModifier(chain[i], 'joint', addSuffix=suffix)
            if searchReplaceSetList:
                for search, replace in searchReplaceSetList:
                    newName = newName.replace(search, replace) 
            if info: print 'jnt = {0}'.format(jnt)
            if info: print 'newName = {0}'.format(newName)
            ret.append(cmds.rename(jnt, newName))
    else:
        ret = cleanDupList
    return ret


def duplicateReverseSegment(chain, addSuffix='RVS', info=False):
    """
    chain = ['jnt_armUpper_left', 'jnt_armLower_left', 'jnt_hand_left', 'jnt_finger1_left']
    joint.duplicateReverseSegment(self.chain, addSuffix='IKRVS')
    """
    ikRvsChain = []
    jntOrientDict = {}
    jntOrientDict['pos'] = []
    jntOrientDict['rot'] = []
    cmds.select(cl=1)
    i = len(chain)
    x = 0
    while i > 0:
        i -= 1
        pos = cmds.xform(chain[i], ws=1, q=1, t=1)
        jntName = util.names.addModifier(chain[i], 'joint', addSuffix=addSuffix)
        jnt = cmds.joint(p=[pos[0], pos[1], pos[2]], n=jntName)
        jntOrientDict['pos'].append([chain[i], jnt])
        if i > 0:
            jntOrientDict['rot'].append([chain[i - 1], jnt])
        else:
            jntOrientDict['rot'].append([ikRvsChain[x - 1], jnt])
        ikRvsChain.append(jnt)
        if(x > 0):
            if info: print jnt
            if info: print ikRvsChain[x - 1]
            if info: print '\n'
            cmds.joint(ikRvsChain[x - 1], e=1, zso=1, oj='xyz', sao='yup')
        x += 1
    cmds.select(cl=1)
    cmds.setAttr('{0}.jointOrientX'.format(ikRvsChain[-1]), 0)
    cmds.setAttr('{0}.jointOrientY'.format(ikRvsChain[-1]), 0)
    cmds.setAttr('{0}.jointOrientZ'.format(ikRvsChain[-1]), 0)
    conList = []
    for source, dest in jntOrientDict['pos']:
        poc = cmds.pointConstraint(source, dest)
        conList.append(poc[0])
    for source, dest in jntOrientDict['rot']:
        oic = cmds.orientConstraint(source, dest)
        conList.append(oic[0])
    cmds.delete(conList)
    # Orient joints
    orient(ikRvsChain)
    return ikRvsChain


def poleVectorPos(chain, factor=0.5):
    """
    returns a worldspace position based on the supplied three joints
    
    # Example
    loc = cmds.spaceLocator()[0]
    chain = ['jnt_armUpper_left', 'jnt_armLower_left', 'jnt_hand_left']
    pos = poleVectorPos(chain)
    cmds.xform(loc , ws =1 , t= (pos[0], pos[1], pos[2])) 
    """
    start = cmds.xform(chain[0], q=1 , ws=1, t=1)
    mid = cmds.xform(chain[1], q=1, ws=1, t=1)
    end = cmds.xform(chain[2], q=1, ws=1, t=1)
    
    startV = OpenMaya.MVector(start[0], start[1], start[2])
    midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
    endV = OpenMaya.MVector(end[0], end[1], end[2])
    
    startEnd = endV - startV
    startMid = midV - startV
    
    dotP = startMid * startEnd
    proj = float(dotP) / float(startEnd.length())  #
    
    startEndN = startEnd.normal()
    projV = startEndN * proj
    
    arrowV = startMid - projV
    finalV = arrowV + midV
    poleToMid = finalV - midV
    arrowV *= (startEnd.length() / poleToMid.length()) * factor
    finalV = arrowV + midV
    
    return (finalV.x , finalV.y, finalV.z)


def isJoint(joint):
    ''' Check if the specified object is a valid joint
    :param joint str: Object to check
    '''
    # Check object exists
    if not cmds.objExists(joint): return False
    
    # Check joint
    if not cmds.ls(type='joint').count(joint): return False
    
    # Return result
    return True

def isEndJoint(joint):
    ''' Check if the specified joint is an end joint
    :param joint str: Joint to check
    '''
    # Check Joint
    if not isJoint(joint):
        raise Exception('Object "{0}" is not a valid joint!'.format(joint))
    
    # Check Child Joints
    jointDescendants = cmds.ls(cmds.listRelatives(joint, ad=True) or [], type='joint')
    if not jointDescendants: return True
    else: return False


def getEndJoint(startJoint,includeTransforms=False):
    ''' Find the end joint of a chain from the specified start joint.
    :param joint str: Joint to find end joint from
    :param includeTransforms bool: Include non-joint transforms in the chain.
    '''
    # Check Start Joint
    if not cmds.objExists(startJoint):
        raise Exception('Start Joint "{0}" does not exist!'.format(startJoint))
    
    # Find End Joint
    endJoint = None
    nextJoint = startJoint
    while(nextJoint):
        
        # Get Child Joints
        childList = cmds.listRelatives(nextJoint,c=True) or []
        childJoints = cmds.ls(childList,type='joint') or []
        if includeTransforms:
            childJoints = list(set(childJoints + cmds.ls(childList,transforms=True) or []))
        
        # Check End Joint
        if childJoints:
            nextJoint = childJoints[0]
        else:
            endJoint = nextJoint
            nextJoint = None
    
    # Return Result    
    return endJoint

    
def length(joint):
    ''' Get length of specified joint
    :param joint str: Joint to query length from
    '''
    # Check Joint
    if not cmds.objExists(joint): raise Exception('Joint "{0}" does not exist!'.format(joint))
    
    # Get Child Joints
    cJoints = cmds.ls(cmds.listRelatives(joint, c=True, pa=True) or [],type='joint')
    if not cJoints: return 0.0
    
    # Get Length
    maxLength = 0.0
    for cJoint in cJoints:
        pt1 = easy.getPosition(joint)
        pt2 = easy.getPosition(cJoint)
        offset = maths.offsetVector(pt1,pt2)
        length = maths.mag(offset)
        if length > maxLength: maxLength = length
    
    # Return Result
    return maxLength

