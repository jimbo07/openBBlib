'''
Created on 4 Oct 2018

@author: lasse-r
'''

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma

from ooutdmaya.rigging.core.util import easy


def isDeformer(deformer):
    ''' Test if node is a valid deformer
    :param deformer str: Name of deformer to query
    :return: True if node is valid
    :rtype: bool
    '''
    # Check Deformer Exists
    if not cmds.objExists(deformer): return False
    
    # Check Deformer Type
    nodeType = cmds.nodeType(deformer,i=1)
    if not nodeType.count('geometryFilter'): return False
    
    # Return result
    return True


def getDeformerFn(deformer):
    ''' Initialize and return an MFnWeightGeometryFilter function set attached to the specified deformer
    :param deformer str: Name of deformer to create function set for
    :return: MFnWeightGeometryFilter function set on deformer
    :rtype: class obj
    '''
    # Checks
    if not cmds.objExists(deformer):
        raise Exception('Deformer {0} does not exist!'.format(deformer))
    
    # Get MFnWeightGeometryFilter
    deformerObj = easy.getMObject(deformer)
    try: deformerFn = oma.MFnWeightGeometryFilter(deformerObj)
    except: raise Exception('Could not get a geometry filter for deformer {0}!'.format(deformer))
    
    # Return result
    return deformerFn


def getDeformerSet(deformer):
    ''' Return the deformer set name associated with the specified deformer
    :param deformer str: Name of deformer to return the deformer set for
    '''
    # Checks
    if not cmds.objExists(deformer):
        raise Exception('Deformer {0} does not exist!'.format(deformer))
    
    # Verify input
    if not isDeformer(deformer):
        raise Exception('Object {0} is not a valid deformer!'.format(deformer))
    
    # Get Deformer Set
    deformerObj = easy.getMObject(deformer)
    deformerFn = oma.MFnGeometryFilter(deformerObj)
    deformerSetObj = deformerFn.deformerSet()
    
    if deformerSetObj.isNull():
        raise Exception('Unable to determine deformer set for {0}!'.format(deformer))
    
    # Return Result
    return om.MFnDependencyNode(deformerSetObj).name()


def getDeformerSetFn(deformer):
    ''' Initialize and return an MFnSet function set attached to the deformer set of the specified deformer
    :param deformer str: Name of deformer attached to the deformer set to create function set for
    :return: the deformerSetFn
    :rtype: str
    '''
    # Checks
    if not cmds.objExists(deformer):
        raise Exception('Deformer {0} does not exist!'.format(deformer))
    
    # Get deformer set
    deformerSet = getDeformerSet(deformer)
    
    # Get MFnWeightGeometryFilter
    deformerSetObj = easy.getMObject(deformerSet)
    deformerSetFn = om.MFnSet(deformerSetObj)
    
    # Return result
    return deformerSetFn


def getGeomIndex(geo, deformer):
    ''' Returns the geometry index of a shape to a specified deformer.
    :param geometry str: Name of shape or parent transform to query
    :param deformer str: Name of deformer to query
    :return: the geometry index of a shape on specified deformer
    :rtype: str
    '''
    # Verify input
    if not isDeformer(deformer):
        raise Exception('Object {0} is not a valid deformer!'.format(deformer))
    
    # Check geometry
    if cmds.objectType(geo) == 'transform':
        try: geo = cmds.listRelatives(geo, s=True, ni=True, pa=True)[0]
        except: raise Exception('Object {0} is not a valid geometry!'.format(geo))
        
    geomObj = easy.getMObject(geo)
    
    # Get geometry index
    deformerObj = easy.getMObject(deformer)
    deformerFn = oma.MFnGeometryFilter(deformerObj)
    try: geomIndex = deformerFn.indexForOutputShape(geomObj)
    except: raise Exception('Object {0} is not affected by deformer {1}'.format(geo, deformer))
    
    # return result
    return geomIndex

def getAffectedGeometry(deformer,returnShapes=False,fullPathNames=False):
    ''' Return a dictionary containing information about geometry affected by
        a specified deformer. Dictionary keys correspond to affected geometry names,
        values indicate geometry index to deformer.
    :param deformer str: Name of deformer to query
    :param returnShapes bool: Return shape instead of parent transform name
    :param fullPathNames bool: Return full path names of affected objects
    :return: dictionary of affected geo
    :rtype: dict
    '''
    # Verify Input
    if not isDeformer(deformer):
        raise Exception('Object {0} is not a valid deformer!'.format(deformer))
    
    # Initialize Return Array (dict)
    affectedObjects = {}
    
    # Get MFnGeometryFilter
    deformerObj = easy.getMObject(deformer)
    geoFilterFn = oma.MFnGeometryFilter(deformerObj)
    
    # Get Output Geometry
    outputObjectArray = om.MObjectArray()
    geoFilterFn.getOutputGeometry(outputObjectArray)
    
    # Iterate Over Affected Geometry
    for i in range(outputObjectArray.length()):
        
        # Get Output Connection at Index
        outputIndex = geoFilterFn.indexForOutputShape(outputObjectArray[i])
        outputNode = om.MFnDagNode(outputObjectArray[i])
        
        # Check Return Shapes
        if not returnShapes: outputNode = om.MFnDagNode(outputNode.parent(0))
        
        # Check Full Path
        if fullPathNames: affectedObjects[outputNode.fullPathName()] = outputIndex
        else: affectedObjects[outputNode.partialPathName()] = outputIndex
    
    # Return Result
    return affectedObjects


def getDeformerSetMembers(deformer,geometry=''):
    ''' Return the deformer set members of the specified deformer.
        You can specify a shape name to query deformer membership for.
        Otherwise, membership for the first affected geometry will be returned.
        Results are returned as a list containing an MDagPath to the affected shape and an MObject for the affected components.
    :param deformer str: Deformer to query set membership for
    :param geometry str: Geometry to query deformer set membership for. Optional.
    '''
    # Get deformer function sets
    deformerSetFn = getDeformerSetFn(deformer)
    
    # Get deformer set members
    deformerSetSel = om.MSelectionList()
    deformerSetFn.getMembers(deformerSetSel,True)
    deformerSetPath = om.MDagPath()
    deformerSetComp = om.MObject()
    
    # Get geometry index
    if geometry: geomIndex = getGeomIndex(geometry,deformer)
    else: geomIndex = 0
    
    # Get number of selection components
    deformerSetLen = deformerSetSel.length()
    if geomIndex >= deformerSetLen:
        raise Exception('Geometry index out of range! (Deformer: "'+deformer+'", Geometry: "'+geometry+'", GeoIndex: '+str(geomIndex)+', MaxIndex: '+str(deformerSetLen)+')')
    
    # Get deformer set members
    deformerSetSel.getDagPath(geomIndex,deformerSetPath,deformerSetComp)
    
    # Return result
    return [deformerSetPath,deformerSetComp]


def getDeformerSetMemberIndices(deformer, geo=''):
    ''' Return a list of deformer set member vertex indices
    :param deformer str: Deformer to set member indices for
    :param geometry str: Geometry to query deformer set membership for.
    '''
    # Check geometry
    if cmds.objectType(geo) == 'transform':
        try: geo = cmds.listRelatives(geo, s=True, ni=True, pa=True)[0]
        except: raise Exception('Object {0} is not a valid geometry!'.format(geo))
        
    # Get geometry type
    geometryType = cmds.objectType(geo)
    
    # Get deformer set members
    deformerSetMem = getDeformerSetMembers(deformer, geo)
    
    # Get Set Member Indices 
    memberIdList = []
    
    # Single Index
    if geometryType == 'mesh' or geometryType == 'nurbsCurve' or geometryType == 'particle':
        memberIndices = om.MIntArray()
        singleIndexCompFn = om.MFnSingleIndexedComponent(deformerSetMem[1])
        singleIndexCompFn.getElements(memberIndices)
        memberIdList = list(memberIndices)
    
    # Double Index
    if geometryType == 'nurbsSurface':
        memberIndicesU = om.MIntArray()
        memberIndicesV = om.MIntArray()
        doubleIndexCompFn = om.MFnDoubleIndexedComponent(deformerSetMem[1])
        doubleIndexCompFn.getElements(memberIndicesU, memberIndicesV)
        for i in range(memberIndicesU.length()):
            memberIdList.append([memberIndicesU[i], memberIndicesV[i]])
    
    # Triple Index
    if geometryType == 'lattice':
        memberIndicesS = om.MIntArray()
        memberIndicesT = om.MIntArray()
        memberIndicesU = om.MIntArray()
        tripleIndexCompFn = om.MFnTripleIndexedComponent(deformerSetMem[1])
        tripleIndexCompFn.getElements(memberIndicesS, memberIndicesT, memberIndicesU)
        for i in range(memberIndicesS.length()):
            memberIdList.append([memberIndicesS[i], memberIndicesT[i], memberIndicesU[i]])
        
    # Return result
    return memberIdList


def getWeights(deformer, geometry=None):
    ''' Get the weights for the specified deformer
    :param deformer str: Deformer to get weights for
    :param geometry str: Target geometry to get weights from
    :return: list of weights for specified deformer
    :rtype: list
    '''
    # Verify input
    if not isDeformer(deformer):
        raise Exception('Object {0} is not a valid deformer!'.format(deformer))
    
    # Check Geometry
    if not geometry:
        geometry = getAffectedGeometry(deformer).keys()[0]
    
    # Get Geometry Shape
    geoShape = geometry
    if geometry and cmds.objectType(geoShape) == 'transform':
        geoShape = cmds.listRelatives(geometry, s=True, ni=True)[0]
    
    # Get deformer function set and members
    deformerFn = getDeformerFn(deformer)
    deformerSetMem = getDeformerSetMembers(deformer, geoShape)
    
    # Get weights
    weightList = om.MFloatArray()
    deformerFn.getWeights(deformerSetMem[0], deformerSetMem[1], weightList)
    
    # Return result
    return list(weightList)


def setWeights(deformer, weights, geometry=None):
    ''' Set the weights for the specified deformer using the input value list
    :param deformer str: Deformer to set weights for
    :param weights list: Input weight value list
    :param geometry str: Target geometry to apply weights to. If None, use first affected geometry.
    '''
    # Verify input
    if not isDeformer(deformer):
        raise Exception('Object {0} is not a valid deformer!'.format(deformer))
    
    # Check Geometry
    if not geometry:
        geometry = getAffectedGeometry(deformer).keys()[0]
        
    # Get Geometry Shape
    geoShape = geometry
    geoObj = easy.getMObject(geometry)
    if geometry and geoObj.hasFn(om.MFn.kTransform):
        geoShape = cmds.listRelatives(geometry, s=True, ni=True)[0]
    
    # Get deformer function set and members
    deformerFn = getDeformerFn(deformer)
    deformerSetMem = getDeformerSetMembers(deformer, geoShape)
    
    # Build weight array
    weightList = om.MFloatArray()
    [weightList.append(i) for i in weights]
    
    # Set weights
    deformerFn.setWeight(deformerSetMem[0], deformerSetMem[1], weightList)


