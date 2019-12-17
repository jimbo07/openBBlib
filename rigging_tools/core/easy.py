'''
Created on 1 Aug 2018

@author: lasse-r
'''
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import math
import types
from ooutdmaya.common.util import names


def getChain(start, end, endAfter=100):
    """ Creates a list that'll store the hierarchy going from start -> end
    
    :param start str: start node
    :param end str: end node
    :param endAfter int: stop the while loop after x iterations
    :return: List of items in hierarchy
    :rtype: list
    :raises ValueError: If endAfter limit is exceeded or end isn't in the hierarchy of start
    
    """
    # Check if in hierarchy
    fullhier = cmds.listRelatives(start, ad=True)
    
    if not fullhier: 
        cmds.warning("No chain could be extracted with the following start {0} and end {1}".format(start, end))
        return
    
    if not end in fullhier:
        raise ValueError("{0} does not exist in the hierarchy of {1}".format(end, start))
    
    # Prep while loop variables
    hier = [] 
    finished = 0
    curItem = end
    safety = 0
    
    # Create the hiearchy
    while finished == 0:
        if safety >= endAfter:
            raise ValueError("Did {0} iteration(s) without finding {1}, exiting...".format(endAfter, start))
        hier.append(curItem)
        curItem = cmds.listRelatives(curItem, p=1)[0]
        if curItem == start:
            hier.append(curItem)
            finished = 1
        safety += 1
            
    # Reverse list
    return hier[::-1]


def driveChain(driven, driversA, driversB, channel="rotate"):
    """ Create a setup where the transforms in the lists driversA and driversB drives the transforms in driven
    
    :param driven list: The list of transforms to be driven
    :param driversA list: The first list of driving transforms
    :param driversB list: The second list of driving transforms
    :param channel str: Which channel to drive
    :return: list of choice nodes to select what currently drives
    :rtype: list
    
    """    
    chcList = []
    for i, jnt in enumerate(driven):
        if i > (len(driven) - 1): break
        chc = cmds.createNode('choice', n=names.addModifier(jnt, 'choice', addSuffix=channel))
        if driversA: cmds.connectAttr("{0}.{1}".format(driversA[i], channel), "{0}.{1}".format(chc, "input[0]"), f=1)
        if driversB: cmds.connectAttr("{0}.{1}".format(driversB[i], channel), "{0}.{1}".format(chc, "input[1]"), f=1)
        cmds.connectAttr("{0}.{1}".format(chc, "output"), "{0}.{1}".format(jnt, channel), f=1)
        chcList.append(chc)
        
    return chcList


def createCompoundAttr(target, name, typ):
    """ Adds a compound attr of specified type to specified target
    :param target str: target object to add attribute to
    :param name str: name of attribute to be created
    :param type str: type of compound attr, ie. float3
    :return: newly created attribute
    :rtype: str
    """
    for i in range(1):
        cmds.addAttr(target, ln=name, dt=typ+"3", h=False, k=False)
    for n in ['X', 'Y', 'Z']:
        cmds.addAttr(ln=name+n, at=typ, parent="{0}.{1}".format(target, name))
    
    return "{0}.{1}".format(target, name)


def getParent(node):
    """ Returns the parent of the node specified
    
    :param node str: Node for which to return parent
    :return: parent of node (if exists)
    :rtype: list
    """
    parent = cmds.listRelatives(node, p=1)
    if not parent:
        parent = []
        cmds.warning("{0} has no parent, returned empty list".format(node))
    
    return parent
    

def getChildren(node):
    """ Returns the child(ren) of the node specified
    
    :param node str: Node for which to return child(ren)
    :return: child(ren) of node (if exists)
    :rtype: list
    """
    children = cmds.listRelatives(node, c=1)
    if not children:
        children = []
        cmds.warning("{0} has no children, returned empty list".format(node))
    
    return children


def getPosition(point):
    ''' Return the position of any point or transform
    :param point str, list, tuple: Point to return position for
    '''
    # Initialize point value
    pos = []
    
    # Determine point type
    if (type(point) == list) or (type(point) == tuple):
        if len(point) < 3:
            raise Exception('Invalid point value supplied! Not enough list/tuple elements!')
        pos = point[0:3]
    elif (type(point) == str) or (type(point) == unicode):
        
        # Check Transform
        mObject = getMObject(point)
        if mObject.hasFn(om.MFn.kTransform):
            try: pos = cmds.xform(point,q=True,ws=True,rp=True)
            except: pass
        
        # pointPosition query
        if not pos:
            try: pos = cmds.pointPosition(point)
            except: pass
        
        # xform - rotate pivot query
        if not pos:
            try: pos = cmds.xform(point,q=True,ws=True,rp=True)
            except: pass
        
        # Unknown type
        if not pos:
            raise Exception('Invalid point value supplied! Unable to determine type of point "'+str(point)+'"!')
    else:
        raise Exception('Invalid point value supplied! Invalid argument type!')
        
    # Return result
    return pos


def trySetAttr(attr, value, loud=0):
    """ Tries setting an attribute, and if it fails it doesn't stop script execution
    
    :param attr str: attribute to set, ie. "test_grp.visibility"
    :param value int: value to set the attribute to
    :param loud bool: if 1, creates a warning if attribute wasn't set
    :return: 1 or 0 depending on whether or not the value was set
    :rtype: bool
    """
    success = 1
    try:
        cmds.setAttr(attr, value)
    except:
        if loud: cmds.warning("Failed to set attribute {0} to {1}".format(attr, value))
        success = 0
    
    return success


def connectAttr(source, target, attr, typ, rename = ""):
    """
    :param source str: node name from where the attribute currently is
    :param target str: node name for where the driving attribute should be created and connected
    :param attr str: the attribute name
    :param typ str: the type of attribute to connect. Only works with bool and float 
    """
    attrType = typ
    if not attrType:
        attrType = "float"
        
    if cmds.attributeQuery(attr, node=source, ex=1):
        if cmds.objExists(target):
            if rename:
                cmds.addAttr(target, at=typ, ln=rename, k=True)
                cmds.connectAttr("{0}.{1}".format(target, rename), "{0}.{1}".format(source, attr), f=True)
            elif cmds.attributeQuery(attr, node=target, ex=1):
                cmds.connectAttr("{0}.{1}".format(target, attr), "{0}.{1}".format(source, attr), f=True)
            else:
                cmds.addAttr(target, at=typ, ln=attr, k=True)
                cmds.connectAttr("{0}.{1}".format(target, attr), "{0}.{1}".format(source, attr), f=True)
        else:
            cmds.warning("The target node '{0}' does not exist!".format(target))
    else:
        cmds.warning("The target attribute destination '{0}.{1}' does not exist!".format(source, attr))
    
    return 


def createAttrSeparator(node, attr):
    """ 
    :param node str: node to create attribute separator on
    :param attr str: separator attribute name
    """
    if cmds.objExists(node):
        if not cmds.attributeQuery(attr, node=node, ex=1):
            cmds.addAttr(node, ln=attr, niceName=attr, at='enum', en='________', k=True)
            cmds.setAttr('{0}.{1}'.format(node, attr), lock=True)
            

def snapTo(source, target):
    """ 
    :param source str: source to snap to
    :param target str: target that will be snapped
    """
    cmds.delete(cmds.pointConstraint(source, target, mo=0))
    

def alignTo(source, target):
    """
    :param source str: source to align to
    :param target str: target that will be aligned
    """
    cmds.delete(cmds.orientConstraint(source, target, mo=0))

    
def scaleTo(source, target):
    """
    :param source str: source to match scale of
    :param target str: target that will be scaled
    """
    cmds.delete(cmds.scaleConstraint(source, target, mo=0))


def snapAlignTo(source, target):
    """
    :param source str: source to snap and align to
    :param target str: target that will be snapped and aligned
    """
    cmds.delete(cmds.parentConstraint(source, target, mo=0))
    
    
def snapAlignScaleTo(source, target):
    """
    :param source str: source to snap, align and scale to
    :param target str: target that will be snapped, aligned and scaled
    """
    snapAlignTo(source, target)
    scaleTo(source, target)


def sliceIndex(x):
    """ Preps a sliceindex omitting all alphas
    :param x str: string to slice
    """
    i = 0
    for c in x:
        if c.isalpha():
            i = i + 1
            return i
        i = i + 1


def upperFirst(x):
    """ Capitalizes first letter in any given string while keeping camelcasing intact
    :param x str: string to capitalize 
    """
    i = sliceIndex(x)
    return x[:i].upper() + x[i:]


def getAlphaFromNumber(number):
    """ Returns a alpha value corresponding to the number supplied, ie. 0 = a, 10 = f.
    :param number int: number to convert to alpha
    """
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    valueDict = {}
    for i, alphas in enumerate(sorted([''.join((x, y)) for x in alpha for y in [''] + [z for z in alpha]], key=len)):
        valueDict[alphas] = i + i

    for key, value in valueDict.items():
        if number == value:
            return key


def findClosest(source, targetList):
    """ Returns the target in targetList which is closest to the source (looks at the rotate pivot pos)
    :param source str: source transform
    :param targetList list: list of targets to test
    :return: target closest to source
    :rtype: str
    """
    closestDistance = 10e10
    closestTarget = None
    p = cmds.xform(source, q=True, rp=True, ws=True, a=True)
    source_mPoint = om.MPoint(p[0], p[1], p[2])
    source_mFloatPoint = om.MFloatPoint(source_mPoint.x, source_mPoint.y, source_mPoint.z)
    
    for target in targetList:
        p = cmds.xform(target, q=True, rp=True, ws=True, a=True)
        target_mPoint = om.MPoint(p[0], p[1], p[2])
        target_mFloatPoint = om.MFloatPoint(target_mPoint.x, target_mPoint.y, target_mPoint.z)
        
        d = target_mFloatPoint.distanceTo(source_mFloatPoint)
        if d < closestDistance: 
            closestDistance = d
            closestTarget = target
    
    return closestTarget


def depthDict(d):
    """Returns the depth of a nested dictionary
    
    Note:
        This is a recursive function, use with care
    
    Args:
        d (dict): Returns the depth of the dictionary specified as d
        
    """
    if isinstance(d, dict):
        return 1 + (max(map(depthDict, d.values())) if d else 0)
    return 0
    

def printDict(d, lvl=0):
    """Prints every key and value in supplied dictionary
    
    Args:
        d (dict): Prints this dictionary
        lvl (int): Defines the current level of depth, used for indentation
        
    """
    for k, v in d.iteritems():
        print '{0}{1}'.format(lvl * '\t', k)
        if type(v) == dict:
            printDict(v, lvl + 1)
        elif type(v) == list:
            for i in v:
                print "{0}{1}".format((lvl * '\t') + '\t', i)


def compareDict(d1, d2, ns=0, d1ns=None, d2ns=None):
    """Compare dictionary A (d1) with dictionary B (d2)
    
    Args:
        d1 (dict): First dictionary
        d2 (dict): Second dictionary
        ns (bool): Account for namespaces
        d1ns (str, optional): Only replace this namespace in dictionary 1
        d2ns (str, optional): Only replace this namespace in dictionary 2
    
    Returns:
        added (set): These keys were not present in d1, but was in d2
        removed (set): These keys were present in d1, but not in d2
        modified (set): These keys were present in both, but the values were different
        same (set): These keys and their values are the same in both dictionaries
        
    """
    if ns:
        # Finds and replaces all keys that contains namespaces
        if d1ns: d1 = {x.replace(d1ns, ""): d1[x] for x in d1.keys()}
        else: d1 = {x.split(":")[-1]: d1[x] for x in d1.keys()}
        if d2ns: d2 = {x.replace(d2ns, ""): d2[x] for x in d2.keys()}
        else: d2 = {x.split(":")[-1]: d2[x] for x in d2.keys()}
    
    d1Keys = set(d1.keys())
    d2Keys = set(d2.keys())

    intersectKeys = d1Keys.intersection(d2Keys)
    added = d1Keys - d2Keys
    removed = d2Keys - d1Keys
    modified = {o : (d1[o], d2[o]) for o in intersectKeys if d1[o] != d2[o]}
    same = set(o for o in intersectKeys if d1[o] == d2[o])
    return added, removed, modified, same


def mergeDict(x, y):
    """Combines dictioniary x and y
    
    Args:
        x (dict): Dictionary X
        y (dict): Dictionary Y
        
    Return:
        z (dict): Updated dictionary
    """
    z = x.copy()
    z.update(y)
    return z


def removeKeyDict(k, d):
    """Removes key (k) from dictionary (d) if key exists in dictionary
    
    Args:
        k (str): Key to look for
        d (dict): Dictionary to look in
        
    Return:
        x (dict): New dictionary with key removed
        d (dict): Old dictionary, untouched
        
    """
    x = d.copy()
    # if second arg is not given, this will return KeyError if the key isn't found)
    x.pop(k, None)
    
    return x, d


def removeDuplicates(seq):
    ''' Remove list duplicates and maintain original order
    :param seq list: The list to remove duplicates for
    :return: list without dupes
    :rtype: list
    '''
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]


def dict_orderedKeyListFromValues(d):
    ''' Return a list of keys from dict, ordered based on their values
    :param d dict: The dictionary to construct list from
    :return: Ordered dictionary based of values
    :rtype: dict
    '''
    return [ i[0] for i in sorted(d.items(), key=lambda (k, v): v) ]

    
def dict_orderedValueListFromKeys(d):
    ''' Return a list of dictionary values, ordered based on their keys
    :param d dict: The dictionary to construct list from
    :return: Ordered dictionary based of keys
    :rtype: dict
    '''
    return [ d[key] for key in sorted(d.keys()) ]


def flattenList(listToFlatten):
    ''' Return a flattened version of the input list.
    :param listToFlatten list: The list to flatten
    :return: flattened list
    :rtype: list
    '''
    elems = []
    for i in listToFlatten:
        if isinstance(i,types.ListType): elems.extend(i)
        else: elems.append(i)
    return elems


def getAffectedJoints(ikh):
    ''' Get a list of joints affected by a specified ikHandle
    :param ikh str: IK Handle to query affected joints for
    '''
    # Check ikHandle
    if not cmds.objExists(ikh): raise Exception('IK handle {0} does not exist!'.format(ikh))
    if cmds.objectType(ikh) != 'ikHandle': raise Exception('Object {0} is not a valid ikHandle!'.format(ikh))
    
    # Get startJoint
    startJoint = cmds.listConnections(ikh+'.startJoint',s=True,d=False)[0]
    # Get endEffector
    endEffector = cmds.listConnections(ikh+'.endEffector',s=True,d=False)[0]
    endJoint = cmds.listConnections(endEffector+'.translateX',s=True,d=False)[0]
    
    # Get list of joints affected by ikHandle
    ikJoints = [endJoint]
    while ikJoints[-1] != startJoint:
        ikJoints.append(cmds.listRelatives(ikJoints[-1],p=True)[0])
    # Reverse joint list
    ikJoints.reverse()
    
    # Return ik joints list
    return ikJoints


# ====================================================================== # 
# Misc functionality 
# ====================================================================== #
# Data Object List
dataList = []

# Global SkinClusterData object
GlobalSkinClusterData = None

# Global ConstraintData object
GlobalConstraintData = None

# Global copy/paste skin weights command string
copyPasteWeightCmd = ''

def importFolderBrowser(textField): # ,caption='Import',startingDirectory=None):
    ''' Set the input directory from file browser selection
    '''
    mel.eval('global proc importGetFolder(string $textField,string $path,string $type){ textFieldButtonGrp -e -text $path $textField; deleteUI projectViewerWindow; }')
    mel.eval('fileBrowser "importGetFolder {0}" Import "" 4'.format(textField))
        

def exportFolderBrowser(textField):
    ''' Set the output directory from file browser selection
    '''
    mel.eval('global proc exportGetFolder(string $textField,string $path,string $type){ textFieldButtonGrp -e -text $path $textField; /*deleteUI projectViewerWindow;*/ }')
    mel.eval('fileBrowser "exportGetFolder {0}" Export "" 4'.format(textField))
    

# String utilties
def stripSuffix(name, delineator='_'):
    ''' Return the portion of name minus the last element separated by the name delineator.
        Useful for determining a name prefix from an existing object name.
    :param name str: String name to strip the suffix from
    :param delineator str: String delineator to split the string name with. If default will inherit the class delineator string.
    :return: Resulting string
    :rtype: str
    '''
    # Check for Delineator in Name
    if not name.count(delineator): return name
    # Determine Suffix
    suffix = name.split(delineator)[-1]
    # Remove Suffix
    result = name.replace(delineator+suffix,'')
    # Return Result
    return result

        
def stringIndex(index, padding=2):
    ''' Return the string equivalent for the specified iteger index.
    :param index int: The index to get the string equivalent for
    :param padding int: The number of characters for the index string
    :return: Return the string equivalent for the specified iteger index.
    :rtype: str
    '''
    # Convert to String
    strInd = str(index)
    # Prepend Padding
    for i in range(padding-len(strInd)): strInd = '0'+strInd
    # Return Result
    return strInd

    
def alphaIndex(index,upper=True):
    ''' Return the alpha string equivalent for the specified iteger index.
    :param index int: The index to get the alpha string equivalent for
    :param upper bool: Return the result in upper case form
    :return: The alpha string equivalent for specified int index
    :rtype: str
    '''
    # Define Alpha List
    alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        
    # Build Alpha Index
    alphaInd = alpha[index % 26]
    depth = index / 26.0
    while int(math.floor(depth)):
        alphaInd = alpha[int(depth % 26)-1] + alphaInd
        depth = depth / 26.0
    
    # Check Case
    if upper: alphaInd = alphaInd.upper()
    
    # Return result
    return alphaInd


# OpenMaya integration
def getMDagPath(obj):
    ''' Return an MDagPath for the input scene object
    :param obj str: Object to get MDagPath for
    :return: MDagPath of object
    :rtype: str
    '''
    # Check input object
    if not cmds.objExists(obj):
        raise Exception('Object {0} does not exist!'.format(obj))
    
    # Get selection list
    selectionList = om.MSelectionList()
    om.MGlobal.getSelectionListByName(obj,selectionList)
    mDagPath = om.MDagPath()
    selectionList.getDagPath(0,mDagPath)
    
    # Return result
    return mDagPath


def getMObject(obj):
    ''' Return an MObject for the input scene object
    :param obj str: Object to get MObject for
    :return: MObject of object
    :rtype: str
    '''
    # Check input object
    if not cmds.objExists(obj):
        raise Exception('Object {0} does not exist!'.format(obj))
    
    # Get selection list
    selectionList = om.MSelectionList()
    om.MGlobal.getSelectionListByName(obj,selectionList)
    mObject = om.MObject()
    selectionList.getDependNode(0,mObject)
    
    # Return result
    return mObject


def getShapes(transform, returnNonIntermediate=True, returnIntermediate=True):
    ''' Return a list of shapes under a specified transform
    :param transform str: Transform to query
    :param returnNonIntermediate bool: Return non intermediate shapes.
    :param returnIntermediate bool: Return intermediate shapes.
    :return: list of shapes for specified transform
    :rtype: list
    '''
    # Initialize arrays
    shapeList = []
    
    # Check for shape input
    transformObj = getMObject(transform)
    if not transformObj.hasFn(om.MFn.kTransform):
        transform = cmds.listRelatives(transform, p=True, pa=True)[0]
    
    # Get shape lists
    allShapeList = cmds.listRelatives(transform, s=True, pa=True)
    if not allShapeList: return []
    for shape in allShapeList:
        intermediate = bool(cmds.getAttr("{0}.intermediateObject".format(shape)))
        if intermediate and returnIntermediate: shapeList.append(shape)
        if not intermediate and returnNonIntermediate: shapeList.append(shape)
        
    # Return result
    return shapeList


# ====================================================================== # 
# COMPONENENT
# ====================================================================== #
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
        obj = getShapes(obj, True, False)[0]
    
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
    mObj = getMObject(geometry)
    if mObj.hasFn(om.MFn.kTransform):
        geometry = getShapes(geometry,True,False)
        if geometry: geometry = geometry[0]
        else: raise Exception('Object {0} is not a valid geometry object!'.format(geometry))
    
    # Check type
    mObj = getMObject(geometry)
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


# ====================================================================== # 
# DEFORMERS
# ====================================================================== #
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
    deformerObj = getMObject(deformer)
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
    deformerObj = getMObject(deformer)
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
    deformerSetObj = getMObject(deformerSet)
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
        try: geometry = cmds.listRelatives(geo, s=True, ni=True, pa=True)[0]
        except: raise Exception('Object {0} is not a valid geometry!'.format(geo))
        
    geomObj = getMObject(geo)
    
    # Get geometry index
    deformerObj = getMObject(deformer)
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
    deformerObj = getMObject(deformer)
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
    geoObj = getMObject(geometry)
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


# ====================================================================== # 
# MESH
# ====================================================================== #
def isMesh(mesh):
    ''' Check if the specified object is a polygon mesh or transform parent of a mesh
    :param mesh str: Object to query
    :return: True if mesh
    :rtype: bool
    '''
    # Check Object Exists
    if not cmds.objExists(mesh): return False
    
    # Check Shape
    if 'transform' in cmds.nodeType(mesh,i=True):
        meshShape = cmds.ls(cmds.listRelatives(mesh, s=True, ni=True, pa=True) or [],type='mesh')
        if not meshShape: return False
        mesh = meshShape[0]
    
    # Check Mesh
    if cmds.objectType(mesh) != 'mesh': return False
    
    # Return Result
    return True


def isOpen(mesh):
    ''' Check if mesh is a closed surface or has boundary components
    :param mesh str: Mesh to check for boundary conditions
    :return: True or False depending
    :rtype: bool
    '''
    # Check Mesh
    if not isMesh(mesh):
        raise Exception('Object {0} is not a valid mesh!!'.format(mesh))
    
    # Get User Selection
    sel = cmds.ls(sl=1)
    
    # Select Mesh
    cmds.select(mesh)
    cmds.polySelectConstraint(mode=3, type=1, where=1)
    boundarySel = cmds.ls(sl=1,fl=1)
    
    # Restore User Selection
    if sel: cmds.select(sel)
    
    # Return Result
    return bool(boundarySel)

    
def getMeshFn(mesh):
    ''' Create an MFnMesh class object from the specified polygon mesh
    :param mesh str: Mesh to create function class for
    :return: MFnMesh for specified poly mesh
    :rtype: class object
    '''
    # Checks
    if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
    
    # Get shape
    if cmds.objectType(mesh) == 'transform':
        mesh = cmds.listRelatives(mesh,s=True,ni=True,pa=True)[0]
        
    # Get MFnMesh
    meshPath = getMDagPath(mesh)
    meshFn = om.MFnMesh(meshPath)
    
    # Return result
    return meshFn

