"""
"""
from maya import cmds

from ooutdmaya.rigging.core.util.deform import wrap

def create(sourceMesh, destMesh, name=None, useVertsnapPlugin=True):
    """
    """
    if useVertsnapPlugin:
        pluginName = 'oouCfx.so'
        if not cmds.pluginInfo(pluginName, loaded=1, q=1):
            cmds.loadPlugin(pluginName)
            print 'loading "{0}" from:\n\t{1}'.format(pluginName, cmds.pluginInfo(pluginName, path=1, q=1))
        name = name or '{0}_vts'.format(destMesh)
        vts = cmds.deformer(destMesh, type='vertSnap',n=name)[0]
        cmds.connectAttr(sourceMesh+'.worldMesh[0]', vts+'.driverMesh')
        cmds.setAttr(vts+'.initialize', 1)
        return vts

def createSelected(name=None, useVertsnapPlugin=True):
    """
    """
    sel = cmds.ls(sl=1)
    if useVertsnapPlugin:
        return create(sourceMesh=sel[0], destMesh=sel[1], name=name, useVertsnapPlugin=useVertsnapPlugin)
    else:
        wrap.vertSnap(dest=sel[1], src=sel[0])


def vertSnapSelectionDialog(selection=None):
    """Select source mesh first, and then destination mesh last
    """
    sl = selection or cmds.ls(sl=1)
    if len(sl)<1:
        cmds.warning('you must first select source mesh(es) first, and then destination mesh last')
        return
    dest = sl[1]
    src = sl[0]
    confirm = cmds.confirmDialog(title='Vert Snap',
        message='First select the source/driver mesh,\nthen shift select the destination/driven mesh last\n\n\nfrom:\n   {0}\nto:\n   {1}\n\n'.format(src, dest),
        button=['Go','Cancel'],
        defaultButton='Go',
        cancelButton='Cancel',
        dismissString='Cancel' )
    if confirm=='Go':
        print 'proceeding to vert snap geometry...'
        print 'source meshes = {0}'.format(src)
        print 'deformed mesh = {0}'.format(dest)
        return createSelected()
