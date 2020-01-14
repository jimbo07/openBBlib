import maya.cmds as cmds
from collections import OrderedDict 
from ooutdmaya.rigging.core.util import tag, easy

import json


def saveConstraintsJSON(topnode, filepath):
    """Exports all constraints found under specified node to specified filepath
    
    Note:
        Assumes simple connections, ie. one or several sources driving a singular target
    
    Args:
        topnode (str): Node to look beneath for constraints. ALL constraints beneath this node will be stored
        filepath (str): Path to write the information to
        
    """
    if not topnode or not filepath:
        raise ValueError("Topnode or filepath was not specified")
    
    # prep lists
    pacs = cmds.listRelatives(topnode, ad=1, typ="parentConstraint")
    pocs = cmds.listRelatives(topnode, ad=1, typ="pointConstraint")
    oics = cmds.listRelatives(topnode, ad=1, typ="orientConstraint")
    sacs = cmds.listRelatives(topnode, ad=1, typ="scaleConstraint")
    aics = cmds.listRelatives(topnode, ad=1, typ="aimConstraint")
    
    # prep dict
    conDict = dict()
    
    # add parent constraint information to the conDict
    if pacs:
        for pac in pacs:
            suffix = "_pac"
            
            sourceList = list()
            attrList = ["constraintRotateX", "constraintRotateY", "constraintRotateZ",
                        "constraintTranslateX", "constraintTranslateY", "constraintTranslateZ"]
            for attr in attrList:
                sourceList = sourceList + cmds.listConnections("{0}.{1}".format(pac, attr))
            sourceList = list(OrderedDict.fromkeys(sourceList))
            sourceList = [x for x in sourceList if not suffix in x]
            
            targetList = cmds.parentConstraint(pac, q=True, targetList=True)
            
            attrList = ["interpType"] + cmds.parentConstraint(pac, q=True, weightAliasList=True)
            attrDict = dict()
            
            for attr in attrList:
                attrDict[attr] = cmds.getAttr("{0}.{1}".format(pac, attr))
            
            conDict[pac] = {
                'targets':targetList,
                'source':sourceList,
                'attributes':attrDict
            }
        
    # add point constraint information to the conDict
    if pocs:
        for poc in pocs:
            suffix = "_poc"
            
            sourceList = list()
            attrList = ["constraintTranslateX", "constraintTranslateY", "constraintTranslateZ"]
            for attr in attrList:
                sourceList = sourceList + cmds.listConnections("{0}.{1}".format(poc, attr))
            sourceList = list(OrderedDict.fromkeys(sourceList))
            sourceList = [x for x in sourceList if not suffix in x]
            
            targetList = cmds.pointConstraint(poc, q=True, targetList=True)
            
            attrList = cmds.pointConstraint(poc, q=True, weightAliasList=True)
            attrDict = dict()
            
            for attr in attrList:
                attrDict[attr] = cmds.getAttr("{0}.{1}".format(poc, attr))
            
            conDict[pac] = {
                'targets':targetList,
                'source':sourceList,
                'attributes':attrDict
            }

    # add point constraint information to the conDict
    if oics:
        for oic in oics:
            suffix = "_oic"
            
            sourceList = list()
            attrList = ["constraintRotateX", "constraintRotateY", "constraintRotateZ"]
            for attr in attrList:
                sourceList = sourceList + list(OrderedDict.fromkeys(cmds.listConnections("{0}.{1}".format(oic, attr))))
            sourceList = [x for x in sourceList if not suffix in x]
            
            targetList = cmds.pointConstraint(oic, q=True, targetList=True)
            
            attrList = cmds.pointConstraint(oic, q=True, weightAliasList=True)
            attrDict = dict()
            
            for attr in attrList:
                attrDict[attr] = cmds.getAttr("{0}.{1}".format(oic, attr))
            
            conDict[pac] = {
                'targets':targetList,
                'source':sourceList,
                'attributes':attrDict
            }        

    # add scale constraint information to the conDict
    if sacs:
        for sac in sacs:
            suffix = "_sac"
            
            sourceList = list()
            attrList = ["constraintScaleX", "constraintScaleY", "constraintScaleZ"]
            for attr in attrList:
                sourceList = sourceList + cmds.listConnections("{0}.{1}".format(sac, attr))
            sourceList = list(OrderedDict.fromkeys(sourceList))
            sourceList = [x for x in sourceList if not suffix in x]
            
            targetList = cmds.scaleConstraint(sac, q=True, targetList=True)
            
            attrList = cmds.scaleConstraint(sac, q=True, weightAliasList=True)
            attrDict = dict()
            
            for attr in attrList:
                attrDict[attr] = cmds.getAttr("{0}.{1}".format(sac, attr))
            
            conDict[pac] = {
                'targets':targetList,
                'source':sourceList,
                'attributes':attrDict
            }

    """
    # add aim constraint information to the conDict
    if aics:
        for aic in aics:
            # TODO:
            # Expand to return stuff like world up objects etc.
            suffix = "_aic"
            sourceList = list(OrderedDict.fromkeys(cmds.listConnections("{0}.{1}".format(aic, "target"))))
            sourceList = [x for x in sourceList if not suffix in x]
            
            targetList = cmds.aimConstraint(aic, q=True, targetList=True)
            
            attrList = cmds.aimConstraint(aic, q=True, weightAliasList=True)
            attrDict = dict()
            
            for attr in attrList:
                attrDict[attr] = cmds.getAttr("{0}.{1}".format(aic, attr))
            
            conDict[pac] = {
                'targets':targetList,
                'source':sourceList,
                'attributes':attrDict
            }    
    """
    j = json.dumps(conDict, indent=4)
    f = open(filepath, 'w')
    print >> f, j
    f.close()

    tag.printDict(conDict, lvl=0)

    
def loadConstraintsJSON(filepath):
    """Loads constraints from specified file
    
    Args:
        filepath (str): fullpath to the json file containing the constraint information
        topnode (str): 
        
    """
    with open(filepath) as jd:
        conDict = json.loads(jd.read())
    
    # tag.printDict(conDict, lvl=0)
    for constraint in conDict:
        targets = conDict[constraint]['targets']
        source = conDict[constraint]['source']

        if "_pac" in constraint:
        
            if len(source) == 1:
                if cmds.objExists(source[0]):
                    try:
                        con = cmds.parentConstraint(targets, source, mo=1, n=constraint)[0]
                        
                        for attr in conDict[constraint]['attributes']:
                            cmds.setAttr("{0}.{1}".format(con, attr), conDict[constraint]['attributes'][attr])
                    except ValueError:
                        print "One of the following was not found: {0} or {1}, skipping...".format(targets, source)
            
        if "_poc" in constraint:
        
            if len(targets) == 1:
                if cmds.objExists(targets[0]):
                    con = cmds.pointConstraint(targets, source, mo=1, n=constraint)[0]
                    
                    for attr in conDict[constraint]['attributes']:
                        cmds.setAttr("{0}.{1}".format(con, attr), conDict[constraint]['attributes'][attr])
                        
        if "_oic" in constraint:
        
            if len(targets) == 1:
                if cmds.objExists(targets[0]):
                    con = cmds.orientConstraint(source, targets, mo=1, n=constraint)[0]
                    
                    for attr in conDict[constraint]['attributes']:
                        cmds.setAttr("{0}.{1}".format(con, attr), conDict[constraint]['attributes'][attr])        
                        
        if "_sac" in constraint:
        
            if len(targets) == 1:
                if cmds.objExists(targets[0]):
                    con = cmds.scaleConstraint(source, targets, mo=1, n=constraint)[0]
                    
                    for attr in conDict[constraint]['attributes']:
                        cmds.setAttr("{0}.{1}".format(con, attr), conDict[constraint]['attributes'][attr])        
    


def isConstraint(constraint):
    ''' Check if the specified node is a valid constraint
    :param constraint str: The constraint node to query
    :return: True if object is a constraint
    '''
    if not cmds.objExists(constraint): return False
    if not cmds.ls(constraint, type='constraint'): return False
    return True


def isBaked(constraint):
    ''' Check if the specified constraint has been baked
    :param constraint str: The constraint node to query
    '''
    # Check Constraint
    if not isConstraint(constraint):
        raise Exception('Constraint {0} does not exist!!'.format(constraint))
    
    # Get Constraint Slave
    cSlave = slave(constraint)
    
    # Get Slave Channels
    cSlaveAttrs = cmds.listConnections(constraint, s=False, d=True, p=True) or []
    slaveAttrs = [i.split('.')[-1] for i in attrList if i.startswith(slave+'.')] or []
    
    # Check Slave Channels
    if slaveAttrs: return False
    
    # Return Result
    return False


def targetList(constraint):
    ''' Return a list of targets (drivers) for the specified constraint node
    :param constraint str: The constraint node whose targets will be returned
    :return: List of target drivers for specified constraint
    :rtype: list
    '''
    # Check Constraint
    if not isConstraint(constraint):
        raise Exception('Constraint {0} does not exist!!'.format(constraint))
    
    # Get Target List
    targetList = []
    constraintType = cmds.objectType(constraint)
    if constraintType == 'aimConstraint': targetList = cmds.aimConstraint(constraint, q=True, tl=True)
    elif constraintType == 'geometryConstraint': targetList = cmds.geometryConstraint(constraint, q=True, tl=True)
    elif constraintType == 'normalConstraint': targetList = cmds.normalConstraint(constraint, q=True, tl=True)
    elif constraintType == 'orientConstraint': targetList = cmds.orientConstraint(constraint, q=True, tl=True)
    elif constraintType == 'parentConstraint': targetList = cmds.parentConstraint(constraint, q=True, tl=True)
    elif constraintType == 'pointConstraint': targetList = cmds.pointConstraint(constraint, q=True, tl=True)
    elif constraintType == 'poleVectorConstraint': targetList = cmds.poleVectorConstraint(constraint, q=True, tl=True)
    elif constraintType == 'scaleConstraint': targetList = cmds.scaleConstraint(constraint, q=True, tl=True)
    elif constraintType == 'tangentConstraint': targetList = cmds.tangentConstraint(constraint, q=True, tl=True)
    
    # Check Target List
    if not targetList: targetList = []
    
    # Return Result
    return targetList


def targetIndex(constraint, target):
    ''' Return the target index of the specified target of a constraint
    :param constraint str: The constraint to return the target index for
    :param target str: The constraint target to return the input index for
    :return: Target index of specified target of a constraint
    :rtype: int
    '''
    # Get Target List
    tgtList = targetList(constraint)
    # Get Target List
    targetIndex = tgtList.index(target)
    # Return Result
    return targetIndex


def targetAliasList(constraint):
    ''' Return a list of targets (drivers) attribute aliases for the specified constraint node
    :param constraint str: The constraint node whose targets will be returned
    '''
    # Check Constraint
    if not isConstraint(constraint):
        raise Exception('Constraint "'+constraint+'" does not exist!!')
    
    # Get Target List
    targetList = []
    constraintType = cmds.objectType(constraint)
    if constraintType == 'aimConstraint': targetList = cmds.aimConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'geometryConstraint': targetList = cmds.geometryConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'normalConstraint': targetList = cmds.normalConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'orientConstraint': targetList = cmds.orientConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'parentConstraint': targetList = cmds.parentConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'pointConstraint': targetList = cmds.pointConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'poleVectorConstraint': targetList = cmds.poleVectorConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'scaleConstraint': targetList = cmds.scaleConstraint(constraint, q=True, weightAliasList=True)
    elif constraintType == 'tangentConstraint': targetList = cmds.tangentConstraint(constraint, q=True, weightAliasList=True)
    
    # Check Target List
    if not targetList: targetList = []
    
    # Return Result
    return targetList


def targetAlias(constraint, target):
    ''' Return the target alias fo the specified constraint and target transform
    :param constraint str: The constraint to get the target alias from
    :param target str: The constraint target transform to get the target alias from
    :return: target alias for specified contraint + target transform
    :rtype: str
    '''
    # Check Constraint
    if not isConstraint(constraint):
        raise Exception('Object {0} is not a valid constraint node!'.format(constraint))
    
    # Get Target List 
    conTargetList = targetList(constraint)
    if not conTargetList.count(target):
        raise Exception('Constraint {0} has no target {1}!'.format(constraint, target))
    
    # Get Target Alias List
    conTargetAliasList = targetAliasList(constraint)
    
    # Get Target Index
    targetIndex = conTargetList.index(target)
    
    # Get Target Alias
    targetAlias = conTargetAliasList[targetIndex]
    
    # Return Result
    return targetAlias


def slaveList(constraint):
    ''' Return a list of slave transforms for the specified constraint node
    :param constraint str: The constraint node whose slaves will be returned
    :return: list of slave transform for specified constraint
    :rtype: list
    '''
    # Check constraint
    if not cmds.objExists(constraint): raise Exception('Constraint {0} does not exist!!'.format(constraint))
    
    # Get slave list
    tgtList = cmds.listConnections(constraint+'.constraintParentInverseMatrix', s=True, d=False) or []
    
    # Return result
    return tgtList


def slave(constraint):
    ''' Return the slave transforms for the specified constraint node
    :param constraint str: The constraint node to query
    :return: Return the slave for the specified constraint node
    :rtype: str
    '''
    # Get Slave Transform
    slaves = slaveList(constraint)
    if not slaves: raise Exception('Unable to determine slave transform for constraint {0}!'.format(constraint))
    # Return Result
    return slaves[0]


def blendConstraint(targetList, slave, blendNode='', blendAttr='bias', maintainOffset=True, prefix=''):
    ''' Create a parent constraint that can be blended between 2 (more later) constraint targets
    :param targetList list: 2 target transforms to constrain to
    :param slave str: Transform to constrain
    :param blendNode str: Node that will contain the constraint blend attribute. If empty, use slave.
    :param blendAttr str: Constraint blend attribute name.
    :param maintainOffset bool: Maintain relative offsets between slave and targets.
    :param prefix str: Name prefix for created nodes
    :return: The resulting blendNode + attr path
    :rtype: str
    '''
    # Check prefix
    if not prefix: prefix = slave
    
    # Check targets
    if len(targetList) != 2: raise Exception('Target list must contain 2 target transform!')
    for target in targetList:
        if not cmds.objExists(target):
            raise Exception('Target transform {0} does not exist!'.format(target))
    
    # Check slave
    if not cmds.objExists(slave):
        raise Exception('Slave transform {0} does not exist!'.format(slave))
    
    # Check blendNode
    if not blendNode: blendNode = slave
    
    # Create constraint
    constraint = cmds.parentConstraint(targetList, slave, mo=maintainOffset, n="{0}_parentConstraint".format(prefix))[0]
    constraintAlias = cmds.parentConstraint(constraint, q=True, wal=True)
    
    # Create blend
    cmds.addAttr(blendNode, ln=blendAttr, min=0, max=1, dv=0.5, k=True)
    blendSub = cmds.createNode('plusMinusAverage', n="{0}_plusMinusAverage".format(prefix))
    cmds.setAttr(blendSub+'.operation', 2) 
    cmds.setAttr(blendSub+'.input1D[0]', 1.0)
    cmds.connectAttr(blendNode+'.'+blendAttr, blendSub+'.input1D[1]', f=True)
    
    # Connect Blend
    cmds.connectAttr(blendSub+'.output1D', constraint+'.'+constraintAlias[0], f=True)
    cmds.connectAttr(blendNode+'.'+blendAttr, constraint+'.'+constraintAlias[1], f=True)
    
    # Return result
    return blendNode+'.'+blendAttr

