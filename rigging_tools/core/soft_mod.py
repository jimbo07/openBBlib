"""Library for working
"""
from maya import cmds, mel
from ooutdmaya.rigging.core.util.mesh import rivet
reload(rivet)
from ooutdmaya.rigging.core.util import mesh
reload(mesh)
from ooutdmaya.rigging.core import util
reload(util)

def shotSculpt(baseName=None, mesh=None, fallOffRadiusAttr='falloffRadius',
            envelopeAttr='envelope', falloffModeAttr='falloffMode', attachToMesh=True, useRivet=True):
    """Creates a soft-mod with an adjustable area of influence
    
    Select the vertex where you want the softmod positioned,
    then run. Alternatively you can specify attachToMesh=False
    in order to skip the rivet/mesh constraining behavior.
    You can also pass in a vertex path via the mesh argument instead
    of running based on selection
    
    :param baseName: name to give resulting transforms
    :param mesh: mesh to affect
    :param fallOffRadiusAttr: attribute name to give resulting soft mod driver node
    :param envelopeAttr: attribute name to give resulting soft mod driver node
    :param falloffModeAttr: attribute name to give resulting soft mod driver node
    :param attachToMesh: whether to constrain the soft mod to an already deforming mesh
    :type baseName: name to give resulting transforms
    :type mesh: mesh to affect
    :type fallOffRadiusAttr: string
    :type envelopeAttr: string
    :type falloffModeAttr: string
    :type attachToMesh: bool
    :returns: dictionary of resulting nodes
    :rtype: dict

    :Example:
    
    from ooutdmaya.rigging.core.util.deform import softMod
    
    # build an example sphere
    pSphereData = cmds.polySphere(ch=0)
        
    # build an example skinCluster applied to the sphere
    jnt1 = cmds.joint(p=[0, -1, 0])
    jnt2 = cmds.joint(p=[0, 0, 0])
    cmds.joint(jnt1, e=1, zso=1, oj='xyz', sao='yup')
    jnt3 = cmds.joint(p=[0, 1, 0])
    cmds.joint(jnt2, e=1, zso=1, oj='xyz', sao='yup')
    cmds.select(cl=1)
    cmds.select(jnt1, jnt2, mesh)
    cmds.skinCluster(tsb=1)
    
    # select a vertex
    cmds.select('{0}.vtx[279]'.format(pSphereData[0]))
    
    # build the soft mod
    softMod.shotSculpt()
    # Result: {'ctl': u'shotSculpt1_grp',
     'ctlGrp': u'shotSculpt1Grp_grp',
     'ctlPiv': u'shotSculpt1Pivot_grp',
     'ctlPivGrp': u'shotSculpt1PivotGrp_grp',
     'grpParent': u'shotSculpt1PivotGrp_grp',
     'smd': u'shotSculpt1_smdHandle'} # 

    .. warning:: Expects non-overlapping UVs
    .. todo:: Add support for adding multiple meshes to be deformed,
        and also a helper function for adding meshes to pre-existing soft mods
    """
    retData = {}
    # If no arguments passed, work on selection
    if not mesh:
        try:
            sel = cmds.ls(sl= True)
            mesh = sel[0]
        except Exception, e:
            raise RuntimeError('Invalid Mesh Selection,\n\t{0}'.format(e))
        
    # Generate unique name
    if not baseName:
        startString = 'shotSculpt'
        i=1
        baseName = startString+str(i)
        smdName = util.names.nodeName('softMod', baseName)
        while cmds.objExists(smdName):
            i += 1
            baseName = startString+str(i) 
            smdName = util.names.nodeName('softMod', baseName)
    else:
        smdName = util.names.nodeName('softMod', baseName)
            
    vtxPlug = mesh
    mesh = mel.eval('plugNode("{0}")'.format(str(vtxPlug)))
    if vtxPlug != mesh:
        softModPos = cmds.xform(vtxPlug, ws=1, t=1, q=1)
    else:
        softModPos = cmds.xform(mesh, ws=1, rp=1, q=1)
    
    # Piv ctl
    softModCenterCtlGrp = cmds.createNode('transform',
        n=util.names.nodeName('transform', '{0}PivotGrp'.format(baseName)))
    softModCenterCtl = cmds.spaceLocator(n=util.names.nodeName('transform', '{0}Pivot'.format(baseName)))[0]
    cmds.parent(softModCenterCtl, softModCenterCtlGrp)
    locatorShape = cmds.listRelatives(softModCenterCtl, children=1, type='locator')[0]
    grpParent = softModCenterCtlGrp
    
    # Soft Mod ctl
    softModCtlGrp = cmds.createNode('transform',
        n=util.names.nodeName('transform', '{0}Grp'.format(baseName)))
    softModCtl = cmds.circle(
        n=util.names.nodeName('transform', '{0}'.format(baseName)))[0]
    cmds.parent(softModCtl, softModCtlGrp)
    cmds.parent(softModCtlGrp, softModCenterCtl)
    
    meshConnections = cmds.listConnections('{0}.inMesh'.format(mesh), s=1, d=0, plugs=1)
    if attachToMesh and meshConnections:
        # Create a transform constrained to the mesh
        rivetGrp = cmds.createNode('transform',
            n=util.names.addModifier(softModCenterCtlGrp, 'transform', addSuffix='Rivet'))
        grpParent = rivetGrp
        retData['rivetGrp'] = rivetGrp
        # Parent the soft mode group under the rivet group
        cmds.parent(softModCenterCtlGrp, rivetGrp)
        # Position the group
        cmds.xform(rivetGrp, ws=1, t=softModPos)
        # Constrain the transform
        if useRivet:
            rivetData = util.mesh.rivet.auto_rivet_transforms_to_meshes([rivetGrp, mesh])
            for inMeshAttr in rivetData['inMeshAttrs']:
                cmds.connectAttr('{0}'.format(meshConnections[0]), inMeshAttr, f=1)
            locShapes = cmds.listRelatives(rivetData['loc'], type='locator')
            if locShapes:
                cmds.hide(locShapes)
        else:
            popcList = util.mesh.rivet.attachTransformsToMesh(transformList=[rivetGrp], geo=mesh)
            for popc in popcList:
                cmds.connectAttr('{0}'.format(meshConnections[0]), '{0}.target[0].targetMesh'.format(popc), f=1)
    else:
        # Query the position to place the softmod
        cmds.xform(softModCenterCtlGrp, t=softModPos, ws=1)
        
    # build soft mod
    softModData = cmds.softMod("{0}".format(mesh), falloffRadius=2, falloffMode=0,
        falloffBasedOnX=1, falloffBasedOnY=1, falloffBasedOnZ=1, falloffAroundSelection=0,
        falloffMasking=1, n=smdName)
        
    # Add attributes to the soft mod control, and connect those attributes
    cmds.addAttr(softModCtl, at='double', ln=envelopeAttr, k=1, dv=1, min=0, max=1)
    cmds.connectAttr(
        '{0}.{1}'.format(softModCtl, envelopeAttr),
        '{0}.{1}'.format(softModData[0], envelopeAttr), f=1)
    cmds.addAttr(softModCtl, at='double', ln=fallOffRadiusAttr, k=1, dv=1)
    cmds.connectAttr(
        '{0}.{1}'.format(softModCtl, fallOffRadiusAttr),
        '{0}.{1}'.format(softModData[0], fallOffRadiusAttr), f=1)
    cmds.addAttr(softModCtl, at='enum', ln=falloffModeAttr, k=1, en='Volume:Surface')
    cmds.connectAttr(
        '{0}.{1}'.format(softModCtl, falloffModeAttr),
        '{0}.{1}'.format(softModData[0], falloffModeAttr), f=1)
    
    # connect the pivot control
    cmds.connectAttr('{0}.worldPosition[0].worldPositionX'.format(locatorShape), '{0}.falloffCenterX'.format(softModData[0]), f=1)
    cmds.connectAttr('{0}.worldPosition[0].worldPositionY'.format(locatorShape), '{0}.falloffCenterY'.format(softModData[0]), f=1)
    cmds.connectAttr('{0}.worldPosition[0].worldPositionZ'.format(locatorShape), '{0}.falloffCenterZ'.format(softModData[0]), f=1)
    
    # connect the soft mod control
    # cmds.parent(softModData[1], softModCtl)
    con = cmds.listConnections('{0}.softModXforms'.format(softModData[0]), s=1, d=0, plugs=1, connections=1)
    cmds.disconnectAttr(con[1], con[0])
    cmds.connectAttr('{0}.worldMatrix[0]'.format(softModCtl), '{0}.matrix'.format(softModData[0]), f=1)
    cmds.connectAttr('{0}.worldMatrix[0]'.format(softModCenterCtl), '{0}.preMatrix'.format(softModData[0]), f=1)
    cmds.connectAttr('{0}.matrix'.format(softModCtl), '{0}.weightedMatrix'.format(softModData[0]), f=1)
    cmds.connectAttr('{0}.worldInverseMatrix[0]'.format(softModCenterCtl), '{0}.postMatrix'.format(softModData[0]), f=1)
    # cmds.connectAttr('{0}.worldMatrix[0]'.format(softModCenterCtl), '{0}.preMatrix'.format(softModData[0]), f=1)
    
    cmds.delete(softModData[1])
    
    retData['smd'] = softModData[1]
    retData['ctl'] = softModCtl
    retData['ctlGrp'] = softModCtlGrp
    retData['ctlPiv'] = softModCenterCtl
    retData['ctlPivGrp'] = softModCenterCtlGrp
    retData['grpParent'] = grpParent
    
    return retData
