try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

from . import attributes_utils

reload(attributes_utils)

DEBUG_MODE = False

def offset_grps_hierarchy(obj, top_grp_name = "offset", middle_grp_name = "modify"):
    """
    building up a hierarchy of grps on top of the given obj

    Args:

    Returns:
    
    """
    if "CTRL" in obj or "ctrl" in obj:
        grp_offset = cmds.group(empty=True, name="{}_{}_GRP".format(obj[:len(obj)-5], top_grp_name))
        grp_modify = cmds.group(empty=True, name="{}_{}_GRP".format(obj[:len(obj)-5], middle_grp_name))
    else:
        grp_offset = cmds.group(empty=True, name="{}_{}_GRP".format(obj, top_grp_name))
        grp_modify = cmds.group(empty=True, name="{}_{}_GRP".format(obj, middle_grp_name))
    
    align_objs(obj, grp_offset)
    align_objs(obj, grp_modify)
    cmds.parent(obj, grp_modify)
    cmds.parent(grp_modify, grp_offset)
    
    return [grp_offset, grp_modify]


def make_spaces(obj, obj_offset_trs, attribute_name, spaces, naming=None):
    if obj != None or obj != "":
        if obj_offset_trs != "" or obj_offset_trs != None:
            
            if spaces != [] or spaces != None:
                
                name_attr = ""
                if attribute_name != "" or attribute_name != None:
                    name_attr = attribute_name
                else:
                    name_attr = "spaces"
                
                enum_values = ""
                if naming != "" or naming != None:
                    enum_values = ':'.join(naming)
                else:
                    enum_values = ':'.join(spaces)

                if DEBUG_MODE:
                    print naming
                    print enum_values

                attributes_utils.add_enum_attr(obj, name_attr, enum_values)
                pac = cmds.parentConstraint(spaces, obj_offset_trs, maintainOffset=True)
                
                for i, space in enumerate(spaces):
                    for j in range(0, len(spaces)):
                        if j == i:
                            cmds.setDrivenKeyframe(pac, attribute="{}W{}".format(space, i), currentDriver="{}.{}".format(obj, name_attr), driverValue=j, value=1.0)
                        else:
                            cmds.setDrivenKeyframe(pac, attribute="{}W{}".format(space, i), currentDriver="{}.{}".format(obj, name_attr), driverValue=j, value=0.0)

            else:    
                cmds.warning("Please make sure you enter the right spaces objects as a list")
        else:
            cmds.warning("Please make sure you enter the right offset transform where will be applied the constraints")
    else:
        cmds.warning("Please make sure you enter the right object as a string which should has the spaces")

    return True

def align_objs(driver, driven, translation=True, rotation=True):
    """
    """
    if translation == True and rotation == True:
        cmds.xform(driven, worldSpace=True, matrix=(cmds.xform(driver, query=True, worldSpace=True, matrix=True)))
    elif translation == True and rotation == False:
        cmds.xform(driven, worldSpace=True, translation=(cmds.xform(driver, query=True, worldSpace=True, translation=True)))
    elif translation == False and rotation == True:
        cmds.xform(driven, worldSpace=True, rotation=(cmds.xform(driver, query=True, worldSpace=True, rotation=True)))
    else:
        print "translation and rotation"
