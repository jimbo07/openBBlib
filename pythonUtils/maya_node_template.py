import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import math
VERSION = '1.0'

## @brief A node that triggers shapes from of an orientation
class TemplateNode(OpenMayaMPx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0x00000000)

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # the compute function get called once one or more attributes of the node have been changed 
    def compute(self, plug, data):
        return

## @brief Creates the object for Maya.
def creator():
    return OpenMayaMPx.asMPxPtr(TemplateNode())


## @brief Creates the node attributes.
#
def initialize():
    pass


## @brief Initializes the plug-in in Maya.
#
def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'fabio-f', VERSION, 'Any')
    plugin.registerNode('templateNode', TemplateNode.kPluginNodeId, creator, initialize)


## @brief Uninitializes the plug-in in Maya.
#
def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    plugin.deregisterNode(TemplateNode.kPluginNodeId)

