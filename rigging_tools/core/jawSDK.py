from maya import cmds

defaultSDK = {
    'protraction':{
        'locValue':0.25,
        'posTx':0.1,
        'posTz':0.1},
    'retraction':{
        'locValue':-0.25,
        'posTx':-0.1,
        'posTz':-0.1},
    'sideLeft':{
        'locValue':0.25,
        'rotRz':5},
    'sideRight':{
        'locValue':-0.25,
        'rotRz':-5},
    'open':{
        'locValue':-1,
        'rotRy':10,
        'rotTx':-0.1,
        'rotTz':-0.2},
    'close':{
        'locValue':0.25,
        'rotRy':-3,
        'rotTx':0.01,
        'rotTz':0.02},
    'limits':{
        'tx':[-0.25, 0.25],
        'ty':[-1, 0.25],
        'tz':[-0.25, 0.25]}
    }


def run(prefix='jaw', jawBase='jaw_jnt', jawEnd='jawEnd_jnt', sdkDict=defaultSDK, jawBaseUpVector=[0, 1, 0]):
    """ Creates a jaw which uses SDK to define ROM
    
    Example:
        from jm_maya.rig.face import jawSDK 
        
        cmds.file('/path/to/jaw/start/scene.mb', i=1, ns='Jaw_')
        
        prefix = 'Jaw'
        jawBase = 'Jaw_:joint1'
        jawEnd = 'Jaw_:joint2'
        jawBaseUpVector = [0, 1, 0]
        
        jawSDK.run(prefix=prefix, jawBase=jawBase, jawEnd=jawEnd, jawBaseUpVector=jawBaseUpVector)
    
    Args:
        prefix (str): Prefix for naming purposes
        jawBase (str): The base joint, ie. "jaw_jnt"
        jawEnd (str): The end joint, ie. "jawEnd_jnt"
        sdkDict (dict): Dict which contains all the information to be applied to the sdk
        jawBaseUpVector (list): The upvector for the resulting jaw (default [0,1,0])
        
    """
    
    if not sdkDict:
        raise ValueError("No sdk values defined")
    
    # Create a jaw base offset group to maintain the jaw base position
    # relative to all of our set driven key transforms that will
    # be parents of the jaw base    
    offsetGrp = cmds.createNode('transform', n='{0}Offset_GRP'.format(prefix))
    jawBaseParent = cmds.listRelatives(jawBase, parent=1)
    if jawBaseParent:
        cmds.delete(cmds.parentConstraint(jawBaseParent, offsetGrp))
        cmds.delete(cmds.scaleConstraint(jawBaseParent, offsetGrp))    
    cmds.parent(jawBase, offsetGrp)
    
    # Create a local space / zero group for set driven key transformations
    sdkZeroGrp = cmds.createNode('transform', n='{0}SetDrivenZero_GRP'.format(prefix))
    if jawBaseParent:
        cmds.parent(sdkZeroGrp, jawBaseParent)
    cmds.delete(cmds.parentConstraint(jawBase, sdkZeroGrp))
    cmds.delete(cmds.scaleConstraint(jawBase, sdkZeroGrp))
    # align via aim constraint
    cmds.delete(cmds.aimConstraint(jawEnd, sdkZeroGrp, aimVector=[1, 0, 0],
        upVector=[0, 0, 1], worldUpType='objectrotation', worldUpVector=jawBaseUpVector,
        worldUpObject=jawBase))
    
    # Create a rotation set driven key transform
    sdkRotGrp = cmds.duplicate(sdkZeroGrp, n='{0}SetDrivenRot_GRP'.format(prefix))[0]
    
    # Create a position set driven key transform
    sdkPosGrp = cmds.duplicate(sdkZeroGrp, n='{0}SetDrivenPos_GRP'.format(prefix))[0]
    
    # Parent all groups together
    cmds.parent(sdkRotGrp, sdkZeroGrp)
    cmds.parent(sdkPosGrp, sdkRotGrp)
    cmds.parent(offsetGrp, sdkPosGrp)
    
    # Create a transform to drive our jaw transformations
    sdkDriverLoc = cmds.spaceLocator(n='{0}SdkDriver_LOC'.format(prefix))[0]
    cmds.delete(cmds.pointConstraint(jawEnd, sdkDriverLoc))
    sdkDriverLocGrp = cmds.createNode('transform', n='{0}SdkDriverLoc_GRP'.format(prefix))
    cmds.delete(cmds.pointConstraint(jawEnd, sdkDriverLocGrp))
    cmds.parent(sdkDriverLoc, sdkDriverLocGrp)
    
    # Set driven keys
    posTxAttrPlug = '{0}.translateX'.format(sdkPosGrp)
    posTzAttrPlug = '{0}.translateZ'.format(sdkPosGrp)
    rotTxAttrPlug = '{0}.translateX'.format(sdkRotGrp)
    rotTzAttrPlug = '{0}.translateZ'.format(sdkRotGrp)
    rotRyAttrPlug = '{0}.rotateY'.format(sdkRotGrp)
    rotRzAttrPlug = '{0}.rotateZ'.format(sdkRotGrp)
    
    # Protraction/Retraction driven keys
    cmds.setDrivenKeyframe(posTxAttrPlug,
        currentDriver='{0}.translateZ'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(posTzAttrPlug,
        currentDriver='{0}.translateZ'.format(sdkDriverLoc))
    # rename sdk nodes
    posTxSdk = cmds.listConnections(posTxAttrPlug, s=1, d=0, type='animCurve')[0]
    posTxSdk = cmds.rename(posTxSdk, '{0}PosTx_SDK'.format(prefix))
    posTzSdk = cmds.listConnections(posTzAttrPlug, s=1, d=0, type='animCurve')[0]
    posTzSdk = cmds.rename(posTzSdk, '{0}PosTz_SDK'.format(prefix))
    
    # Protraction driven key
    cmds.setAttr('{0}.translateZ'.format(sdkDriverLoc), sdkDict['protraction']['locValue'])
    cmds.setAttr(posTxAttrPlug, sdkDict['protraction']['posTx'])
    cmds.setAttr(posTzAttrPlug, sdkDict['protraction']['posTz'])
    cmds.setDrivenKeyframe(posTxAttrPlug,
        currentDriver='{0}.translateZ'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(posTzAttrPlug,
        currentDriver='{0}.translateZ'.format(sdkDriverLoc))
    
    # Retraction driven key
    cmds.setAttr('{0}.translateZ'.format(sdkDriverLoc), sdkDict['retraction']['locValue'])
    cmds.setAttr(posTxAttrPlug, sdkDict['retraction']['posTx'])
    cmds.setAttr(posTzAttrPlug, sdkDict['retraction']['posTz'])
    cmds.setDrivenKeyframe(posTxAttrPlug,
        currentDriver='{0}.translateZ'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(posTzAttrPlug,
        currentDriver='{0}.translateZ'.format(sdkDriverLoc))
    cmds.setAttr('{0}.translateZ'.format(sdkDriverLoc), 0)
    
    # Sideways driven keys
    cmds.setDrivenKeyframe(rotRzAttrPlug,
        currentDriver='{0}.translateX'.format(sdkDriverLoc))
    # rename sdk node
    rotRzSdk = cmds.listConnections(rotRzAttrPlug, s=1, d=0, type='animCurve')[0]
    rotRzSdk = cmds.rename(rotRzSdk, '{0}RotRz_SDK'.format(prefix))
    
    # Sideways left driven key
    cmds.setAttr('{0}.translateX'.format(sdkDriverLoc), sdkDict['sideLeft']['locValue'])
    cmds.setAttr(rotRzAttrPlug, sdkDict['sideLeft']['rotRz'])
    cmds.setDrivenKeyframe(rotRzAttrPlug,
        currentDriver='{0}.translateX'.format(sdkDriverLoc))
        
    # Sideways right driven key
    cmds.setAttr('{0}.translateX'.format(sdkDriverLoc), sdkDict['sideRight']['locValue'])
    cmds.setAttr(rotRzAttrPlug, sdkDict['sideRight']['rotRz'])
    cmds.setDrivenKeyframe(rotRzAttrPlug,
        currentDriver='{0}.translateX'.format(sdkDriverLoc))
    cmds.setAttr('{0}.translateX'.format(sdkDriverLoc), 0)
    
    # Open/Close driven keys
    cmds.setDrivenKeyframe(rotRyAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(rotTxAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(rotTzAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    
    # rename sdk node
    rotRySdk = cmds.listConnections(rotRyAttrPlug, s=1, d=0, type='animCurve')[0]
    rotRySdk = cmds.rename(rotRySdk, '{0}RotRy_SDK'.format(prefix))
    rotTxSdk = cmds.listConnections(rotTxAttrPlug, s=1, d=0, type='animCurve')[0]
    rotTxSdk = cmds.rename(rotTxSdk, '{0}RotTx_SDK'.format(prefix))
    rotTzSdk = cmds.listConnections(rotTzAttrPlug, s=1, d=0, type='animCurve')[0]
    rotTzSdk = cmds.rename(rotTzSdk, '{0}RotTz_SDK'.format(prefix))
        
    # Open driven key
    cmds.setAttr('{0}.translateY'.format(sdkDriverLoc), sdkDict['open']['locValue'])
    cmds.setAttr(rotRyAttrPlug, sdkDict['open']['rotRy'])
    cmds.setAttr(rotTxAttrPlug, sdkDict['open']['rotTx'])
    cmds.setAttr(rotTzAttrPlug, sdkDict['open']['rotTz'])
    cmds.setDrivenKeyframe(rotRyAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(rotTxAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(rotTzAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
        
    # Close driven key
    cmds.setAttr('{0}.translateY'.format(sdkDriverLoc), sdkDict['close']['locValue'])
    cmds.setAttr(rotRyAttrPlug, sdkDict['close']['rotRy'])
    cmds.setAttr(rotTxAttrPlug, sdkDict['close']['rotTx'])
    cmds.setAttr(rotTzAttrPlug, sdkDict['close']['rotTz'])
    cmds.setDrivenKeyframe(rotRyAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(rotTxAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setDrivenKeyframe(rotTzAttrPlug,
        currentDriver='{0}.translateY'.format(sdkDriverLoc))
    cmds.setAttr('{0}.translateY'.format(sdkDriverLoc), 0)
    
    # Set tangents to linear
    cmds.keyTangent(posTxSdk, itt='linear', ott='linear', e=1)
    cmds.keyTangent(posTzSdk, itt='linear', ott='linear', e=1)
    cmds.keyTangent(rotRzSdk, itt='linear', ott='linear', e=1)
    cmds.keyTangent(rotRySdk, itt='linear', ott='linear', e=1)
    cmds.keyTangent(rotTxSdk, itt='linear', ott='linear', e=1)
    cmds.keyTangent(rotTzSdk, itt='linear', ott='linear', e=1)
    
    # Set transform limits
    cmds.transformLimits(sdkDriverLoc, tx=sdkDict['limits']['tx'], etx=[1, 1])
    cmds.transformLimits(sdkDriverLoc, ty=sdkDict['limits']['ty'], ety=[1, 1])
    cmds.transformLimits(sdkDriverLoc, tz=sdkDict['limits']['tz'], etz=[1, 1])
    
