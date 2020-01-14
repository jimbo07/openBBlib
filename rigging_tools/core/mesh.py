'''
Created on 4 Oct 2018

@author: lasse-r
'''

import maya.cmds as cmds
import maya.OpenMaya as om
from ooutdmaya.rigging.core.util import easy


def isMesh(mesh):
    ''' Check if the specified object is a polygon mesh or transform parent of a mesh
    :param mesh str: Object to query
    :return: True if mesh
    :rtype: bool
    '''
    # Check Object Exists
    if not cmds.objExists(mesh): return False
    
    # Check Shape
    if 'transform' in cmds.nodeType(mesh,i=True):
        meshShape = cmds.ls(cmds.listRelatives(mesh, s=True, ni=True, pa=True) or [],type='mesh')
        if not meshShape: return False
        mesh = meshShape[0]
    
    # Check Mesh
    if cmds.objectType(mesh) != 'mesh': return False
    
    # Return Result
    return True


def isOpen(mesh):
    ''' Check if mesh is a closed surface or has boundary components
    :param mesh str: Mesh to check for boundary conditions
    :return: True or False depending
    :rtype: bool
    '''
    # Check Mesh
    if not isMesh(mesh):
        raise Exception('Object {0} is not a valid mesh!!'.format(mesh))
    
    # Get User Selection
    sel = cmds.ls(sl=1)
    
    # Select Mesh
    cmds.select(mesh)
    cmds.polySelectConstraint(mode=3, type=1, where=1)
    boundarySel = cmds.ls(sl=1,fl=1)
    
    # Restore User Selection
    if sel: cmds.select(sel)
    
    # Return Result
    return bool(boundarySel)

    
def getMeshFn(mesh):
    ''' Create an MFnMesh class object from the specified polygon mesh
    :param mesh str: Mesh to create function class for
    :return: MFnMesh for specified poly mesh
    :rtype: class object
    '''
    # Checks
    if not isMesh(mesh): raise Exception('Object '+mesh+' is not a polygon mesh!')
    
    # Get shape
    if cmds.objectType(mesh) == 'transform':
        mesh = cmds.listRelatives(mesh,s=True,ni=True,pa=True)[0]
        
    # Get MFnMesh
    meshPath = easy.getMDagPath(mesh)
    meshFn = om.MFnMesh(meshPath)
    
    # Return result
    return meshFn
