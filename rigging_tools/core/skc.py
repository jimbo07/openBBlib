"""
from jm_maya.rig.deform import skc
reload(skc)
skc.resetBindPreMatrices()
"""
from maya import cmds, mel

def resetBindPreMatrices(meshList=None):
    sl1 = cmds.ls(sl=1)
    if meshList:
        nodeList = meshList
    else:
        nodeList = cmds.ls(sl=1)
    cmds.select(cl=1)
    for each in nodeList:
        skc = mel.eval('findRelatedSkinCluster "{0}"'.format(each))
        infList = cmds.skinCluster(skc, q=1, inf=1)
        for inf in infList:
            con = cmds.listConnections('{0}.worldMatrix[0]'.format(inf), plugs=1, connections=1, s=0, d=1)
            for i, c in enumerate(con):
                if i % 2 == 0: continue
                if not skc in c: continue
                m1 = cmds.getAttr('{0}.worldInverseMatrix[0]'.format(inf))
                cmds.setAttr(c.replace('matrix', 'bindPreMatrix'), m1, type='matrix')
    cmds.select(sl1)

def copyWeights(srcMesh=None, destMesh=None, influenceAssociation=['closestJoint', 'oneToOne', 'name']):
    """
    Copies Skin Weights, matching influences first (works based on selection if no srcMesh & destMesh args passed)
    """
    sl = cmds.ls(sl=1)
    src = srcMesh or sl[0]
    dest = destMesh or sl[1]
    skc = mel.eval('findRelatedSkinCluster "{0}"'.format(src))
    inf = cmds.skinCluster(skc, q=1, inf=1)
    newSkc = mel.eval('findRelatedSkinCluster "{0}"'.format(dest))
    if not newSkc:
        cmds.select(inf, dest)
        newSkc = cmds.skinCluster(tsb=1)
    for each in inf:
        try: cmds.skinCluster(newSkc, e=1, ai=each)
        except: pass
        
    cmds.copySkinWeights(src, dest, noMirror=1, surfaceAssociation='closestPoint', influenceAssociation=influenceAssociation)

def copyWeightsConfirmDialog():
    """
    just presents a confirmation dialog before running copyWeights based on selection
    """
    sl = cmds.ls(sl=1)
    if len(sl)<1:
        cmds.warning('you must select source mesh first, and then destination mesh second')
        return
    src = sl[0]
    dest = sl[1]
    confirm = cmds.confirmDialog(title='Copy Skin Weights (matching influences first)',
        message='First select the source/driver mesh,\nthen shift select the destination/driven mesh second\n\n\nfrom:\n   {0}\nto:\n   {1}\n\n'.format(src, dest),
        button=['Go','Cancel'],
        defaultButton='Go',
        cancelButton='Cancel',
        dismissString='Cancel' )
    if confirm=='Go':
        print 'proceeding to copy skin weights ...'
        print 'source mesh = {0}'.format(src)
        print 'deformed mesh = {0}'.format(dest)
        return copyWeights(srcMesh=src, destMesh=dest)
