try:
    from maya import cmds
    from maya.api import OpenMaya as newOM
    from maya import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_stack()


def vectors_distance_length(first_obj, second_obj):
    """
    """
    first_pos = cmds.xform(first_obj, query=True, worldSpace=True, translation=True)
    second_pos = cmds.xform(second_obj, query=True, worldSpace=True, translation=True)

    first_vector = OM.MVector(first_pos[0], first_pos[1], first_pos[2])
    second_vector = OM.MVector(second_pos[0], second_pos[1], second_pos[2])

    sub_vector = first_vector - second_vector

    length_sub_vector = sub_vector.length()

    return length_sub_vector