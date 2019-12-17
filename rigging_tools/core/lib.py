"""
generic lib for standard maya processes related to secret garden
"""
from maya import cmds

from ooutdmaya.rigging.core.util import names


def createNode(nodeType, description=None, side='', name=None, objAlreadyExistsInfo=False):
    """
    """
    objAlreadyExists = False
    if not name:
        name = names.nodeName(nodeType, description, side=side)
    if cmds.objExists(name):
        result = name
        objAlreadyExists = True
    else:
        result = cmds.createNode(nodeType, n=name)
    if objAlreadyExistsInfo:
        return {'result':result, 'objAlreadyExists':objAlreadyExists}
    else:
        return result
