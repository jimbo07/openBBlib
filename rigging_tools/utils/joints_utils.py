try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

from . import transforms_utils

def related_clean_joint_chain(main_chain, side, name, full_name = False):
    """
    building a chain of joints based on the one given

    Args:

    Returns:
    
    """
    final_chain = []
    cmds.select(clear=True)
    for i, obj in enumerate(main_chain):

        if DEBUG_MODE:
            print "joint involved : {}".format(obj)

        if full_name:
            jnt = cmds.joint(name="{}_{}_JNT".format(obj[:len(obj)-4], name))
        else:
            jnt = cmds.joint(name="{}_{}{}_JNT".format(side, name, i))
        final_chain.append(jnt)
        transforms_utils.align_objs(obj, jnt)
    cmds.makeIdentity(final_chain[0], apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
    cmds.select(clear=True)
    return final_chain

def duplicate_chain(main_chain, type_chain = 0, name_chain = "duplicated"):
    """
    duplicate the joint chain given as a input and rename it

    Args:

    Returns:

    """
    cmds.select(clear=True)
        
    duplicated_chain = cmds.duplicate(main_chain[0])
    cmds.parent(duplicated_chain[0], world=True)
    
    duplicated_jnts = []
    get_joints_chain(duplicated_chain[0], duplicated_jnts)
    tmp_jnts_chain = rename_chain(string_bit, duplicated_jnts)
    
    jnts_chain = []
    
    for jnt in tmp_jnts_chain:
        if DEBUG_MODE:
            print "{}_JNT".format(jnt[:len(jnt)-(len(string_bit)+5)])
        if "{}_JNT".format(jnt[:len(jnt)-(len(string_bit)+5)]) in main_chain:
            if DEBUG_MODE:
                print "Joints that needs"
                
            jnts_chain.append(jnt)
        else:
            if cmds.objExists(jnt):
                cmds.delete(jnt)
            else:
                print "#--- {} ---# already deleted".format(jnt)
    
    cmds.makeIdentity(jnts_chain[0], apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
    
    return jnts_chain


def rename_chain(string_bit, chain):
    """
    renaming an entire joint chain

    Args:

    Returns:
    
    """
    chain_renamed = []
    reversed_list = chain[::-1]
    print reversed_list
    if reversed_list != [] or reversed_list != None:
        for jnt in reversed_list:
            if cmds.nodeType(jnt) == "joint":
                string_parts = jnt.split("|")
                joint_name = string_parts[-1]
                regex_no_numb = r"\jnt+$"
                matches_no_numb = re.search(regex_no_numb, joint_name)
                regex_numb = r"\jnt+\d+$"
                matches_numb = re.search(regex_numb, joint_name)
                if matches_no_numb:
                    new_jnt_name = joint_name.replace(joint_name[matches_no_numb.start():matches_no_numb.end()], "{}_JNT".format(string_bit))
                    cmds.rename(jnt, new_jnt_name)
                    chain_renamed.append(new_jnt_name)
                elif matches_numb:
                    new_jnt_name = joint_name.replace(joint_name[matches_numb.start():matches_numb.end()], "{}_JNT".format(string_bit))
                    cmds.rename(jnt, new_jnt_name)
                    chain_renamed.append(new_jnt_name)
                else:
                    new_jnt_name = cmds.rename(jnt, "{}{}_JNT".format(joint_name, string_bit))
                    chain_renamed.append(new_jnt_name)
            else:
                print "#--- {} ---# is not a joint nodeType. It'll be skipped".format(jnt)
    
    final_chain = chain_renamed[::-1]
    
    return final_chain

def get_joints_chain(joint_father, joints = []):
    """
    get the entire joint chain hierarchy just passing the father joint

    Args:

    Returns:
    
    """
    if cmds.nodeType(joint_father) == "joint":
        joints.append(joint_father)
        children = cmds.listRelatives(joint_father, children=True, fullPath=True)
        if children == [] or children == None:
            return joints
        else:
            for child in children:
                if cmds.nodeType(child) == "joint": 
                    get_joints_chain(child, joints)
                else:
                    print ("Object in children list not a joint. It'll skipped")
            
    else:
        print ("Wrong type of object passed to the function. It needs to be a joint, and it'll be skipped")


def joint_chain_in_between(name, start_jnt, end_jnt, joint_number, main_axis = "X"):
    """
    creating a straight joint chain all along the two objs given as input

    Args:

    Returns:
    
    """
    joint_chain = []
    if main_axis == "" or main_axis == None:
        x_val = cmds.getAttr("{}.translateX".format(end_jnt))
        y_val = cmds.getAttr("{}.translateY".format(end_jnt))
        z_val = cmds.getAttr("{}.translateZ".format(end_jnt))
        if x_val != 0:
            main_axis = "X"
        elif y_val != 0:
            main_axis = "Y"
        else:
            main_axis = "Z"

    axis_val = cmds.getAttr("{}.translate{}".format(end_jnt, main_axis))
    for i in range(0, joint_number):
        if i == 0:
            jnt = cmds.createNode("joint", name="{}_{}_JNT".format(name, i))
            transforms_utils.align_objs(start_jnt, jnt)
            joint_chain.append(jnt)
        else:
            jnt = cmds.createNode("joint", name="{}_{}_JNT".format(name, i))
            transforms_utils.align_objs(joint_chain[i-1], jnt)
            cmds.parent(jnt, joint_chain[i-1])
            joint_chain.append(jnt)

            factor = axis_val/float(joint_number-1)
            cmds.setAttr("{}.translate{}".format(joint_chain[i], main_axis), factor)
    
    cmds.makeIdentity(joint_chain[0], apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
        
    return joint_chain

