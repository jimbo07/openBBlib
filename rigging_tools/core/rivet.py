"""Mesh constraint functions
"""
import os
from maya import cmds, mel
import maya.OpenMaya as om

from ooutdmaya.rigging.core.util import names
from ooutdmaya.rigging.core.util.mesh import lib

animFilName = 'ooutdRigRivet.mel'
# Source any mel files in our install location
# __file__ = '/jobs/foxtest/tools/maya/ooutdmaya/scripts/ooutdmaya/animation/cMotionTrail.py'
# __file__ = '/home/jarl-m/eclipse-workspace/ooutd/ooutdmaya/animation/cMotionTrail.py'
# __file__ = '/jobs/foxtest/tools/maya/ooutdmaya/python/ooutdmaya/animation/cMotionTrail.py'
# __file__ = '/home/jarl-m/eclipse-workspace/ooutd/ooutdmaya/animation/cMotionTrail.py'
# split = __file__.split('scripts/ooutdmaya')
try:
    print 'melFile exists in install location:\n\t{0}'.format(animFilName)
    mel.eval('source "{0}";'.format(animFilName))
except:
    print 'melFile does not exist in install location:\n\t{0}'.format(animFilName)
# Override if this python module is locatedin our sandbox location
melFile = os.path.join(os.path.dirname(__file__), 'mel')
melFile = os.path.join(melFile, animFilName)
if os.path.exists(melFile):
    print 'melFile exists in sandbox location:\n\t{0}'.format(melFile)
    mel.eval('source "{0}";'.format(melFile))
    

def attachTransformsToMesh(transformList=[], geo=None, useRivet=True):
    
    # Constrain the transform
    if useRivet:
        rivetData = auto_rivet_transforms_to_meshes([geo]+transformList)
        locShapes = cmds.listRelatives(rivetData['loc'], type='locator')
        if locShapes:
            cmds.hide(locShapes)
        return rivetData
            
    """Attaches (a) transform(s) to a mesh using the pointOnPolyConstraint node
    
    :param transformList: list of transforms to constrain
    :param geo: geo to drive transform constraint
    :type mo: string
    :type selection: string
    :returns: list of result pointOnPolyConstraint nodes or rivet constrained data
    :rtype: list
    
    **Directions**
    Select the transforms you want to constrain,
    then shift select the mesh you want to constrain them to,
    then run the command. Alternatively you can 
    pass in a transformList and a geo argument instead
    of relying on selection

    :Example:
    
    from ooutdmaya.rigging.core.util.mesh import rivet
    rivet.attachTransformsToMesh()
    
    .. warning:: Expects non-overlapping UVs
    """
    uValueAttr = 'meshConstraintU'
    vValueAttr = 'meshConstraintV'
    # if no arguments passed, work on selection
    if not geo:
        try:
            sel = cmds.ls(sl= True)
            geo = sel[-1]
            transformList = sel[:-1]
        except Exception, e:
            raise RuntimeError('Invalid Selection,\n\t{0}'.format(e))
    # Query Info
    uvSetName = cmds.polyUVSet(geo, q=1, currentUVSet=1)[0]
    # closestPointOnMesh
    cpom = cmds.createNode('closestPointOnMesh')
    mesh = lib.getMeshShape(geo)
    sourceAttr = '{0}.outMesh'.format(mesh)
    destAttr = '{0}.inMesh'.format(cpom)
    cmds.connectAttr(sourceAttr, destAttr)
    popcList = []
    for transform in transformList:
        # set position values on closestPointOnMesh
        pos = cmds.xform(transform, q=1, rp=1, ws=1)
        for i, attr in enumerate(['x', 'y', 'z']):
            plugAttr = '{0}.inPosition.inPosition{1}'.format(cpom, attr.upper())
            cmds.setAttr(plugAttr, pos[i])
        # build the pointOnPolyConstraint
        # using the position values from the closestPointOnMesh
        popc = cmds.createNode('pointOnPolyConstraint', 
            n=names.addModifier(transform, 'pointOnPolyConstraint'))
        popcList.append(popc)
        cmds.parent(popc, transform)
        sourceAttr = '{0}.worldMesh[0]'.format(geo)
        destAttr = '{0}.target[0].targetMesh'.format(popc)
        cmds.connectAttr(sourceAttr, destAttr)
        
        uVal = cmds.getAttr('{0}.parameterU'.format(cpom))
        vVal = cmds.getAttr('{0}.parameterV'.format(cpom))
        
        cmds.setAttr('{0}.target[0].targetUVSetName'.format(popc), uvSetName, type='string')
        # cmds.setAttr('{0}.target[0].targetU'.format(popc), uVal)
        cmds.addAttr(transform, at='double', ln=uValueAttr, k=1, dv=uVal, min=0, max=1)
        cmds.connectAttr(
            '{0}.{1}'.format(transform, uValueAttr),
            '{0}.target[0].targetU'.format(popc), f=1)
        # cmds.setAttr('{0}.target[0].targetV'.format(popc), vVal)
        cmds.addAttr(transform, at='double', ln=vValueAttr, k=1, dv=vVal, min=0, max=1)
        cmds.connectAttr(
            '{0}.{1}'.format(transform, vValueAttr),
            '{0}.target[0].targetV'.format(popc), f=1)
        
        for attr in ['x', 'y', 'z']:
            # translate
            sourceAttr = '{0}.constraintTranslate{1}'.format(popc, attr.upper())
            destAttr = '{0}.translate{1}'.format(transform, attr.upper())
            cmds.connectAttr(sourceAttr, destAttr)
            # rotate
            sourceAttr = '{0}.constraintRotate{1}'.format(popc, attr.upper())
            destAttr = '{0}.rotate{1}'.format(transform, attr.upper())
            cmds.connectAttr(sourceAttr, destAttr)
    cmds.delete(cpom)
    return popcList

# Grabbed from Ziva Dynamics, original made by Andy van Straten


def get_mdagpath_from_object_name(object_name):
    '''
    Returns the corresponding MDagPath object based on the objectName as a string. 

    Accepts:
        objectName - string

    Returns: 
        MDagPath object


    '''#
    selList = om.MSelectionList()
    selList.add(object_name)  
    dagPath = om.MDagPath()
    it = om.MItSelectionList(selList)
    it.getDagPath(dagPath)
  
    return dagPath


def auto_rivet_transforms_to_meshes(everything_list): 
    '''
    TO DO: This script assumes you have rivet.mel in your scripts directory
    '''

    '''  
    Description: 
        Given a list containing transforms and meshes, find the closest point on mesh from all 
        given meshes (so the closest of all closest points) And build a rivet on that mesh at 
        that point. Parent the transform under the rivet locator. 
      
    Accepts: 
        A list of transforms and meshes. 

    Returns: None
  
    '''

    lookupMeshes_dict = dict()
    transforms_list = list()
    inMesh_list = list()

    for item in everything_list: 
        shapes = cmds.listRelatives(item, shapes=True)
        if shapes != None: 
            if cmds.objectType(shapes[0]) == 'mesh': 
                mesh_mfnMesh = om.MFnMesh(get_mdagpath_from_object_name(shapes[0]))
                lookupMeshes_dict[item] = mesh_mfnMesh
            else: 
                transforms_list.append(item)
        elif cmds.objectType(item) == 'mesh':
            mesh_mfnMesh = om.MFnMesh(get_mdagpath_from_object_name(item))
            lookupMeshes_dict[item] = mesh_mfnMesh
        else: 
            transforms_list.append(item)
                        
    for transform in transforms_list: 
        closestDistance = 10e10
        closestMesh = None
        closestPolygon = None
        p = cmds.xform(transform, q=True, rp=True, ws=True, a=True)
        lookup_mPoint = om.MPoint(p[0], p[1], p[2])
        lookup_mFloatPoint = om.MFloatPoint(lookup_mPoint.x, lookup_mPoint.y, lookup_mPoint.z)

        closestPolygon_mScriptUtil = om.MScriptUtil()

        for lookupMesh in lookupMeshes_dict.keys(): 
            currMesh_mfnMesh = lookupMeshes_dict[ lookupMesh ]
          
            closest_mPoint = om.MPoint()
            closest_mScriptUtil = om.MScriptUtil()
            closestPolygon_ptr = closest_mScriptUtil.asIntPtr()
          
            currMesh_mfnMesh.getClosestPoint(lookup_mPoint, closest_mPoint, om.MSpace.kWorld, closestPolygon_ptr)
    
            closestPolygon_currIndex = closest_mScriptUtil.getInt(closestPolygon_ptr)
    
            closest_mFloatPoint = om.MFloatPoint(closest_mPoint.x, closest_mPoint.y, closest_mPoint.z)
    
            d = closest_mFloatPoint.distanceTo(lookup_mFloatPoint)
            if d < closestDistance: 
                closestDistance = d
                closestMesh = lookupMesh
                closestPolygon = closestPolygon_currIndex

        prevIndex_util = om.MScriptUtil()        
        meshName_mItMeshPolygon = om.MItMeshPolygon(get_mdagpath_from_object_name(closestMesh))
        meshName_mItMeshPolygon.setIndex(closestPolygon, prevIndex_util.asIntPtr())

        edges_mIntArray = om.MIntArray()
        meshName_mItMeshPolygon.getEdges(edges_mIntArray)

        cmds.select(closestMesh + '.e[%i]' % edges_mIntArray[0], r=True)
        cmds.select(closestMesh + '.e[%i]' % edges_mIntArray[2], add=True)
        
        # Source the MEL file
        '''
        melFile = __file__.replace('.pyc', '.mel')
        if melFile[-4:] == '.mel':
            # mel.eval('catchQuiet("source \\\"'+str(melFile)+'\\\"")')
            mel.eval('source "{0}";'.format(melFile))
        else:
            melFile = __file__.replace('.py', '.mel')
            mel.eval('source "{0}";'.format(melFile))
        '''
            
        rivetLocator_str = mel.eval('rivet;')
        rivetLocator_str[0] = cmds.rename(rivetLocator_str[0], transform + '_rivet')
        cfme1 = cmds.rename(rivetLocator_str[1], '{0}_rivetCurveFromMeshEdge1'.format(transform))
        cfme2 = cmds.rename(rivetLocator_str[2], '{0}_rivetCurveFromMeshEdge2'.format(transform))
        inMesh_list.append('{0}.im'.format(cfme1))
        inMesh_list.append('{0}.im'.format(cfme2))

        cmds.parent(transform, rivetLocator_str[0]) 
    
    return {'inMeshAttrs':inMesh_list, 'loc':rivetLocator_str[0]}
    
