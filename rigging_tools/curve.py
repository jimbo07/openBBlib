"""
Generic lib for curve related stuff
"""
from maya import cmds, mel
import maya.OpenMaya as om
    
from ooutdmaya.common.util import names
reload(names)

def nurbsCurveShapes(nodeList, f=1):
    nrbCrvList = []
    for each in nodeList:
        if cmds.objectType(each) == 'nurbsCurve':
            nrbCrvList.append(each)
        else:
            nrbCrvChldrn = cmds.listRelatives(each, type='nurbsCurve', f=f)
            if not nrbCrvChldrn:
                continue
            nrbCrvList = nrbCrvList+nrbCrvChldrn
    return nrbCrvList

def pointOnCurve(curve, param):
    """
    Returns positional information for a curve based on a parameter
    """
    # normalize the curve
    uniformCurve = cmds.rebuildCurve(curve, ch=0, rpo=False, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=3, tol=0.01)
    # query curve shape
    curveShape = cmds.listRelatives(uniformCurve, type='shape')[0]
    # create point on curve info
    poci = cmds.createNode('pointOnCurveInfo')
    # connect curve shape to point on curve info
    cmds.connectAttr('%s.worldSpace[0]' % curveShape, '%s.inputCurve' % poci)
    # set curve on info param
    cmds.setAttr("%s.parameter" % poci, param)
    # setup return data object
    returnData = {}
    # set position key value pair
    returnData['position'] = cmds.getAttr('%s.position' % poci)[0]
    # delete extraneous nodes
    cmds.delete(poci, uniformCurve)
    # done
    return returnData


def curveInfo(curve):
    """
    returns information about the supplied curve
    """
    # normalize the curve
    uniformCurve = cmds.rebuildCurve(curve, ch=0, rpo=False, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=0, d=3, tol=0.01)
    # query curve shape
    curveShape = cmds.listRelatives(uniformCurve, type='shape')[0]
    # create point on curve info
    cvi = cmds.createNode('curveInfo')
    # connect curve shape to point on curve info
    cmds.connectAttr('%s.worldSpace[0]' % curveShape, '%s.inputCurve' % cvi)
    # setup return data object
    returnData = {}
    # set arcLength key value pair
    returnData['arcLength'] = cmds.getAttr('%s.arcLength' % cvi)
    # delete extraneous nodes
    cmds.delete(cvi, uniformCurve)
    # done
    return returnData

def curveToJoints(curve, numJoints, name=None, oj='xyz', sao='yup'):
    """
    """
    crvShape = curve
    if not cmds.objectType(crvShape) == 'nurbsCurve':
        children = cmds.listRelatives(curve, children=1, type='nurbsCurve')
        if not children:
            raise Exception('the supplied curve argument {0} is not a curve'.format(curve))
        crvShape = children[0]
    
    def getDagPath(node=None):
        sel = om.MSelectionList()
        sel.add(node)
        d = om.MDagPath()
        sel.getDagPath(0, d)
        return d
        
    cmds.select(cl=1)
    chain = []
    crvFn = om.MFnNurbsCurve(getDagPath(crvShape))
    for i in range(0, numJoints):
        parameter = crvFn.findParamFromLength( (crvFn.length() / (float(numJoints)-1)) * i )
        # param = i/float(numJoints-1)
        pos = om.MPoint()
        crvFn.getPointAtParam(parameter, pos)
        if i < (numJoints-1):
            jntName = names.nodeName('joint', '{0}{1}'.format(name, str(i + 1)))
        else:
            jntName = names.nodeName('joint', '{0}End'.format(name))
        jnt = cmds.joint(p=[pos.x, pos.y, pos.z], n=jntName)
        if i > 0:
            jntName = names.nodeName('joint', '{0}{1}'.format(name, str(i + 1)))
            cmds.joint(chain[i-1], e=1, zso=1, oj=oj, sao=sao)
            # jntName = util.names.nodeName('joint', '{0}End'.format(baseName))
        chain.append(jnt)
    cmds.setAttr('{0}.jo'.format(chain[-1]), 0, 0, 0)
    cmds.select(cl=1)
    
    return chain

def uniformCurve(curveName, name=None, degree=3):
    """
    Returns a live, parametricallu unifrom curve driven by the supplied curve
    """
    name = name or curveName
    # build a live normalized curve
    uniCrvName = names.nodeName('nurbsCurve', '{0}Uniform'.format(name))
    uniformCurve = cmds.rebuildCurve(curveName, ch=1, rpo=0, rt=0, end=1, kr=0, kcp=1, kep=0, kt=1, s=0, d=degree, tol=0.01, name=uniCrvName)
    # query curve shape
    curveShape = cmds.listRelatives(uniformCurve, type='shape')[0]
    rebuildCrvName = names.nodeName('rebuildCurve', name)
    rebuildCrvName = cmds.rename(uniformCurve[1], rebuildCrvName)
    
    return {'crv':[uniformCurve[0]], 'crvShape':curveShape, 'rebuildCurve':[rebuildCrvName]}

def grpsToMotionPath(curveName, grpList, name=None, pointConstraint=True, createTangentLocs=False):
    """
    Creates locators matching the number of transforms (grpList)
    and a motion path for locator
    which positions locator along by the curve (curveName)
    and finally locator point constrains each transform (grpList), if so desired 
    """
    retData = {}
    retData['grpMap'] = {}
    name = name or curveName
    locList = []
    mphList = []
    pocList = []
    npoc = cmds.createNode('nearestPointOnCurve')
    crvShape = curveName
    if not cmds.objectType(crvShape) == 'nurbsCurve':
        children = cmds.listRelatives(curveName, children=1, type='nurbsCurve')
        if not children:
            raise Exception('the supplied curve argument {0} is not a curve'.format(curveName))
        crvShape = children[0]
    cmds.connectAttr('{0}.worldSpace[0]'.format(crvShape), '{0}.inputCurve'.format(npoc))
    '''
    cviName = names.nodeName('curveInfo', '{0}'.format(name))
    cvi = cmds.createNode('curveInfo', n=cviName)
    cmds.connectAttr('{0}.worldSpace[0]'.format(crvShape), '{0}.inputCurve'.format(cvi))
    arcLenAttr = '{0}.arcLength'.format(cvi)
    '''
    for i, grp in enumerate(grpList):
        '''
        i = 6
        grp = 'test7_jnt'
        '''
        retData['grpMap'][grp] = {}
        pos = cmds.xform(grp, t=1, ws=1, q=1)
        cmds.setAttr('{0}.inPosition'.format(npoc), pos[0], pos[1], pos[2])
        param = cmds.getAttr('{0}.parameter'.format(npoc))
        
        mphLocName = names.nodeName('locator', '{0}{1}'.format(name, i+1))
        mphLoc = cmds.spaceLocator(n=mphLocName)[0]
        locList.append(mphLoc)
        retData['grpMap'][grp]['loc'] = mphLoc
        crvMphName = names.nodeName('motionPath', '{0}{1}'.format(name, i+1))
        crvMph = cmds.createNode('motionPath', n=crvMphName)
        retData['grpMap'][grp]['mph'] = crvMph
        mphList.append(crvMph)
        cmds.setAttr('{0}.fractionMode'.format(crvMph), 1)
        
        cmds.connectAttr('{0}.worldSpace[0]'.format(crvShape), '{0}.geometryPath'.format(crvMph))
        cmds.setAttr('{0}.uValue'.format(crvMph), param)
        cmds.connectAttr('{0}.xCoordinate'.format(crvMph), '{0}.tx'.format(mphLoc))
        cmds.connectAttr('{0}.yCoordinate'.format(crvMph), '{0}.ty'.format(mphLoc))
        cmds.connectAttr('{0}.zCoordinate'.format(crvMph), '{0}.tz'.format(mphLoc))
        
        if pointConstraint:
            poc = cmds.pointConstraint(mphLoc, grp, mo=1, n=names.addModifier(grp, 'pointConstraint'))
            retData['grpMap'][grp]['poc'] = poc
    cmds.delete(npoc)
            
    retData['loc'] = locList
    retData['poc'] = pocList
    retData['mph'] = mphList
    
    # Start and End tangent locators
    retData['sTanLoc']= {}
    retData['eTanLoc']= {}
    if createTangentLocs:
        # Start
        mphLocName = names.nodeName('locator', '{0}StartTangent'.format(name))
        mphLoc = cmds.spaceLocator(n=mphLocName)[0]
        retData['sTanLoc']['loc'] = mphLoc
        crvMphName = names.nodeName('motionPath', '{0}StartTangent'.format(name))
        crvMph = cmds.createNode('motionPath', n=crvMphName)
        retData['sTanLoc']['mph'] = crvMph
        mphList.append(crvMph)
        cmds.setAttr('{0}.fractionMode'.format(crvMph), 1)
        # Start connections
        cmds.connectAttr('{0}.worldSpace[0]'.format(crvShape), '{0}.geometryPath'.format(crvMph))
        cmds.setAttr('{0}.uValue'.format(crvMph), 0.001)
        cmds.connectAttr('{0}.xCoordinate'.format(crvMph), '{0}.tx'.format(mphLoc))
        cmds.connectAttr('{0}.yCoordinate'.format(crvMph), '{0}.ty'.format(mphLoc))
        cmds.connectAttr('{0}.zCoordinate'.format(crvMph), '{0}.tz'.format(mphLoc))
        # End
        mphLocName = names.nodeName('locator', '{0}EndTangent'.format(name))
        mphLoc = cmds.spaceLocator(n=mphLocName)[0]
        retData['eTanLoc']['loc'] = mphLoc
        crvMphName = names.nodeName('motionPath', '{0}EndTangent'.format(name))
        crvMph = cmds.createNode('motionPath', n=crvMphName)
        retData['eTanLoc']['mph'] = crvMph
        mphList.append(crvMph)
        cmds.setAttr('{0}.fractionMode'.format(crvMph), 1)
        # Start connections
        cmds.connectAttr('{0}.worldSpace[0]'.format(crvShape), '{0}.geometryPath'.format(crvMph))
        cmds.setAttr('{0}.uValue'.format(crvMph), 0.999)
        cmds.connectAttr('{0}.xCoordinate'.format(crvMph), '{0}.tx'.format(mphLoc))
        cmds.connectAttr('{0}.yCoordinate'.format(crvMph), '{0}.ty'.format(mphLoc))
        cmds.connectAttr('{0}.zCoordinate'.format(crvMph), '{0}.tz'.format(mphLoc))
        
        
    return retData

def numCVs(curve):
    # get the control points for the curve
    curveSel = om.MSelectionList()
    om.MGlobal.getSelectionListByName(curve, curveSel)
    curvePath = om.MDagPath()
    curveSel.getDagPath(0, curvePath)
    curveFn = om.MFnNurbsCurve(curvePath)
    numCVs = curveFn.numCVs()
    return numCVs

def clusterize(curve, baseName=None):
    """
    Creates clusters for each CV
    """
    if not baseName:
        baseName = curve
    
    # get the control points for the curve
    cvCount = numCVs(curve)
    
    # create a control set
    # cmds.select(cl= True)
    # self.controlSel = cmds.sets(n= self.getName('SEL', 'Control'))
    # clusterize each control point
    csrList = []
    cshList = []
    csrGrpList = []
    controlPoints = []
    for point in xrange(0, cvCount):
        controlPoints.append(point)
        cshName = names.nodeName("clusterHandle", description='{0}{1}'.format(baseName, point))
        csrName = names.nodeName("cluster", description='{0}{1}'.format(baseName, point))
        csrGrpName = names.nodeName("transform", description='{0}{1}'.format(baseName, point))
        csr = cmds.cluster('%s.cv[%s]' % (curve, point))
        csrName = cmds.rename(csr[0], csrName)
        csrGrpName = cmds.rename(csr[1], csrGrpName)
        csrChildren = cmds.listRelatives(csrGrpName, children=True, shapes=True, type='clusterHandle')
        if csrChildren:
            for shape in csrChildren:    
                cshName = cmds.rename(shape, cshName)
        csrList.append(csrName)
        csrGrpList.append(csrGrpName)
        cshList.append(cshName)
        cmds.hide(csrGrpName)
        
    retArgs = {}
    retArgs['controlPoints'] = controlPoints
    retArgs['csrList'] = csrList
    retArgs['csrGrpList'] = csrGrpList
    retArgs['cshList'] = cshList
    return retArgs

def curveFromCylinderEdge(cylinderEdge=None):
    """
    # Example
    from ooutdmaya.common import curve
    reload(curve)
    
    # Pass in the edge name to work from
    crv = curve.curveFromCylinderEdge('polySurface25.e[214]')
    
    # Work based on selection
    cmds.select('polySurface25.e[214]')
    crv = curve.curveFromCylinderEdge()
    """
    if cylinderEdge:
        cmds.select(cylinderEdge)

    cmds.polySelectSp(loop=1)
    edges = cmds.ls(sl=1)
    mel.eval('ConvertSelectionToVertices;')
    # sl = cmds.ls(sl=1)
    sl = cmds.filterExpand(sm=31, expand=1)
    
    locList = []
    posList = []
    for each in sl:
        # each = 'polySurface25.vtx[478]'
        cmds.select(each)
        mel.eval('PolySelectConvert 2;')
        cmds.select(edges, d=1)
        cmds.polySelectSp(loop=1)
        mel.eval('ConvertSelectionToVertices;')
        edgeVtx = cmds.filterExpand(sm=31, expand=1)
        posDict = {'x':[], 'y':[], 'z':[]}
        for vtx in edgeVtx:
            pos = cmds.xform(vtx, q=1, ws=1, t=1)
            posDict['x'].append(pos[0])
            posDict['y'].append(pos[1])
            posDict['z'].append(pos[2])
        
        posX = reduce(lambda x, y: x + y, posDict['x']) / len(posDict['x'])
        posY = reduce(lambda x, y: x + y, posDict['y']) / len(posDict['y'])
        posZ = reduce(lambda x, y: x + y, posDict['z']) / len(posDict['z'])
        
        posList.append([posX, posY, posZ])
        '''
        loc = cmds.spaceLocator()[0]
        locList.append(loc)
        cmds.xform(loc, ws=1, t=[posX, posY, posZ])
        '''
    return cmds.curve(d=1, p=posList, k=[i for i in xrange(0, len(posList))])


def curveFromCylinderEdgeGUI():
    """
    from ooutdmaya.common import curve
    reload(curve)
    crv = curve.curveFromCylinderEdgeGUI()
    """
    # Make a new window
    #
    windowBaseName = 'curveFromCylinderEdge'
    window = '{0}Window'.format(windowBaseName)
    edgeTxtFldBtnGrp = '{0}TxtFldGrp2'.format(windowBaseName)
    wWidth = 500
    wHeight = 100
    if cmds.window(window, exists=1, q=1):
        cmds.deleteUI(window)
    window = cmds.window(window, title="Curve From Polygon Cylinder Edge", iconName='Curve From Cylinder Edge', widthHeight=(wWidth, wHeight))
    cmds.columnLayout( adjustableColumn=True )
    edgeTxtFldBtnGrp = cmds.textFieldButtonGrp(edgeTxtFldBtnGrp, label='Edge', text='', buttonLabel='<<<' )
    edgeTxtFldBtnGrp = cmds.textFieldButtonGrp(edgeTxtFldBtnGrp, e=1, buttonCommand='cmds.textFieldButtonGrp("{0}", e=1, text=cmds.ls(sl=1)[0])'.format(edgeTxtFldBtnGrp))

    cmd = 'edge=cmds.textFieldButtonGrp("{0}", q=1, text=1); from ooutdmaya.common import curve; reload(curve); crv = curve.curveFromCylinderEdge(edge)'.format(edgeTxtFldBtnGrp)
    cmds.button( label='Build',  command=cmd)
    cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
    cmds.setParent( '..' )
    cmds.showWindow( window )
    cmds.window( window, edit=True, widthHeight=(wWidth, wHeight) )
