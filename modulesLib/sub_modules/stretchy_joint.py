try:
    from maya import cmds
    from maya.api import OpenMaya as newOM
    from maya import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_stack()

import sys

path = "C:\\Users\\ffior\\Documents\\GitHub\\openBBlib\\core\\utils"

if path not in sys.path:
    sys.path.append(path)

import groups_utils, vectors_utils

reload(groups_utils)
reload(vectors_utils)

class StretchyJoint():
    def __init__(self, name, start_trf, end_trf, up_trf = None, side = "C", twist_chain = False, number_twist_joints=5):
        """
        """
        self.name = name
        self.start_trf = start_trf
        self.end_trf = end_trf
        self.up_trf = up_trf
        self.side = side
        self.twist_chain = twist_chain
        self.number_twist_joints = number_twist_joints

        self.start_loc = None
        self.end_loc = None
        self.up_loc = None

        self.ik_handle_solver = None

        self.stretchy_chain = []
        
        self.start_distance_attr_val = 0.0

        self.start_twist_grp = None
        self.twist_joitns_chain = []
        
        self.main_grp = "{}_{}_stretchySystem_GRP".format(self.side, self.name)

    def stretchy_system(self):
        """
        """
        # set-up a START locator
        self.start_loc = cmds.spaceLocator(name="{}_{}_startStretchy_LOC".format(self.side, self.name))
        cmds.xform(self.start_loc[0], worldSpace=True, matrix=(cmds.xform(self.start_trf, query=True, worldSpace=True, matrix=True)))
        start_loc_grps = groups_utils.offset_grp(self.start_loc[0])

        # set-up an END locator
        self.end_loc = cmds.spaceLocator(name="{}_{}_endStretchy_LOC".format(self.side, self.name))
        cmds.xform(self.end_loc[0], worldSpace=True, matrix=(cmds.xform(self.end_trf, query=True, worldSpace=True, matrix=True)))
        end_loc_grps = groups_utils.offset_grp(self.end_loc[0])

        # set-up the stretchy chain
        for i in range (0, 2):
            self.stretchy_chain.append(cmds.createNode("joint", name="{}_{}_startStretchy_JNT".format(self.side, self.name)))
            if i !=0:
                cmds.xform(self.stretchy_chain[i], worldSpace=True, matrix=(cmds.xform(self.end_loc[0], query=True, worldSpace=True, matrix=True)))
                cmds.parent(self.stretchy_chain[i], self.stretchy_chain[i-1])
            else:
                cmds.xform(self.stretchy_chain[i], worldSpace=True, matrix=(cmds.xform(self.start_loc[0], query=True, worldSpace=True, matrix=True)))
        
        cmds.joint(self.stretchy_chain[0], edit=True, orientJoint="xyz", secondaryAxisOrient="yup", children=True, zeroScaleOrient=True)
        cmds.joint(self.stretchy_chain[-1], edit=True, orientJoint="none", children=True, zeroScaleOrient=True)

        start_distance_attr = "startLength"
        cmds.addAttr(self.stretchy_chain[0], longName=start_distance_attr, attributeType="double", defaultValue=0.0)
        cmds.setAttr("{}.{}".format(self.stretchy_chain[0], start_distance_attr), edit=True, keyable=True, lock=False)

        actual_distance_attr = "actualLength"
        cmds.addAttr(self.stretchy_chain[0], longName=actual_distance_attr, attributeType="double", defaultValue=0.0)
        cmds.setAttr("{}.{}".format(self.stretchy_chain[0], actual_distance_attr), edit=True, keyable=True, lock=False)

        # set-up an UP locator
        self.up_loc = cmds.spaceLocator(name="{}_{}_upStretchy_LOC".format(self.side, self.name))
        up_loc_grps = groups_utils.offset_grp(self.up_loc[0])
        if self.up_trf != None:
            cmds.xform(up_loc_grps[0], worldSpace=True, matrix=(cmds.xform(self.up_trf, query=True, worldSpace=True, matrix=True)))
        else:
            cmds.xform(up_loc_grps[0], worldSpace=True, matrix=(cmds.xform(self.stretchy_chain[0], query=True, worldSpace=True, matrix=True)))
            ty = vectors_utils.vectors_distance_length(self.stretchy_chain[-1], self.stretchy_chain[0])
            cmds.setAttr("{}.translateY".format(up_loc_grps[1]), ty)

        cmds.parentConstraint(self.start_loc[0], up_loc_grps[0], maintainOffset=True)

        # set-up ikHandle behaviour
        self.ik_handle_solver = cmds.ikHandle(name="{}_{}_rotatePlaneStretchy_IKH".format(self.side, self.name), solver="ikRPsolver", startJoint=self.stretchy_chain[0], endEffector=self.stretchy_chain[-1])
        cmds.parentConstraint(self.start_loc[0], self.stretchy_chain[0], maintainOffset=True)
        cmds.parentConstraint(self.end_loc[0], self.ik_handle_solver[0], maintainOffset=True)
        cmds.poleVectorConstraint(self.up_loc[0], self.ik_handle_solver[0])

        # set-up stretchy feature 
        distance_node = cmds.createNode("distanceBetween", name="{}_{}_distanceStretchy_DSB".format(self.side, self.name))
        cmds.connectAttr("{}Shape.worldMatrix[0]".format(self.start_loc[0]), "{}.inMatrix1".format(distance_node), force=True)
        cmds.connectAttr("{}Shape.worldMatrix[0]".format(self.end_loc[0]), "{}.inMatrix2".format(distance_node), force=True)

        multiply_node = cmds.createNode("multiplyDivide", name="{}_{}_multiplyStretchy_MLD".format(self.side, self.name))
        cmds.setAttr("{}.operation".format(multiply_node), 2)

        self.start_distance_attr_val = cmds.getAttr("{}.distance".format(distance_node))
        cmds.setAttr("{}.{}".format(self.stretchy_chain[0], start_distance_attr), self.start_distance_attr_val)
        
        cmds.connectAttr("{}.distance".format(distance_node), "{}.{}".format(self.stretchy_chain[0], actual_distance_attr), force=True)
        cmds.connectAttr("{}.{}".format(self.stretchy_chain[0], actual_distance_attr), "{}.input1X".format(multiply_node), force=True)
        cmds.connectAttr("{}.{}".format(self.stretchy_chain[0], start_distance_attr), "{}.input2X".format(multiply_node), force=True)

        cmds.connectAttr("{}.outputX".format(multiply_node), "{}.scaleX".format(self.stretchy_chain[0]), force=True)

        return True

    def twist_system(self):
        """
        """
        # set-up start group
        self.start_twist_grp = cmds.group(empty=True, name="{}_{}_startTwist_GRP".format(self.side, self.side))
        cmds.xform(self.start_twist_grp, worldSpace=True, matrix=(cmds.xform(self.stretchy_chain[0], query=True, worldSpace=True, matrix=True)))

        # set-up joint chain
        distance_factor = 0.0

        for i in range(0, self.number_twist_joints):
            unit = float(self.start_distance_attr_val / (self.number_twist_joints - 1))
            jnt = cmds.createNode("joint", name="{}_{}{}_twist_JNT".format(self.side, self.name, i))
            self.twist_joitns_chain.append(jnt)
            cmds.parent(self.twist_joitns_chain[i], self.start_twist_grp)
            if i == 0:
                cmds.xform(self.twist_joitns_chain[i], worldSpace=True, matrix=(cmds.xform(self.start_twist_grp, query=True, worldSpace=True, matrix=True)))
                cmds.makeIdentity(self.twist_joitns_chain[i], apply=True, t=True,  r=True, scale=True, n=False, pn=True)
            else:
                cmds.xform(self.twist_joitns_chain[i], worldSpace=True, matrix=(cmds.xform(self.start_twist_grp, query=True, worldSpace=True, matrix=True)))
                cmds.makeIdentity(self.twist_joitns_chain[i], apply=True, t=True,  r=True, scale=True, n=False, pn=True)
                distance_factor = distance_factor + unit
                if self.side == "L":
                    cmds.setAttr("{}.translateX".format(self.twist_joitns_chain[i]), distance_factor)
                else:
                    cmds.setAttr("{}.translateX".format(self.twist_joitns_chain[i]), distance_factor*(-1))
        
        # aimConstraint -mo -weight 1 -aimVector 1 0 0 -upVector 0 1 0 -worldUpType "object" -worldUpObject locator2;
        cmds.aimConstraint(self.end_loc[0], self.start_twist_grp, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="object", worldUpObject=self.up_loc[0], maintainOffset=True)
        cmds.pointConstraint(self.start_loc[0], self.start_twist_grp, maintainOffset=True)

        # set-up twist feature
        # cmds.orientConstraint(self.end_loc[0], self.twist_joitns_chain[-1], maintainOffset=True)
        mlm_node = cmds.createNode("multMatrix", name="{}_{}_opMatTwist_MLM".format(self.side, self.side))
        dcm_node = cmds.createNode("decomposeMatrix", name="{}_{}_opMatTwist_DCM".format(self.side, self.side))
        qte_node = cmds.createNode("quatToEuler", name="{}_{}_opMatTwist_QTE".format(self.side, self.side))

        cmds.connectAttr("{}.worldMatrix[0]".format(self.end_loc[0]), "{}.matrixIn[0]".format(mlm_node), force=True)
        cmds.connectAttr("{}.worldInverseMatrix[0]".format(self.start_loc[0]), "{}.matrixIn[1]".format(mlm_node), force=True)

        cmds.connectAttr("{}.matrixSum".format(mlm_node), "{}.inputMatrix".format(dcm_node), force=True)
        cmds.connectAttr("{}.outputQuatX".format(dcm_node), "{}.inputQuatX".format(qte_node), force=True)
        cmds.connectAttr("{}.outputQuatW".format(dcm_node), "{}.inputQuatW".format(qte_node), force=True)

        factor = 0.0
        for i in range(0, self.number_twist_joints):
            factor_unit = (1.0/self.number_twist_joints)
            mld_node = cmds.createNode("multiplyDivide", name="{}_{}{}_opMatTwist_MLD".format(self.side, self.side, i))
            cmds.connectAttr("{}.outputRotateX".format(qte_node), "{}.input1X".format(mld_node), force=True)
            cmds.connectAttr("{}.outputX".format(mld_node), "{}.rotateX".format(self.twist_joitns_chain[i]), force=True)

            if i == 0:
                cmds.setAttr("{}.input2X".format(mld_node), 0.0)
            else:
                factor = factor + factor_unit
                cmds.setAttr("{}.input2X".format(mld_node), factor)

        return True

    def run(self):
        self.stretchy_system()
        
        if self.twist_chain:
            self.twist_system()
