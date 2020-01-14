try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

from . import dag_node

DEBUG_MODE = True

def get_MVector_obj(obj):
    """
    """
    position_obj = cmds.xform(obj, query=True, worldSpace=True, translation=True)
    vector = OM.MVector(position_obj[0], position_obj[1], position_obj[2])
    
    return vector

def distance_between(first_vector, second_vector):
    """
    """
    sub_mVector = OM.MVector()
    distance = 0.0

    sub_mVector = second_vector - first_vector
    distance = sub_mVector.length()

    return distance
