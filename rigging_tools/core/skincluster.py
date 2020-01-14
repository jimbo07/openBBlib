"""
# Example
from ooutdmaya.rigging.core.util.IO import skinCluster
reload(skinCluster)

# define
ns1 = 'furVolume_'
skc = '{0}:skc_neckPly'.format(ns1)
weightFilePath = '/jobs/tsg/assets/prop/test_asset/3d/rig/work/maya/jarl-m/scenes/rig/weights/skc.001.xml'
    
# export weight file
exportPath = skinCluster.write(skc, weightFilePath)

# import weight file
search = 'tmp_:'
replace = ''
skc = 'skinCluster1'
skinCluster.read(skc, weightFilePath, search=search, replace=replace)
"""

from xml.dom.minidom import parse, Node
import os, shutil
from maya import cmds,  mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
from ooutdmaya.rigging.core.util import easy
from ooutdmaya.common.util import names



def deformerWeightsExport(skc, fileName='test.xml',
    baseDir=cmds.workspace(expandName='data'),
    weightTolerance=0.00001, info=False):
    """
    """
    # Define / Query
    filePath = os.path.join(baseDir, fileName)
    
    # Generate initial deformer weights file
    cmds.deformerWeights(fileName, path=baseDir, export=1, deformer=skc, method='index', weightTolerance=weightTolerance)
    
    # Build custom higher floating point dataset
    
    # instantiate the xml object
    xmltree = parse(filePath)
    deformerWeight = xmltree.getElementsByTagName('deformerWeight')[0]

    # remove/flush existing weights entries
    meshShape = ''
    for node1 in deformerWeight.getElementsByTagName('weights'):
        meshShape = node1.getAttribute('shape')
        deformerWeight.removeChild(node1)
    vtxNum = cmds.polyEvaluate(meshShape, vertex=1)

    # replace with more exact weights entries
    infList = cmds.skinCluster(skc, q=1, inf=1)
    aDict = {}
    valDict = {}
    for vtx in xrange(0, vtxNum):
        attrPath = '{0}.vtx[{1}]'.format(meshShape, vtx)
        valDict[vtx] = cmds.skinPercent(skc, attrPath, q=1, value=1)
    for i, inf in enumerate(infList):
        # <weights deformer="tmp_:skinCluster1" source="tmp_:joint2" shape="tmp_:pSphereShape1" layer="0" defaultValue="0.000" size="382" max="381">
        weightsNode = xmltree.createElement('weights')
        weightsNode.setAttribute('deformer', skc)
        weightsNode.setAttribute('source', inf)
        weightsNode.setAttribute('shape', meshShape)
        weightsNode.setAttribute('layer', str(i))
        weightsNode.setAttribute('defaultValue', "0.000")
        weightsNode.setAttribute('size', str(vtxNum))
        weightsNode.setAttribute('max', str(vtxNum - 1))
        deformerWeight.appendChild(weightsNode)
        for vtx in xrange(0, vtxNum):
            # <point index="0" value="1.000"/>
            attrPath = '{0}.vtx[{1}]'.format(meshShape, vtx)
            # valList = cmds.skinPercent(skc, attrPath, q=1, value=1)
            valList = valDict[vtx]
            if valList[i] < weightTolerance:
                continue
            pointNode = xmltree.createElement('point')
            pointNode.setAttribute('index', str(vtx))
            pointNode.setAttribute('value', str(valList[i]))
            weightsNode.appendChild(pointNode)
    
    if info:
        aDict = {}
        for node1 in deformerWeight.getElementsByTagName('weights'):
            aDict['deformer'] = node1.getAttribute('deformer')
            aDict['source'] = node1.getAttribute('source')
            aDict['shape'] = node1.getAttribute('shape')
            aDict['layer'] = node1.getAttribute('layer')
            aDict['defaultValue'] = node1.getAttribute('defaultValue')
            aDict['size'] = node1.getAttribute('size')
            aDict['max'] = node1.getAttribute('max')
            if info: print('<weights deformer={0} source={1} shape={2} layer={3} defaultValue={4} size={5} max={6}>'.format(
                aDict['deformer'], aDict['source'], aDict['shape'], aDict['layer'], aDict['defaultValue'], aDict['size'], aDict['max'])
            )
            for child in node1.getElementsByTagName('point'):
                aDict['index'] = child.getAttribute('index')
                aDict['value'] = child.getAttribute('value')
                if info: print('{0}.vtx[{1}] {2} {3}'.format(aDict['shape'], aDict['index'], aDict['source'], aDict['value']))
    
    fileObj = open(filePath, 'w')
    # help(xmltree.writexml)
    xmltree.writexml(fileObj, indent='\n  ', addindent='  ')
    fileObj.close()
    if info:
        print xmltree.toprettyxml()
        
    return filePath


def write(skc, filePath, weightTolerance=0.00001, info=False):
    """
    # define
    ns1 = 'tmp_'
    skc = '{0}:skinCluster1'.format(ns1)
    weightFilePath = '/path/to/xml/file.xml'
    rigFilePath = '/path/to/rig/file.mb'
    
    # import rig
    cmds.file(new=1, f=1)
    cmds.file(rigFilePath, i=1, ns=ns1)
    
    # export weight file
    exportPath = write(skc, weightFilePath)
    """
    # Construct a temporary file path
    fileName = '{0}_{1}'.format(__name__, os.path.basename(filePath))
    # Export the weights
    tmpFile = deformerWeightsExport(skc, fileName=fileName,
    baseDir=cmds.workspace(expandName=''),
    weightTolerance=weightTolerance, info=info)
    # Place the file in the right spot
    shutil.move(tmpFile, filePath)
    # return the file
    return filePath


def read(skc, filePath, search='', replace='', weightTolerance=0.00001, positionTolerance=10, info=False):
    """
    # define
    ns1 = 'tmp_'
    ns2 = 'tmp2_'
    skc = '{0}:skinCluster1'.format(ns2)
    weightFilePath = '/path/to/xml/file.xml'
    rigFilePath = '/path/to/rig/file.mb'
    
    # import rig
    cmds.file(new=1, f=1)
    cmds.file(rigFilePath, i=1, ns=ns2)
    
    # import weights (make sure you add influences first)
    read(skc, weightFilePath, search=ns1, replace=ns2)
    """
    baseDir = cmds.workspace(expandName='')
    rawFileName = '{0}_{1}Raw'.format(__name__, os.path.basename(filePath))
    resultFileName = '{0}_{1}Result'.format(__name__, os.path.basename(filePath))
    tmpRawFilePath = os.path.join(baseDir, rawFileName)
    tmpResultFilePath = os.path.join(baseDir, resultFileName)
    print('temp file path = {0}'.format(tmpRawFilePath))
    if tmpRawFilePath == filePath:
        resultFileName = '{0}_safetyTempFile_{1}'.format(__name__, os.path.basename(filePath))
        tmpResultFilePath = os.path.join(baseDir, resultFileName)
    shutil.copyfile(filePath, tmpResultFilePath)
    shutil.copyfile(filePath, tmpRawFilePath)
    
    # Match influences in the skin cluster file before import,
    # otherwise the deformer weights import doesn't work
    xmltree = parse(filePath)
    deformerWeight = xmltree.getElementsByTagName('deformerWeight')[0]
    infList = []
    # Query the current skc influences
    currInfs = cmds.skinCluster(skc, q=1, inf=1)
    # Query weight file influences, adding them to the skin cluster as we go
    for node1 in deformerWeight.getElementsByTagName('weights'):
        cmds.select(cl=1)
        inf = node1.getAttribute('source')
        inf = inf.replace(search, replace)
        infList.append(inf)
        print inf
        if inf in currInfs:
            continue
        print('adding influence {0}'.format(inf))
        cmds.skinCluster(skc, ai=inf, e=1)
    # Remove influences not in the weight file
    for currInf in currInfs:
        if currInf in infList:
            continue
        print('removing influence {0}'.format(currInf))
        cmds.skinCluster(skc, ri=currInf, e=1)
        
    # Query the destination mesh name
    destMeshName = cmds.listConnections('{0}.outputGeometry[0]'.format(skc), s=0, d=1, plugs=1)[0]
    destMeshName = destMeshName.split('.')[0]
    
    # Process the file for the destination mesh name
    xmltree = parse(tmpResultFilePath)
    for node1 in deformerWeight.getElementsByTagName('shape'):
        node1.setAttribute('name', destMeshName)
    for node1 in deformerWeight.getElementsByTagName('weights'):
        node1.setAttribute('shape', destMeshName)
    fileObj = open(tmpResultFilePath, 'w')
    xmltree.writexml(fileObj, indent='\n  ', addindent='  ')
    fileObj.close()
    shutil.copyfile(tmpResultFilePath, tmpRawFilePath)

    # Import
    if search != '' or replace != '':
        readfile = open(tmpRawFilePath, 'r')
        writefile = open(tmpResultFilePath, 'w')
        for line in readfile:
            writefile.write(line.replace(search, replace))
        writefile.close()
        readfile.close()
        cmds.deformerWeights(
            resultFileName, path=baseDir, im=1, deformer=skc,
            method='index', positionTolerance=10, weightTolerance=0.00000000001)
    else:
        cmds.deformerWeights(
            resultFileName, path=baseDir, im=1, deformer=skc,
            method='index', positionTolerance=10, weightTolerance=0.00000000001)
    os.remove(tmpRawFilePath)
    os.remove(tmpResultFilePath)


def getInfs(filePath):
    """
    """
    xmltree = parse(filePath)
    deformerWeight = xmltree.getElementsByTagName('deformerWeight')[0]
    infList = []
    # Query weight file influences, adding them to the skin cluster as we go
    for node1 in deformerWeight.getElementsByTagName('weights'):
        inf = node1.getAttribute('source')
        infList.append(inf)
    return infList
    
    
def isSkinCluster(skinCluster):
    '''Test if the input node is a valid skinCluster
    :param blendShape str: Name of blendShape to query
    :return: True if valid skinCluster, else False
    :rtype: bool
    '''
    # Check object exists
    if not cmds.objExists(skinCluster):
        print('SkinCluster {0} does not exists!'.format(skinCluster))
        return False
    # Check object is a valid skinCluster
    if cmds.objectType(skinCluster) != 'skinCluster':
        print('Object {0} is not a vaild skinCluster node!'.format(skinCluster))
        return False
    
    # Return result
    return True


def findRelatedSkinCluster(geometry):
    ''' Return the skinCluster attached to the specified geometry
    :param geometry str: Geometry object/transform to query
    :return: skinCluster attached to specified geo, or empty string if none exists
    :rtype: string
    '''
    # Check geometry
    if not cmds.objExists(geometry):
        raise Exception('Object {0} does not exist!'.format(geometry))
    # Check transform
    if cmds.objectType(geometry) == 'transform':
        try: geometry = cmds.listRelatives(geometry,s=True,ni=True,pa=True)[0]
        except: raise Exception('Object {0} has no deformable geometry!'.format(geometry))
    
    # Determine skinCluster
    skin = mel.eval('findRelatedSkinCluster "{0}"'.format(geometry))
    if not skin: 
        skin = cmds.ls(cmds.listHistory(geometry), type='skinCluster')
        if skin: skin = skin[0]
    if not skin: skin = ''
    
    # Return result
    return skin


def getSkinClusterFn(skinCluster):
    ''' Return an MFnSkinCluster function class object for the speficied skinCluster
    :param skinCluster str: SkinCluster to attach to function class
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Get skinCluster node
    skinClusterSel = om.MSelectionList()
    skinClusterObj = om.MObject()
    om.MGlobal.getSelectionListByName(skinCluster,skinClusterSel)
    skinClusterSel.getDependNode(0,skinClusterObj)
    
    # Initialize skinCluster function class
    skinClusterFn = oma.MFnSkinCluster(skinClusterObj)
    
    # Return function class
    return skinClusterFn


def getInfluenceIndex(skinCluster, influence):
    ''' Return the input index of an influence for a specified skinCluster
    :param skinCluster str: SkinCluster to query influence index from
    :param influence str: Influence to query index of
    :return: Input index of influence for specified skinCluster
    :rtype: str
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Check influence
    if not cmds.objExists(influence):
        raise Exception('Influence object {0} does not exist!'.format(influence))
    
    # Get skinCluster node
    skinClusterFn = getSkinClusterFn(skinCluster)
    
    # Get influence object
    influencePath = easy.getMDagPath(influence)
    
    # Get influence index
    return skinClusterFn.indexForInfluenceObject(influencePath)


def getInfluenceAtIndex(skinCluster, influenceIndex):
    ''' Return the skinCluster influence at the specified index.
    :param skinCluster str: SkinCluster to query influence from
    :param influenceIndex int: Influence index to query
    :return: skinCluster influence at specified index
    :rtype: str
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Get Influence at Index
    infConn = cmds.listConnections("{0}.matrix[{1}]".format(skinCluster, str(influenceIndex)), s=True, d=False)
    
    # Check Connection
    if not infConn: raise Exception('No influence at specified index!')
    
    # Return Result
    return infConn[0]


def getInfluencePhysicalIndex(skinCluster,influence):
    '''
    Return the physical (non-sparce) index of an influence for a specified skinCluster
    :param skinCluster str: SkinCluster to query influence index from
    :param influence str: Influence to query index of
    :return: physical (non-sparce) index of influence for specified skinCluster
    :rtype: str
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Check influence
    if not cmds.objExists(influence):
        raise Exception('Influence object {0} does not exist!'.format(influence))
    
    # Get skinCluster node
    skinClusterFn = getSkinClusterFn(skinCluster)
    
    # Get influence path list
    infPathArray = om.MDagPathArray()
    skinClusterFn.influenceObjects(infPathArray)
    infNameArray = [infPathArray[i].partialPathName() for i in range(infPathArray.length())]
    
    # Check influence
    if not influence in infNameArray:
        raise Exception('Unable to determine influence index for {0}!'.format(influence))
    infIndex = infNameArray.index(influence)
    
    # Retrun result
    return infIndex


def getInfluenceWeights(skinCluster,influence,componentList=[]):
    ''' Return the weights of an influence for a specified skinCluster
    :param skinCluster str: SkinCluster to query influence weights from
    :param influence str: Influence to query weights from
    :param componentList list: List of components to query weights for
    :return: returns list of weights of an influence for specified skinCluster
    :rtype: list
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Check influence
    if not cmds.objExists(influence):
        raise Exception('Influence object {0} does not exist!'.format(influence))
    
    # Get geometry
    affectedGeo = easy.getAffectedGeometry(skinCluster).keys()[0]
    
    # Check component list
    if not componentList:
        componentList = easy.getComponentStrList(affectedGeo)
    componentSel = easy.getSelectionElement(componentList,0)
    
    # Get skinCluster Fn
    skinFn = getSkinClusterFn(skinCluster)
    
    # Get Influence Index
    influenceIndex = getInfluencePhysicalIndex(skinCluster,influence)
    
    # Get weight values
    weightList = om.MDoubleArray()
    skinFn.getWeights(componentSel[0],componentSel[1],influenceIndex,weightList)
    
    # Return weight array
    return list(weightList)


def getInfluenceWeightsAll(skinCluster,componentList=[]):
    ''' Return the weights of all influence for a specified skinCluster
    :param skinCluster str: SkinCluster to query influence weights from
    :param componentList list: List of components to query weights for
    :return: weights of all influences for specified skinCluster
    :rtype: list
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))

    # Get Geometry
    affectedGeo = easy.getAffectedGeometry(skinCluster).keys()[0]
    
    # Check component list
    if not componentList: componentList = easy.getComponentStrList(affectedGeo)
    componentSel = easy.getSelectionElement(componentList,0)

    # Get skinClusterFn
    skinFn = getSkinClusterFn(skinCluster)

    # Get weight values
    weightList = om.MDoubleArray()
    infCountUtil = om.MScriptUtil(0)
    infCountPtr = infCountUtil.asUintPtr()
    skinFn.getWeights(componentSel[0],componentSel[1],weightList,infCountPtr)
    infCount = om.MScriptUtil(infCountPtr).asUint()
    
    # Break List Per Influence
    wtList = list(weightList)
    infWtList = [wtList[i::infCount] for i in xrange(infCount)]
    
    # Return Result
    return infWtList


def setInfluenceWeights(skinCluster, influence, weightList, normalize=True, componentList=[]):
    ''' Set the weights of an influence for a specified skinCluster using an input weight list
    :param skinCluster str: SkinCluster to set influence weights for
    :param influence str: Influence to set weights for
    :param weightList list: Influence weight list to apply.
    :param normalize bool: Normalize weights as they are applied
    :param componentList list: List of components to set weights for
    :return: list of old weights
    :rtype: list
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Check influence
    if not cmds.objExists(influence):
        raise Exception('Influence object {0} does not exist!'.format(influence))
    
    # Get geometry
    affectedGeo = easy.getAffectedGeometry(skinCluster).keys()[0]
    
    # Get skinCluster Fn
    skinFn = getSkinClusterFn(skinCluster)
    
    # Get Influence Index
    influenceIndex = getInfluencePhysicalIndex(skinCluster,influence)
    
    # Check component list
    if not componentList:
        componentList = easy.getComponentStrList(affectedGeo)
    componentSel = easy.getSelectionElement(componentList,0)
    
    # Encode argument arrays
    infIndexArray = om.MIntArray()
    infIndexArray.append(influenceIndex)
    
    wtArray = om.MDoubleArray()
    oldWtArray = om.MDoubleArray()
    [wtArray.append(i) for i in weightList]
    
    # Set skinCluster weight values
    skinFn.setWeights(componentSel[0], componentSel[1], infIndexArray, wtArray, normalize, oldWtArray)
    
    # Return result
    return list(oldWtArray)


def setInfluenceWeightsAll(skinCluster, weightList, normalize=False, componentList=[]):
    '''
    :param skinCluster str: SkinCluster to set influence weights for
    :param weightList list: Influence weight list to apply.
    :param normalize bool: Normalize weights as they are applied
    :param componentList list: List of components to set weights for
    :return: list of old weights
    :rtype: list
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Get SkinCluster Influence List
    influenceList = cmds.skinCluster(skinCluster,q=True,inf=True)
    infIndexArray = om.MIntArray()
    [infIndexArray.append(getInfluencePhysicalIndex(skinCluster,inf)) for inf in influenceList]
    infDict = {}
    for inf in influenceList: infDict[inf] = getInfluencePhysicalIndex(skinCluster,inf)
    
    # Get SkinCluster Geometry
    skinGeo = easy.getAffectedGeometry(skinCluster).keys()[0]
    if not cmds.objExists(skinGeo):
        raise Exception('SkinCluster geometry {0} does not exist!'.format(skinGeo))
    
    # Check Component List
    if not componentList: componentList = easy.getComponentStrList(skinGeo)
    componentSel = easy.getSelectionElement(componentList,0)
    
    # Get Component Index List
    indexList =  om.MIntArray()
    componentFn = om.MFnSingleIndexedComponent(componentSel[1])
    componentFn.getElements(indexList)
    componentIndexList = list(indexList)
    
    # Check SkinCluster Weights List
    if len(weightList) != len(influenceList):
        raise Exception('Influence and weight list miss-match!')
    
    # Build Master Weight Array
    wtArray = om.MDoubleArray()
    oldWtArray = om.MDoubleArray()
    for c in componentIndexList:
        for inf in influenceList:
            wtArray.append(weightList[infDict[inf]][c])
    
    # Get skinCluster function set
    skinFn = getSkinClusterFn(skinCluster)
    
    # Set skinCluster weights
    skinFn.setWeights(componentSel[0], componentSel[1], infIndexArray, wtArray, normalize, oldWtArray)

    # Return result
    return list(oldWtArray)


def skinAs(src, dst, smooth=False):
    ''' Bind a destination mesh based on the influence list and weights of the skinCluster of a source mesh.
    :param src str: Source mesh that will be used to determine influence list and weights of destination mesh.
    :param dst str: Destination mesh to bind based on source mesh skinCluster.
    :param smooth bool: Smooth incoming skinCluster weights for destination mesh.
    :return: the resulting skinCluster
    :rtype: str
    '''
    # Check inputs
    if not cmds.objExists(src): raise Exception('Source object {0} does not exist!'.format(src))
    if not cmds.objExists(dst): raise Exception('Destination object {0} does not exist!'.format(dst))
    
    # Get source skinCluster
    srcSkin = findRelatedSkinCluster(src)
    
    # Check destination skinCluster
    dstSkin = findRelatedSkinCluster(dst)
    
    # Build destination skinCluster
    if not dstSkin:
        dstPrefix = dst.split(':')[-1]
        srcInfList = cmds.skinCluster(srcSkin, q=True, inf=True)
        dstSkin = cmds.skinCluster(srcInfList, dst, toSelectedBones=True, rui=False, n=names.nodeName('skinCluster', dstPrefix))[0]
    
    # Copy skin weights
    cmds.copySkinWeights(sourceSkin=str(srcSkin), 
                        destinationSkin=str(dstSkin),
                        surfaceAssociation='closestPoint',
                        influenceAssociation='name',
                        noMirror=True,
                        smooth=smooth)
    
    # Return result
    return dstSkin

def clearWeights(geometry):
    ''' Reset the skinCluster weight values (set to 0.0) for the specified objects/components
    :param geometry list: Geometry whose skinCluster weights will have its weights reset to 0.0
    '''
    # Check Geometry
    if not cmds.objExists(geometry):
        raise Exception('Geometry object {0} does not exist!'.format(geometry))
    
    # Get SkinCluster
    skinCluster = findRelatedSkinCluster(geometry)
    if not cmds.objExists(skinCluster):
        raise Exception('Geometry object {0} is not attached to a valid skinCluster!'.format(geometry))
    
    # =================
    # - Clear Weights -
    # =================
    
    # Get geometry component list
    componentList = easy.getComponentStrList(geometry)
    componentSel = easy.getSelectionElement(componentList,0)
    
    # Build influence index array
    infList = cmds.skinCluster(skinCluster,q=True,inf=True)
    infIndexArray = om.MIntArray()
    for inf in infList:
        infIndex = getInfluencePhysicalIndex(skinCluster,inf)
        infIndexArray.append(infIndex)
    
    # Build master weight array
    wtArray = om.MDoubleArray()
    oldWtArray = om.MDoubleArray()
    [wtArray.append(0.0) for i in range(len(componentList)*len(infList))]
    
    # Set skinCluster weights
    skinFn = getSkinClusterFn(skinCluster)
    skinFn.setWeights(componentSel[0], componentSel[1], infIndexArray, wtArray, False, oldWtArray)


def skinObjectList(objList, jntList):
    ''' Skin a list of objects to a list of influences
    :param objList list: List of geoemrty to create skinClusters for.
    :param jntList list: List of joints to add as skinCluster influences.
    :return: list of skinClusters
    :rtype: list
    '''
    # Check Geometry
    for obj in objList:
        if not cmds.objExists(obj):
            raise Exception('Object {0} does not exist!'.format(obj))
    
    # Check Joints
    for jnt in jntList:
        if not cmds.objExists(jnt):
            raise Exception('Joint {0} does not exist!'.format(jnt))
    
    
    # Initialize SkinCluster List
    skinClusterList = []
    
    for obj in objList:
        
        # Get Short Name
        objName = cmds.ls(obj,sn=True)[0].split(':')[-1]
        
        # Create SkinCluster
        skinCluster = cmds.skinCluster(jntList, obj, tsb=True, rui=False, n=names.nodeName('skinCluster', objName))[0]
        
        # Append to Return List
        skinClusterList.append(skinCluster)

    return skinClusterList


def lockInfluenceWeights(influence,lock=True,lockAttr=False):
    ''' Set the specified influence weight lock state.
    :param influence str: SkinCluster influence to lock weights for
    :param lock bool: The lock state to apply to the skinCluster influences
    :param lockAttr bool: Lock the "lockInfluenceWeights" attribute
    '''
    # Check SkinCluster
    if not cmds.objExists(influence):
        raise Exception('Influence {} does not exist!'.format(influence))
    
    # Check Lock Influence Weights Attr
    if not cmds.attributeQuery('liw', n=influence, ex=True):
        raise Exception('Influence ({0}) does not contain attribute "lockInfluenceWeights" ("liw")!'.format(influence))
        
    # Set Lock Influence Weights Attr
    try:
        cmds.setAttr(influence+'.liw',l=False)
        cmds.setAttr(influence+'.liw',lock)
        if lockAttr: cmds.setAttr(influence+'.liw',l=True)
    except: pass
    
    # Return Result
    return lock


def lockSkinClusterWeights(skinCluster,lock=True,lockAttr=False):
    ''' Set the influence weight lock state for all influences of the specified skinCluster.
    :param skinCluster str: SkinCluster to lock influence weights for
    :param lock bool: The lock state to apply to the skinCluster influences
    :param lockAttr bool: Lock the "lockInfluenceWeights" attribute
    '''
    # Verify skinCluster
    if not isSkinCluster(skinCluster):
        raise Exception('Invalid skinCluster {0} specified!'.format(skinCluster))
    
    # Get Influence List
    influenceList = cmds.skinCluster(skinCluster, q=True, inf=True) or []
    
    # For Each Influence
    for influence in influenceList:
        # Set Lock Influence Weights Attr
        lockInfluenceWeights(influence,lock=lock,lockAttr=lockAttr)
    
    # Return Result
    return influenceList


def clean(skinCluster,tolerance=0.005):
    ''' Clean SkinCluster. Prune weights below the specified threshold, and remove unused influences.
    :param skinCluster str: SkinCluster to clean.
    :param tolerance float: Prune all influence weights below this value.
    '''
    # Print Message
    print('Cleaning skinCluster: {0}'.format(skinCluster))
    
    # Get Affected Geometry
    geoShape = cmds.skinCluster(skinCluster, q=True, g=True)
    if not geoShape:
        raise Exception('Unable to determine deformed geometry from skinCluster {0}!'.format(skinCluster))
    
    geo = cmds.listRelatives(geoShape[0], p=True, pa=True)
    if not geo:
        raise Exception('Unable to determine geometry from deformed shape {0}!'.format(geoShape[0]))
    
    # Select Geometry
    cmds.select(geo[0])
    
    # Unlock Influence Weights
    lockSkinClusterWeights(skinCluster, lock=False, lockAttr=False)
    
    # Prune weights
    mel.eval('doPruneSkinClusterWeightsArgList 1 { "'+str(tolerance)+'" }')
    
    # Remove unused influences
    mel.eval('removeUnusedInfluences')
    
    # Lock Influence Weights
    lockSkinClusterWeights(skinCluster, lock=True, lockAttr=True)
    

def gui():
    """
    from ooutdmaya.rigging.core.util.IO import import skinCluster
    reload(skinCluster)
    skinCluster.gui()
    """
    if cmds.window("Skin_Cluster_IO_window", q=True, ex=True):
        cmds.deleteUI("Skin_Cluster_IO_window")
    window_name = cmds.window('Skin_Cluster_IO_window', title="Skin Cluster IO", iconName='Skin_Cluster_IO', widthHeight=(500, 300) )
    column = cmds.columnLayout(adjustableColumn=True)
    cmds.textFieldButtonGrp("Skin_Cluster_IO_window_selectInfoFile_btn", label="XML file path", text='/tmp/tmp.xml', buttonLabel='Browse', buttonCommand=lambda *args:gui_filePath())
    cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_texFielBtn", buttonLabel='<<<', label="Skin Cluster", text='', buttonCommand=lambda *args:loadSelectedSkc())
    cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_search", buttonLabel='<<<', label="Search", text='', buttonCommand=lambda *args:loadSelected("Skin_Cluster_IO_window_sourceSkinCluster_search"))
    cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_replace", buttonLabel='<<<', label="Replace", text='', buttonCommand=lambda *args:loadSelected("Skin_Cluster_IO_window_sourceSkinCluster_replace"))
    cmds.button("Skin_Cluster_IO_window_selectInfluencesBtn", label='Select Influences', command=lambda *args:guiGetInfs())
    cmds.button("Skin_Cluster_IO_window_importBtn", label='Import', command=lambda *args:guiImport())
    '''
    cmds.textFieldButtonGrp("pSkin_Cluster_IO_window_refix_texFielBtn", label="prefix", text=self.prefix, changeCommand = lambda *args:self.prefixChangeCommand(), buttonLabel='Load Selected', buttonCommand=lambda *args:self.prefixCommand() )
    cmds.button("Skin_Cluster_IO_window_driverCharacter_texFielBtn", label='Export Selected Channel Box Values', command=lambda *args:self.loadDrivingChar() )
    cmds.button("Skin_Cluster_IO_window_drivenCharacter_texFielBtn", label='Import Stored Channel Box Values', command=lambda *args:self.loadDrivenChar() )
    '''
    cmds.button("Skin_Cluster_IO_window_exportBtn", label='Export', command=lambda *args:guiExport())
    cmds.button("Skin_Cluster_IO_window_closeBtn", label='Close', command=('cmds.deleteUI(\"' + window_name + '\", window=True)') )

    cmds.setParent( '..' )
    cmds.showWindow( window_name )
    cmds.window(window_name , e=1, widthHeight=(500, 300))
    
def gui_filePath():
    """
    """
    singleFilter = "All Files (*.*)"
    currPath = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_selectInfoFile_btn", q=1, text=1)
    result = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=0, caption='Select or Define an XML file path (*.xml)', startingDirectory=currPath)
    if result:
        cmds.textFieldButtonGrp("Skin_Cluster_IO_window_selectInfoFile_btn", edit=True, text=result[0])
        
def loadSelectedSkc():
    sl1 = cmds.ls(sl=1)
    skc = mel.eval('findRelatedSkinCluster "{0}"'.format(sl1[0]))
    if sl1:
        if skc:
            sl1[0] = skc
        else:
            if not cmds.objectType(sl1[0]) == 'skinCluster':
                cmds.warning('skin cluster not selected ("{0}")....'.format(sl1[0]))
        cmds.textFieldButtonGrp('Skin_Cluster_IO_window_sourceSkinCluster_texFielBtn', e=1, text=sl1[0])
        
def loadSelected(txtFldGrp):
    sl1 = cmds.ls(sl=1)
    if sl1:
        sel = cmds.textFieldButtonGrp(txtFldGrp, e=1, text=sl1[0])
        
def guiExport():
    """
    """
    # Query/define
    skc = cmds.textFieldButtonGrp('Skin_Cluster_IO_window_sourceSkinCluster_texFielBtn', q=1, text=1)
    weightFilePath = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_selectInfoFile_btn", q=True, text=1)
    
    # export weight file
    write(skc, weightFilePath)
        
def guiImport():
    """
    """
    # Query/define
    skc = cmds.textFieldButtonGrp('Skin_Cluster_IO_window_sourceSkinCluster_texFielBtn', q=1, text=1)
    weightFilePath = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_selectInfoFile_btn", q=True, text=1)
    search = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_search", q=True, text=1)
    replace = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_replace", q=True, text=1)
    
    # Import weight file
    read(skc, weightFilePath, search=search, replace=replace)
        
def guiGetInfs():
    search = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_search", q=True, text=1)
    replace = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_sourceSkinCluster_replace", q=True, text=1)
    fPath = cmds.textFieldButtonGrp("Skin_Cluster_IO_window_selectInfoFile_btn", q=True, text=1)
    infList = getInfs(fPath)
    cmds.select([each.replace(search, replace) for each in infList])

