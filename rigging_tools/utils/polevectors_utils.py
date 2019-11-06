try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

from . import vectors_utils, transforms_utils

reload(vectors_utils)
reload(transforms_utils)

def pole_vector_complex_plane(name, root_joint, center_joint, end_joint):
    """
    building up the system for the poleVector

    Args:

    Returns:
    
    """
    loc1 = cmds.spaceLocator() 
    grp1 = cmds.group(loc1[0])
    
    loc2 = cmds.spaceLocator() 
    grp2 = cmds.group(loc2[0])
    
    cmds.pointConstraint(root_joint, end_joint, grp1, maintainOffset=False)
    cmds.aimConstraint(root_joint, grp1, maintainOffset=False, aim=[0,1,0], u=[0,1,0], wut="scene")
    cmds.pointConstraint(center_joint, loc1[0], maintainOffset=False, sk=["x","z"])
    
    poc = cmds.pointConstraint(center_joint, grp2, maintainOffset=False)
    cmds.aimConstraint(loc1[0], grp2, maintainOffset=False, aim=[0,0,1], u=[0,1,0], wut="scene")

    cmds.delete([grp1, poc[0]])
    
    loc_name = "{}_poleVector_loc".format(name)
    cmds.rename(loc2[0], loc_name)
    
    # polevector distance from leg
    root_joint_vector = vectors_utils.get_MVector_obj(root_joint)
    
    center_joint_vector = vectors_utils.get_MVector_obj(center_joint)
    
    distance_factor = vectors_utils.distance_between(root_joint_vector, center_joint_vector)

    cmds.setAttr("{}.translateZ".format(loc_name), distance_factor * (-1))
    
    cmds.parent(loc_name, world=True)
    cmds.delete(grp2)

    grp_name = transforms_utils.offset_grps_hierarchy(loc_name)
    cmds.setAttr("{}.visibility".format(grp_name[0]), 0)
    
    return [loc_name, grp_name[0]]


def pole_vector_simple_plane(chain, factor=0.5):
    """
    returns a worldspace position based on the supplied three joints
    
    # Example
    loc = cmds.spaceLocator()[0]
    chain = ['jnt_armUpper_left', 'jnt_armLower_left', 'jnt_hand_left']
    pos = poleVectorPos(chain)
    cmds.xform(loc , ws =1 , t= (pos[0], pos[1], pos[2])) 
    """
    start = cmds.xform(chain[0], q=1 , ws=1, t=1)
    mid = cmds.xform(chain[1], q=1, ws=1, t=1)
    end = cmds.xform(chain[2], q=1, ws=1, t=1)
    
    startV = OM.MVector(start[0], start[1], start[2])
    midV = OM.MVector(mid[0], mid[1], mid[2])
    endV = OM.MVector(end[0], end[1], end[2])
    
    startEnd = endV - startV
    startMid = midV - startV
    
    dotP = startMid * startEnd
    proj = float(dotP) / float(startEnd.length())  #
    
    startEndN = startEnd.normal()
    projV = startEndN * proj
    
    arrowV = startMid - projV
    finalV = arrowV + midV
    poleToMid = finalV - midV
    arrowV *= (startEnd.length() / poleToMid.length()) * factor
    finalV = arrowV + midV
    
    return (finalV.x , finalV.y, finalV.z)
