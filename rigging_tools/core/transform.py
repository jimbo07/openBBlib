
import maya.OpenMaya as om

import maya.cmds as cmds

from ooutdmaya.rigging.core.util import lib, names


def constraintTrsToClosest(srcTrsList, destTrsList):
    """
    parent constrains the supplied source transforms (srcTrsList)
    to the nearest transform in the supplied destination transforms (destTrsList)
    """
    for transform in srcTrsList:
        # get the closest transform for orient constraining
        closestTrs = lib.closestTransform(transform, destTrsList)
        cmds.parentConstraint(closestTrs, transform, mo=1)


def attachTransformsToCurve(curve, transformList, orientTrsList):
    crvShape = cmds.listRelatives(curve, ad=1, type='nurbsCurve')[0]
    crvShapeAttr = '{0}.create'.format(crvShape)
    npoc = cmds.createNode('nearestPointOnCurve')
    destAttr = '{0}.inputCurve'.format(npoc)
    cmds.connectAttr(crvShapeAttr, destAttr, f=1)
    cvi = cmds.createNode('curveInfo', n='{0}_CVI'.format(curve))
    destAttr = '{0}.inputCurve'.format(cvi)
    cmds.connectAttr(crvShapeAttr, destAttr, f=1)
    arcLen = cmds.getAttr('{0}.arcLength'.format(cvi))
    mdn = cmds.createNode('multiplyDivide', n='{0}_MDN'.format(curve))
    cmds.setAttr('{0}.operation'.format(mdn), 2)
    cmds.connectAttr('{0}.arcLength'.format(cvi), '{0}.input2X'.format(mdn))
    cmds.setAttr('{0}.input1X'.format(mdn), arcLen)

    for transform in transformList:
        # get the closest transform for orient constraining
        closestTrs = closestTransform(transform, orientTrsList)
        # closest point on curve info
        pci = cmds.createNode('pointOnCurveInfo', n='{0}_PCI'.format(transform.replace('_GRP', 'Grp')))
        cmds.setAttr('{0}.turnOnPercentage'.format(pci), 1)
        mdl = cmds.createNode('multDoubleLinear', n='{0}_MDL'.format(transform.replace('_GRP', 'Grp')))
        cmds.connectAttr('{0}.outputX'.format(mdn), '{0}.input1'.format(mdl))
        destAttr = '{0}.inputCurve'.format(pci)
        cmds.connectAttr(crvShapeAttr, destAttr, f=1)
        pos = cmds.xform(transform, q=1, ws=1, rp=1)
        # update nearest point on curve to get param
        cmds.setAttr('{0}.inPosition'.format(npoc), pos[0], pos[1], pos[2])
        param = cmds.getAttr('{0}.parameter'.format(npoc))
        cmds.setAttr('{0}.input2'.format(mdl), param)
        # cmds.setAttr('{0}.parameter'.format(pci), param)
        cmds.connectAttr('{0}.output'.format(mdl), '{0}.parameter'.format(pci))
        pciGrp = cmds.createNode('transform', n='{0}_GRP'.format(transform.replace('_GRP', 'GrpPci')))
        cmds.connectAttr('{0}.positionX'.format(pci), '{0}.tx'.format(pciGrp))
        cmds.connectAttr('{0}.positionY'.format(pci), '{0}.ty'.format(pciGrp))
        cmds.connectAttr('{0}.positionZ'.format(pci), '{0}.tz'.format(pciGrp))
        cmds.parent(pciGrp, cmds.listRelatives(transform, parent=1)[0])
        cmds.orientConstraint(closestTrs, pciGrp, mo=1)
        cmds.parentConstraint(pciGrp, transform, mo=1)
    cmds.delete(npoc)
    
def getDagPath(node=None):
    sel = om.MSelectionList()
    sel.add(node)
    d = om.MDagPath()
    sel.getDagPath(0, d)
    return d

def getLocalOffset(parent, child):
    parentWorldMatrix = getDagPath(parent).inclusiveMatrix()
    childWorldMatrix = getDagPath(child).inclusiveMatrix()
    return childWorldMatrix * parentWorldMatrix.inverse()
    
def matrixConstraint(master, slave, mode="create", maintainOffset=False):
    """Creates a matrix constraint between the master and slave targets
    
    TODO:
    [] Add offset
    [] Prep for joints
    [] Fix remove function (Do a proper check to find correct connections)
    
    Args:
        master (str): The driver target
        slave (str): The driven target
        
    """
    if not cmds.pluginInfo('matrixNodes', q=1, l=1):
        try: cmds.loadPlugin('matrixNodes')
        except: raise RuntimeError('Unable to load the matrixNodes plugin!')
    
    if mode == "create" and not maintainOffset:
        mxMult = cmds.createNode("multMatrix", n=names.addModifier(slave, 'multMatrix'))
        mxDecom = cmds.createNode("decomposeMatrix", n=names.addModifier(slave, 'decomposeMatrix'))
        
        cmds.connectAttr("{0}.{1}".format(master, "worldMatrix"), "{0}.{1}".format(mxMult, "matrixIn[0]"), f=1)
        cmds.connectAttr("{0}.{1}".format(slave, "parentInverseMatrix"), "{0}.{1}".format(mxMult, "matrixIn[1]"), f=1)
        cmds.connectAttr("{0}.{1}".format(mxMult, "matrixSum"), "{0}.{1}".format(mxDecom, "inputMatrix"), f=1)
        
        # output results on the slave transform
        # cmds.connectAttr("{0}.{1}".format(mxDecom, "outputTranslate"), "{0}.{1}".format(slave, "translate"), f=1)
        # cmds.connectAttr("{0}.{1}".format(mxDecom, "outputRotate"), "{0}.{1}".format(slave, "rotate"), f=1)
        # cmds.connectAttr("{0}.{1}".format(mxDecom, "outputScale"), "{0}.{1}".format(slave, "scale"), f=1)
        for attr in ['x', 'y', 'z']:
            capAttr = attr.upper()
            cmds.connectAttr("{0}.{1}{2}".format(mxDecom, "outputTranslate", capAttr), "{0}.{1}{2}".format(slave, "translate", capAttr), f=1)
            cmds.connectAttr("{0}.{1}{2}".format(mxDecom, "outputRotate", capAttr), "{0}.{1}{2}".format(slave, "rotate", capAttr), f=1)
            cmds.connectAttr("{0}.{1}{2}".format(mxDecom, "outputScale", capAttr), "{0}.{1}{2}".format(slave, "scale", capAttr), f=1)
        cmds.connectAttr("{0}.outputShearX".format(mxDecom), "{0}.shearXY".format(slave), f=1)
        cmds.connectAttr("{0}.outputShearY".format(mxDecom), "{0}.shearXZ".format(slave), f=1)
        cmds.connectAttr("{0}.outputShearZ".format(mxDecom), "{0}.shearYZ".format(slave), f=1)
        
    elif mode == "create" and maintainOffset:
        mxMult = cmds.createNode("multMatrix", n=names.addModifier(slave, 'multMatrix'))
        mxDecom = cmds.createNode("decomposeMatrix", n=names.addModifier(slave, 'decomposeMatrix'))
        # multiply
        # 0 - slave world matrix * master world inverse matrix 
        # 1 - master world matrix
        # 2 - slave parent inverse matrix
        localOffset = getLocalOffset(master, slave)
        cmds.setAttr( "{0}.{1}".format(mxMult, "matrixIn[0]"), [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
        cmds.connectAttr("{0}.{1}".format(master, "worldMatrix"), "{0}.{1}".format(mxMult, "matrixIn[1]"), f=1)
        cmds.connectAttr("{0}.{1}".format(slave, "parentInverseMatrix"), "{0}.{1}".format(mxMult, "matrixIn[2]"), f=1)
        cmds.connectAttr("{0}.{1}".format(mxMult, "matrixSum"), "{0}.{1}".format(mxDecom, "inputMatrix"), f=1)
        
        # output results on the slave transform
        for attr in ['x', 'y', 'z']:
            capAttr = attr.upper()
            cmds.connectAttr("{0}.{1}{2}".format(mxDecom, "outputTranslate", capAttr), "{0}.{1}{2}".format(slave, "translate", capAttr), f=1)
            cmds.connectAttr("{0}.{1}{2}".format(mxDecom, "outputRotate", capAttr), "{0}.{1}{2}".format(slave, "rotate", capAttr), f=1)
            cmds.connectAttr("{0}.{1}{2}".format(mxDecom, "outputScale", capAttr), "{0}.{1}{2}".format(slave, "scale", capAttr), f=1)
        cmds.connectAttr("{0}.outputShearX".format(mxDecom), "{0}.shearXY".format(slave), f=1)
        cmds.connectAttr("{0}.outputShearY".format(mxDecom), "{0}.shearXZ".format(slave), f=1)
        cmds.connectAttr("{0}.outputShearZ".format(mxDecom), "{0}.shearYZ".format(slave), f=1)
        
        # Crude accomodation for joint orient
        if cmds.objectType(slave) == 'joint':
            cmds.setAttr('{0}.jo'.format(slave), 0, 0, 0)

    elif mode == "remove":
        mxMult = ""
        mxDecom = ""
        
        outCon = cmds.listConnections(master, s=0)
        for i in outCon:
            if cmds.objectType(i) == "multMatrix":
                mxMult = i
        
        inCon = cmds.listConnections(slave, d=0)
        for i in inCon:
            if cmds.objectType(i) == "decomposeMatrix":
                mxDecom = i
        
        if mxMult and mxDecom:
            cmds.disconnectAttr("{0}.{1}".format(master, "worldMatrix"), "{0}.{1}".format(mxMult, "matrixIn[0]"))
            cmds.disconnectAttr("{0}.{1}".format(slave, "parentInverseMatrix"), "{0}.{1}".format(mxMult, "matrixIn[1]"))
            cmds.disconnectAttr("{0}.{1}".format(mxMult, "matrixSum"), "{0}.{1}".format(mxDecom, "inputMatrix"))
            
            cmds.disconnectAttr("{0}.{1}".format(mxDecom, "outputTranslate"), "{0}.{1}".format(slave, "translate"))
            cmds.disconnectAttr("{0}.{1}".format(mxDecom, "outputRotate"), "{0}.{1}".format(slave, "rotate"))
            cmds.disconnectAttr("{0}.{1}".format(mxDecom, "outputScale"), "{0}.{1}".format(slave, "scale"))


def listAllParents(node):
    """Recursively list all parent transforms
    """
    retList = []
    parent = cmds.listRelatives(node, parent=1)
    if parent:
        retList = parent + listAllParents(parent[0])
    return retList
