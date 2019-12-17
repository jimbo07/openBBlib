"""
from jm_maya.rig.util.deform import wrap
reload(wrap)
wrap.createWrap('sourceMesh', 'destinationMesh', prefix='wrap1')
wrap.vertSnap('sourceMesh', ['destinationMesh'])
"""
from math import sqrt

from maya import cmds, mel

from ooutdmaya.common.mesh import lib


def getMeshShape(source, info=False):
    """
    """
    if cmds.objectType(source) == 'mesh':
        mesh = source
    else:
        children = cmds.listRelatives(source, children=1, type='mesh')
        mesh = children[0]
        for child in children:
            if cmds.getAttr('{0}.intermediateObject'.format(child)):
                if info: print('\tskippingmesh "{0}" is intermediateObject'.format(child))
                continue    
            mesh = child
    return mesh
    

def _create(src, dst, **kwargs):
    """
    """
    cmds.select(dst, src)
    #        [0]  : operation:  1 - Create a new wrap
    #                           2 - Add influence
    #                           3 - Remove influence
    #        [1]  : threshold:  The weight threshold to be used when creating 
    #                           a wrap
    #        [2]  : maxDist  :  The maxDistance to be used when creating a wrap
    #        [3]  : inflType :  The influence type (1 = point, 2 = face)
    #        [4]  : exclusiveBind :  Bind algorithm (0=smooth, 1=exclusive)
    #        [5]  : autoWeightThreshold :  Auto weight threshold control
    #        [6]  : renderInfl :  Render influence objects
    #        [7]  : falloffMode :  Distance falloff algorithm
    operation = kwargs.get('operation', 1)
    threshold = kwargs.get('threshold', 0)
    maxDistance = kwargs.get('maxDistance', 0.01)
    inflType = kwargs.get('inflType', 1)
    exclusiveBind = kwargs.get('exclusiveBind', 1)
    autoWeightThreshold = kwargs.get('autoWeightThreshold', 0)
    renderInfl = kwargs.get('renderInfl', 0)
    falloffMode = kwargs.get('falloffMode', 0)
    version = kwargs.get('version', 7)
    print('doWrapArgList('+str(version)+', {"'+str(operation)+'", "'+str(threshold)+'", "'+str(maxDistance)+'", "'+str(inflType)+'", "'+str(exclusiveBind)+'", "'+str(autoWeightThreshold)+'", "'+str(renderInfl)+'", "'+str(falloffMode)+'"});')
    mel.eval('doWrapArgList('+str(version)+', {"'+str(operation)+'", "'+str(threshold)+'", "'+str(maxDistance)+'", "'+str(inflType)+'", "'+str(exclusiveBind)+'", "'+str(autoWeightThreshold)+'", "'+str(renderInfl)+'", "'+str(falloffMode)+'"});')


def create(source, destination, prefix=None, suffix='_wrp', **kwargs):
    """
    Example:
    create(source='pSphere1', destination='pSphere2')
    """
    # cmds.select(destination, source)
    # data = mel.eval('CreateWrap')
    data = _create(source, destination, **kwargs)
    
    destMesh = getMeshShape(destination)
    wrapNode = cmds.listConnections('{0}.inMesh'.format(destMesh))[0]
    name = '{0}{1}'.format(wrapNode, suffix)
    if prefix:
        name = '{0}{1}'.format(prefix, suffix)
    return cmds.rename(wrapNode, name)

def vertSnap(destMesh, sourceMeshList, snapDistance=0.01):
    """
    from ooutdmaya.rigging.core.util.deform import wrap
    reload(wrap)
    # select source mesh(es) first, and then destination mesh last
    sel = cmds.ls(sl=1)
    wrap.vertSnap(sel[-1], sel[:-1])
    """
    
    # First create the wrap node
    cpoc = cmds.createNode('closestPointOnMesh')
    wrapNodeList = []
    for sourceMesh in sourceMeshList:
        wrapNode = create(prefix='{0}_drivenBy_{1}'.format(destMesh, sourceMesh), source=sourceMesh, destination=destMesh)
        wrapNodeList.append(wrapNode)
        sourceMeshShape = lib.getMeshShape(sourceMesh)
        cmds.connectAttr('{0}.worldMesh[0]'.format(sourceMeshShape), '{0}.inMesh'.format(cpoc), f=1)
        
        # find vertices that are closer than the snapDistance value
        destVtxNum = cmds.polyEvaluate(destMesh, vertex=1)
        destVtxList = []
        for vtx in xrange(0, destVtxNum):
            cmds.flushUndo()
            vtxPos = cmds.xform('{0}.vtx[{1}]'.format(destMesh, vtx), q=1, ws=1, t=1)
            cmds.setAttr('{0}.inPosition'.format(cpoc), vtxPos[0], vtxPos[1], vtxPos[2])
            closestVtx = cmds.getAttr('{0}.closestVertexIndex'.format(cpoc))
            srcVtxPos = cmds.xform('{0}.vtx[{1}]'.format(sourceMesh, closestVtx), q=1, ws=1, t=1)
            dist = sqrt((srcVtxPos[0] - vtxPos[0]) ** 2 + (srcVtxPos[1] - vtxPos[1]) ** 2 + (srcVtxPos[2] - vtxPos[2]) ** 2)
            if dist > snapDistance:
                continue
            destVtxList.append(vtx)
            
        # compile a list of vertices to remove from the wrap object set
        removeVtxList = []
        for vtx in xrange(0, destVtxNum):
            if not vtx in destVtxList:
                removeVtxList.append('{0}.vtx[{1}]'.format(destMesh, vtx))
        # remove non-matching vertices from the wrap node object set
        objectSet = cmds.listConnections('{0}.message'.format(wrapNode), type='objectSet', s=0, d=1)[0]
        print '\n\nremoveVtxList = {0}'.format(removeVtxList)
        print 'objectSet = {0}'.format(objectSet)
        print 'cmds.sets(removeVtxList, rm=objectSet)\n\n'
        cmds.sets(removeVtxList, rm=objectSet)
    # cleanup
    cmds.delete(cpoc)
    return wrapNodeList


def vertSnapSelectionDialog(selection=None):
    """Select source mesh(es) first, and then destination mesh last
    """
    sl = selection or cmds.ls(sl=1)
    if len(sl)<1:
        cmds.warning('you must first select source mesh(es) first, and then destination mesh last')
        return
    dest = sl[-1]
    src = sl[:-1]
    confirm = cmds.confirmDialog(title='Vert Snap',
        message='First select the source/driver mesh(es),\nthen shift select the destination/driven mesh last\n\n\nfrom:\n   {0}\nto:\n   {1}\n\n'.format([str(each) for each in src], dest),
        button=['Go','Cancel'],
        defaultButton='Go',
        cancelButton='Cancel',
        dismissString='Cancel' )
    if confirm=='Go':
        print 'proceeding to vert snap geometry...'
        print 'source meshes = {0}'.format(src)
        print 'deformed mesh = {0}'.format(dest)
        return vertSnap(dest, src)
        
