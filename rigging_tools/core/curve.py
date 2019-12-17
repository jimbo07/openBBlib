"""
"""
from maya import cmds
import maya.OpenMaya as om

from ooutdmaya.common import curve
reload(curve)

def numCVs(*args, **kwargs):
    cmds.warning('ooutdmaya.rigging.core.util.curve.numCVs now DEPRECIATED... please use\n\tooutdmaya.common.curve.numCVs instead')
    return curve.numCVs(*args, **kwargs)

def clusterize(*args, **kwargs):
    cmds.warning('ooutdmaya.rigging.core.util.curve.clusterize now DEPRECIATED... please use\n\tooutdmaya.common.curve.clusterize instead')
    return curve.clusterize(*args, **kwargs)
