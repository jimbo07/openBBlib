"""Helper functions for dealing with polygonal meshes
"""
from maya import cmds

def getMeshShape(source=None, info=False):
    """
    """
    # if no arguments passed, work on selection
    if not source:
        try:
            sel = cmds.ls(sl= True)
            source = sel[0]
        except Exception, e:
            raise RuntimeError('Invalid Selection,\n\t{0}'.format(e))
    # query source shape node
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
