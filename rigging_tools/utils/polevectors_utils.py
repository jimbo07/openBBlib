try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

from . import vectors_utils, transforms_utils, attributes_utils

reload(vectors_utils)
reload(transforms_utils)

DEBUG_MODE = True

def pole_vector_complex_plane(name, root_joint, center_joint, end_joint, amplify_factor_distance = 1):
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
    
    loc_name = "{}_poleVector_LOC".format(name)
    cmds.rename(loc2[0], loc_name)
    
    # polevector distance from leg
    root_joint_vector = vectors_utils.get_MVector_obj(root_joint)
    
    center_joint_vector = vectors_utils.get_MVector_obj(center_joint)
    
    distance_factor = vectors_utils.distance_between(root_joint_vector, center_joint_vector)

    if DEBUG_MODE:
        print loc_name

    cmds.setAttr("{}.translateZ".format(loc_name), (distance_factor * amplify_factor_distance) * (-1))
    
    cmds.parent(loc_name, world=True)
    cmds.delete(grp2)

    grp_name = transforms_utils.offset_grps_hierarchy(loc_name)
    cmds.setAttr("{}.visibility".format(grp_name[0]), 0)
    
    return [loc_name, grp_name[0]]


def pole_vector_simple_plane(chain, factor=0.5):
    """
    returns a worldspace position based on the supplied three joints

    Args:

    Returns:
    
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

def pole_vector_arrow(start_transform, end_transform, name="default", annotation_text=""):
    """
    creating an annotation arrow which will be used commonly for pointing where the poleVector ctrl is
    
    Args:
    
    Returns:
    
    """
    start_position = cmds.xform(start_transform, query=True, worldSpace=True, translation=True)
    tmp_annotation = cmds.annotate(end_transform, text=annotation_text, point=start_position)
    annotationTransform = cmds.listRelatives(tmp_annotation, parent=True)

    annotation = cmds.rename(annotationTransform, name)
    
    cmds.pointConstraint(start_transform, annotation, maintainOffset=True)
    
    cmds.setAttr("{}.overrideEnabled".format(annotation), 1)
    cmds.setAttr("{}.overrideDisplayType".format(annotation), 2)

    return annotation
    
    
def no_flip_pole_vector(name, origin_transform, driver_transform, root_transform, pole_vector_ctrl, pole_vector_offset_grp, spaces, spaces_names, side="C"):
    """
    upgrade the poleVector "system" passed as input with a non flip behavior
    
    Args:
    
    Returns:
    
    """
    ########################## ---- section under test ---- ##########################
    ''''
    no_flip_offset_aiming_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_aiming_offset_GRP".format(side, name))
    no_flip_aiming_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_aiming_GRP".format(side, name))
    cmds.parent(no_flip_aiming_grp, no_flip_offset_aiming_grp)

    no_flip_offset_pelvis_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_pelvis_offset_GRP".format(side, name))
    no_flip_pelvis_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_pelvis_GRP".format(side, name))
    cmds.parent(no_flip_pelvis_grp, no_flip_offset_pelvis_grp)

    transforms_utils.align_objs(origin_transform, no_flip_offset_aiming_grp, True, True)
    cmds.pointConstraint(root_transform, no_flip_offset_pelvis_grp, maintainOffset=False)
    transforms_utils.align_objs(origin_transform, no_flip_offset_pelvis_grp, False, True)
    cmds.pointConstraint(origin_transform, no_flip_offset_aiming_grp, maintainOffset=False)
    
    cmds.aimConstraint(driver_transform, no_flip_offset_aiming_grp, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 0, 1], worldUpObject=no_flip_pelvis_grp, maintainOffset=True)
    cmds.aimConstraint(driver_transform, no_flip_aiming_grp, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 0, 1], worldUpObject=driver_transform, maintainOffset=True)

    spaces.insert(0, no_flip_aiming_grp)
    spaces_names.insert(0, "noFlipGrp")
    transforms_utils.make_spaces(pole_vector_ctrl, pole_vector_offset_grp, "positionScapes", spaces, spaces_names)
    
    # automated poleVector
    cmds.setKeyframe("{}.rotateX".format(no_flip_aiming_grp))
    cmds.setKeyframe("{}.rotateY".format(no_flip_aiming_grp))
    cmds.setKeyframe("{}.rotateZ".format(no_flip_aiming_grp))
    
    attributes_utils.add_float_attr(pole_vector_ctrl, "automatedPoleVector", 0, 10, 0)
    cmds.setDrivenKeyframe(no_flip_aiming_grp, attribute="blendAim1", currentDriver="{}.automatedPoleVector".format(pole_vector_ctrl), driverValue=0.0, value=0.0)
    cmds.setDrivenKeyframe(no_flip_aiming_grp, attribute="blendAim1", currentDriver="{}.automatedPoleVector".format(pole_vector_ctrl), driverValue=10.0, value=1.0)    
    '''
    ###################################################################################
    
    
    no_flip_offset_aiming_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_aiming_offset_GRP".format(side, name))
    no_flip_aiming_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_aiming_GRP".format(side, name))
    cmds.parent(no_flip_aiming_grp, no_flip_offset_aiming_grp)

    no_flip_offset_pelvis_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_pelvis_offset_GRP".format(side, name))
    no_flip_pelvis_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_pelvis_GRP".format(side, name))
    cmds.parent(no_flip_pelvis_grp, no_flip_offset_pelvis_grp)

    # transforms_utils.align_objs(origin_transform, no_flip_offset_aiming_grp, True, True)
    cmds.pointConstraint(root_transform, no_flip_offset_pelvis_grp, maintainOffset=False)
    # transforms_utils.align_objs(origin_transform, no_flip_offset_pelvis_grp, False, True)
    cmds.pointConstraint(origin_transform, no_flip_offset_aiming_grp, maintainOffset=False)
    
    cmds.aimConstraint(driver_transform, no_flip_offset_aiming_grp, aimVector=[0, -1, 0], upVector=[1, 0, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0], worldUpObject=no_flip_pelvis_grp, maintainOffset=True)
    cmds.aimConstraint(driver_transform, no_flip_aiming_grp, aimVector=[0, -1, 0], upVector=[1, 0, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0], worldUpObject=driver_transform, maintainOffset=True)

    spaces.insert(0, no_flip_aiming_grp)
    spaces_names.insert(0, "noFlipGrp")
    transforms_utils.make_spaces(pole_vector_ctrl, pole_vector_offset_grp, "positionScapes", spaces, spaces_names)
    
    # automated poleVector
    cmds.setKeyframe("{}.rotateX".format(no_flip_aiming_grp))
    cmds.setKeyframe("{}.rotateY".format(no_flip_aiming_grp))
    cmds.setKeyframe("{}.rotateZ".format(no_flip_aiming_grp))
    
    attributes_utils.add_float_attr(pole_vector_ctrl, "automatedPoleVector", 0, 10, 0)
    cmds.setDrivenKeyframe(no_flip_aiming_grp, attribute="blendAim1", currentDriver="{}.automatedPoleVector".format(pole_vector_ctrl), driverValue=0.0, value=0.0)
    cmds.setDrivenKeyframe(no_flip_aiming_grp, attribute="blendAim1", currentDriver="{}.automatedPoleVector".format(pole_vector_ctrl), driverValue=10.0, value=1.0)   
    
    return [no_flip_offset_aiming_grp, no_flip_offset_pelvis_grp]
