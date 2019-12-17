'''
Created on 4 Oct 2018

@author: lasse-r
'''

import maya.cmds as cmds
import maya.OpenMaya as om

from ooutdmaya.rigging.core.util import easy


def getComponentIndexList(componentList=[]):
    ''' Return an list of integer component index values
    :param componentList list: A list of component names. if empty will default to selection.
    :return: list of integer component index values
    :rtype: list
    '''
    # Initialize return dictionary
    componentIndexList = {}
    
    # Check string input
    if type(componentList) == str or type(componentList) == unicode:
        componentList = [componentList]
    
    # Get selection if componentList is empty
    if not componentList: componentList = cmds.ls(sl=True, fl=True) or []
    if not componentList: return []
    
    # Get MSelectionList
    selList = om.MSelectionList()
    for i in componentList: selList.add(str(i))
    
    # Iterate through selection list
    selPath = om.MDagPath()
    componentObj = om.MObject()
    componentSelList = om.MSelectionList()
    for i in range(selList.length()):
        # Check for valid component selection
        selList.getDagPath(i,selPath,componentObj)
        if componentObj.isNull():
            # Clear component MSelectionList
            componentSelList.clear()
            # Get current object name
            objName = selPath.partialPathName()
            
            # Transform
            if selPath.apiType() == om.MFn.kTransform:
                numShapesUtil = om.MScriptUtil()
                numShapesUtil.createFromInt(0)
                numShapesPtr = numShapesUtil.asUintPtr()
                selPath.numberOfShapesDirectlyBelow(numShapesPtr)
                numShapes = om.MScriptUtil(numShapesPtr).asUint()
                selPath.extendToShapeDirectlyBelow(numShapes-1)
            
            # Mesh
            if selPath.apiType() == om.MFn.kMesh:
                meshFn = om.MFnMesh(selPath.node())
                vtxCount = meshFn.numVertices()
                componentSelList.add("{0}.vtx[0:{1}]".format(objName, str(vtxCount-1)))
            # Curve
            elif selPath.apiType() == om.MFn.kNurbsCurve:
                curveFn = om.MFnNurbsCurve(selPath.node())
                componentSelList.add("{0}.cv[0:{1}]".format(objName, str(curveFn.numCVs()-1)))
            # Surface
            elif selPath.apiType() == om.MFn.kNurbsSurface:
                surfaceFn = om.MFnNurbsSurface(selPath.node())
                componentSelList.add("{0}.cv[0:{1}][0:{2}]".format(objName, str(surfaceFn.numCVsInU()-1), str(surfaceFn.numCVsInV()-1)))
            # Lattice
            elif selPath.apiType() == om.MFn.kLattice:
                sDiv = cmds.getAttr('{0}.sDivisions'.format(objName))
                tDiv = cmds.getAttr('{0}.tDivisions'.format(objName))
                uDiv = cmds.getAttr('{0}.uDivisions'.format(objName))
                componentSelList.add("{0}.pt[0:{1}][0:{2}][0:{3}]".format(objName, str(sDiv -1), str(tDiv -1), str(uDiv -1)))
            # Get object component MObject
            componentSelList.getDagPath(0,selPath,componentObj)
        
        # =======================
        # - Check Geometry Type -
        # =======================
        
        # MESH / NURBS CURVE
        if (selPath.apiType() == om.MFn.kMesh) or (selPath.apiType() == om.MFn.kNurbsCurve):
            indexList = om.MIntArray()
            componentFn = om.MFnSingleIndexedComponent(componentObj)
            componentFn.getElements(indexList)
            componentIndexList[selPath.partialPathName()] = list(indexList)
        
        # NURBS SURFACE
        if selPath.apiType() == om.MFn.kNurbsSurface:
            indexListU = om.MIntArray()
            indexListV = om.MIntArray()
            componentFn = om.MFnDoubleIndexedComponent(componentObj)
            componentFn.getElements(indexListU,indexListV)
            componentIndexList[selPath.partialPathName()] = zip(list(indexListU),list(indexListV))
        
        # LATTICE
        if selPath.apiType() == om.MFn.kLattice:
            indexListS = om.MIntArray()
            indexListT = om.MIntArray()
            indexListU = om.MIntArray()
            componentFn = om.MFnTripleIndexedComponent(componentObj)
            componentFn.getElements(indexListS,indexListT,indexListU)
            componentIndexList[selPath.partialPathName()] = zip(list(indexListS),list(indexListT),list(indexListU))
    
    # Return Result
    return componentIndexList


def getMultiIndex(obj, index):
    ''' Convert a single element index to a 2 or 3 element index .
    :param obj str: Object parent of component.
    :param index list: Single element index of component.
    :return: Returns the multi element index of the given component.
    :rtype: list
    '''
    # Get shape node
    if cmds.objectType(obj) == 'transform':
        obj = easy.getShapes(obj, True, False)[0]
    
    # Mesh
    if cmds.objectType(obj) == 'mesh':
        print('Component specified is a mesh vertex! No multi index information for single element indices!!')
        return [index]
    
    # Nurbs Curve
    if cmds.objectType(obj) == 'nurbsCurve':
        print('Component specified is a curve CV! No multi index information for single element indices!!')
        return [index]
    
    # Nurbs Surface
    if cmds.objectType(obj) == 'nurbsSurface':
        # Spans / Degree / Form
        spansV = cmds.getAttr('{0}.spansV'.format(obj))
        degreeV = cmds.getAttr('{0}.degreeV'.format(obj))
        formV = cmds.getAttr('{0}.formV'.format(obj))
        if formV: spansV -= degreeV
        # Get Multi Index
        uIndex = int(index/(spansV+degreeV))
        vIndex = index%(spansV+degreeV)
        return [uIndex,vIndex]
    
    # Lattice
    elif cmds.objectType(obj) == 'lattice':
        sDiv = cmds.getAttr('{0}.sDivisions'.format(obj))
        tDiv = cmds.getAttr('{0}.tDivisions'.format(obj))
        uDiv = cmds.getAttr('{0}.uDivisions'.format(obj))
        sInd = int(index%sDiv)
        tInd = int((index/sDiv)%tDiv)
        uInd = int((index/(sDiv*tDiv))%uDiv)
        return [sInd,tInd,uInd]
    

def getComponentStrList(geometry,componentIndexList=[]):
    ''' Return a string list containing all the component points of the specified geometry object
    :param geometry str: Geometry to return components for
    :param componentIndexList list: Component indices to return names for. If empty, all components will be returned
    :return: string list w/ all points of specified geo
    :rtype: list
    '''
    # Check object
    if not cmds.objExists(geometry):
        raise Exception('Object {0} does not exist!'.format(geometry))
    
    # Check transform
    mObj = easy.getMObject(geometry)
    if mObj.hasFn(om.MFn.kTransform):
        geometry = easy.getShapes(geometry,True,False)
        if geometry: geometry = geometry[0]
        else: raise Exception('Object {0} is not a valid geometry object!'.format(geometry))
    
    # Check type
    mObj = easy.getMObject(geometry)
    if not mObj.hasFn(om.MFn.kShape):
        raise Exception('Object {0} is not a valid geometry object!'.format(geometry))
    
    # Get component multiIndex list
    componentStrList = []
    componentList = []
    if not componentIndexList:
        componentList = getComponentIndexList(geometry)[geometry]
    else:
        for i in componentIndexList:
            index = getMultiIndex(geometry,i)
            if len(index) == 1: componentList.append( index[0] )
            else: componentList.append( index )
    
    objType = cmds.objectType(geometry)
    for i in componentList:
        # Mesh
        if objType == 'mesh':
            componentStrList.append('{0}.vtx[{1}]'.format(geometry, str(i)))
        # Curve
        if objType == 'nurbsCurve':
            componentStrList.append('{0}.cv[{1}]'.format(geometry, str(i)))

        # Surface
        if objType == 'nurbsSurface':
            componentStrList.append("{0}.cv[{1}][{2}]".format(geometry, str(i[0]), str(i[1])))
            
        # Lattice
        if objType == 'lattice':
            componentStrList.append("{0}.pt[{1}][{2}][{3}]".format(geometry, str(i[0]), str(i[2])))
    
    # Return Component String List
    return componentStrList

def getSelectionElement(selection, element=0):
    ''' Return the selection components (MDagPath object, MObject component)
        for the specified element of the input selection list
    :param selection list/str: Selection to return the element components for.
    :param element int: Element of the selection to return selection components for.
    :return: selection components
    :rtype: list
    '''
    # Initialize function wrappers
    selectionList = om.MSelectionList()
    selectionPath = om.MDagPath()
    selectionObj = om.MObject()
    
    # Build selection list
    if type(selection) == str or type(selection) == unicode: selection = [str(selection)]
    [selectionList.add(i) for i in selection]
    
    # Check length
    if element >= selectionList.length():
        raise Exception('Element value ({0}) out of range!'.format(str(element)))
    
    # Get selection elements
    selectionList.getDagPath(element,selectionPath,selectionObj)
    
    # Return result
    return [selectionPath,selectionObj]


def singleIndexList(componentList):
    ''' Only works for single indexed components, such as mesh vertices, faces, edges or NURBS curve CV's.
        All components should be from the same shape/geometry. If components of multiple shapes are selected, only components of the first shape will be used.
    :param componentList list: The component list to return the indices for.
    :return: Return a list of component indices for the specified component list.
    :rtype: list
    '''
    # Get Selection Elements
    sel = getSelectionElement(componentList,element=0)
    # Get Component Indices
    indexList =  om.MIntArray()
    componentFn = om.MFnSingleIndexedComponent(sel[1])
    componentFn.getElements(indexList)
    # Return result
    return list(indexList)


def getSingleIndexComponentList(componentList=[]):
    ''' Convert a 2 or 3 value component index to a single value index.
    :param componentList list: A list of component names. if empty will default to selection.
    :return: Returns a flat list of integer component index values.
    :rtype: list
    '''
    # Check Component List
    if not componentList: componentList = cmds.ls(sl=True)
    if not componentList: return singleIndexList
    
    # Initialize Result
    singleIndexList = {}
    
    # Get Component Selection
    componentSel = getComponentIndexList(componentList)
    
    # Iterate Through Shape Keys
    shapeList = componentSel.keys()
    for shape in shapeList:
        
        # Get Shape Component Indices
        indexList = componentSel[shape]
        
        # Check Transform
        if cmds.objectType(shape) == 'transform':
            shape = cmds.listRelatives(shape, ni=True, pa=True)[0]
        
        # Check Mesh or Curve
        if (cmds.objectType(shape) == 'mesh') or (cmds.objectType(shape) == 'nurbsCurve'):
            singleIndexList[shape] = indexList
            
        # Check Surface
        elif cmds.objectType(shape) == 'nurbsSurface':
            # Get nurbsSurface function set
            surfList = om.MSelectionList()
            surfObj = om.MObject()
            om.MGlobal.getSelectionListByName(shape, surfList)
            surfList.getDependNode(0, surfObj)
            surfFn = om.MFnNurbsSurface(surfObj)
            # CV count in V direction
            numV = surfFn.numCVsInV()
            # Check for periodic surface
            if surfFn.formInV() == surfFn.kPeriodic: numV -= surfFn.degreeV()
            singleIndexList[shape] = [(i[0]*numV)+i[1] for i in indexList]
            
        # Check Lattice
        elif (cmds.objectType(shape) == 'lattice'):
            sDiv = cmds.getAttr(shape+'.sDivisions')
            tDiv = cmds.getAttr(shape+'.tDivisions')
            singleIndexList[shape] = [i[0]+(i[1]*sDiv)+(i[2]*sDiv*tDiv) for i in indexList]
    
    # Return Result
    return singleIndexList

