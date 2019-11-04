try:
    from maya import cmds
    from maya.api import OpenMaya as newOM
    from maya import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_stack()


def offset_grp(obj, offset_grp_name = "offset", modify_grp_name = "modify"):
    """
    """
    offset_grp = cmds.group(empty=True, name="{}_offset_GRP".format(obj))
    modify_grp = cmds.group(empty=True, name="{}_modify_GRP".format(obj))
    cmds.parent(modify_grp, offset_grp)

    cmds.xform(offset_grp, worldSpace=True, matrix=(cmds.xform(obj, query=True, worldSpace=True, matrix=True)))

    cmds.parent(obj, modify_grp)

    return [offset_grp, modify_grp]