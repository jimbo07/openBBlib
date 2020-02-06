from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils, vectors_utils
from ...controls import controller


reload(attributes_utils)
reload(controller)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)
reload(polevectors_utils)
reload(vectors_utils)

import pprint

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class Digit():
    def __init__(self,
                name,
                root_trf,
                meta_joint,
                main_chain,
                switch_ctrl,
                side = "C", 
                central_transform = None):
        """
        """
        self.name = name
        self.root_trf = root_trf
        self.meta_joint = meta_joint
        self.main_chain = main_chain
        self.switch_ctrl = switch_ctrl
        self.side = side
        self.central_transform = central_transform

        self.driver_chain = []
        self.fk_chain = []
        self.ik_primary_chain = []
        self.ik_bendy_chain = []

        self.fk_controls = []
        self.ik_controls = {}

        self.ik_system_grp = "{}_{}_ikSystem_GRP".format(self.side, self.name)
        self.fk_system_grp = "{}_{}_fkSystem_GRP".format(self.side, self.name)

        self.ik_controls_grp = "{}_{}_ikControls_GRP".format(self.side, self.name)
        self.fk_controls_grp = "{}_{}_fkControls_GRP".format(self.side, self.name)

        self.main_grp = "{}_{}_system_GRP".format(self.side, self.name)
    
    def create_driver_chain(self):
        """
        """
        print self.main_chain
        self.driver_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "driver", True)

        self.module_main_grp(self.driver_chain[0])

        return self.driver_chain

    def fk_system(self):
        """
        """
        self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)

        for i, jnt in enumerate(self.fk_chain):
            
            if i == (len(self.fk_chain) - 1):
                break
            ctrl = None
            if i != 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, self.fk_controls[i-1].get_control(), ['s', 'v'], '', True, True, False)
            else:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
            self.fk_controls.append(ctrl)
            
            cmds.parentConstraint(ctrl.get_control(), jnt, maintainOffset=True)
            # scale fix
            cmds.scaleConstraint(ctrl.get_control(), jnt, maintainOffset=True)

        

        if cmds.objExists(self.fk_controls_grp):
            cmds.parentConstraint(self.meta_joint, self.fk_controls_grp, maintainOffset=False)
            # scale fix
            for axis in ["X", "Y", "Z"]:
                cmds.connectAttr("{}.scale{}".format(self.meta_joint, axis), "{}.scale{}".format(self.fk_controls_grp, axis), force=True)
            cmds.parent(self.fk_controls[0].get_offset_grp(), self.fk_controls_grp)
        else:
            cmds.group(empty=True, name=self.fk_controls_grp)
            cmds.parentConstraint(self.meta_joint, self.fk_controls_grp, maintainOffset=False)
            # scale fix
            for axis in ["X", "Y", "Z"]:
                cmds.connectAttr("{}.scale{}".format(self.meta_joint, axis), "{}.scale{}".format(self.fk_controls_grp, axis), force=True)
            cmds.parent(self.fk_controls[0].get_offset_grp(), self.fk_controls_grp)

        # clean up the scene
        if cmds.objExists(self.fk_system_grp):
            cmds.parent(self.fk_chain[0], self.fk_system_grp)
        else:
            cmds.group(empty=True, name=self.fk_system_grp)
            cmds.parent(self.fk_chain[0], self.fk_system_grp)

        self.module_main_grp(self.fk_system_grp)

        return True

    def ik_system(self):
        """
        """
        self.ik_primary_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ikPrimary", True)
        self.ik_bendy_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ikBendy", True)

        # building the IKHandles
        ik_primary_handle = cmds.ikHandle(name="{}_{}_primaryChain_IKH".format(self.side, self.name), solver="ikRPsolver", startJoint=self.ik_primary_chain[0], endEffector=self.ik_primary_chain[-1])
        ik_bendy_handle = cmds.ikHandle(name="{}_{}_bednyChain_IKH".format(self.side, self.name), solver="ikRPsolver", startJoint=self.ik_bendy_chain[0], endEffector=self.ik_bendy_chain[len(self.ik_bendy_chain)-2])

        self.ik_controls = {
            "base_CTRL":None,
            "finger_CTRL":None,
            "bendy_CTRL":None
        }

        # building the base_CTRL / finger_CTRL / bendy_CTRL
        base_CTRL = controller.Control("{}_{}_base_ik".format(self.side, self.name), 1.0, 'pin', self.ik_primary_chain[0], self.ik_primary_chain[0], '', ['s', 'v'], '', True, True, False)
        self.ik_controls["base_CTRL"] = base_CTRL
        finger_CTRL = controller.Control("{}_{}_ik".format(self.side, self.name), 1.0, 'square', self.ik_primary_chain[-1], "", '', ['r', 's', 'v'], '', True, True, False)
        self.ik_controls["finger_CTRL"] = finger_CTRL
        bendy_CTRL = controller.Control("{}_{}_bendy_ik".format(self.side, self.name), 1.0, 'pin', self.ik_bendy_chain[-1], self.ik_bendy_chain[-1], '', ['t', 's', 'v'], '', True, True, False)
        self.ik_controls["bendy_CTRL"] = bendy_CTRL

        if DEBUG_MODE:
            pprint.pprint(self.ik_controls) 

        cmds.parentConstraint(self.ik_controls["base_CTRL"].get_control(), self.ik_primary_chain[0], maintainOffset=True)
        cmds.parentConstraint(self.ik_controls["base_CTRL"].get_control(), self.ik_bendy_chain[0], maintainOffset=True)
        cmds.parentConstraint(self.ik_primary_chain[-1], self.ik_controls["bendy_CTRL"].get_offset_grp(), maintainOffset=True)
        cmds.parentConstraint(self.ik_controls["finger_CTRL"].get_control(), ik_primary_handle[0], maintainOffset=True)
        cmds.parentConstraint(self.ik_controls["bendy_CTRL"].get_control(), ik_bendy_handle[0], maintainOffset=True)


        # poleVectors systems
        polevector_prim_IK = polevectors_utils.pole_vector_complex_plane("{}_{}_primaryIKHandle".format(self.side, self.name), self.ik_primary_chain[0], self.ik_primary_chain[1], self.ik_primary_chain[-1], 1.2)
        polevector_bend_IK = polevectors_utils.pole_vector_complex_plane("{}_{}_bendyIKHandle".format(self.side, self.name), self.ik_bendy_chain[0], self.ik_bendy_chain[1], self.ik_bendy_chain[2], 1.2)
        cmds.poleVectorConstraint(polevector_prim_IK[0], ik_primary_handle[0])
        cmds.poleVectorConstraint(polevector_bend_IK[0], ik_bendy_handle[0])

            # noflip poleVector system
        no_flip_prim_IK_off_grp = cmds.group(empty=True, name="{}_{}_primaryIK_noFlip_offset_GRP".format(self.side, self.name))
        no_flip_bend_IK_off_grp = cmds.group(empty=True, name="{}_{}_bendyIK_noFlip_offset_GRP".format(self.side, self.name))
        no_flip_prim_IK_mod_grp = cmds.group(empty=True, name="{}_{}_primaryIK_noFlip_modify_GRP".format(self.side, self.name))
        cmds.parent(no_flip_prim_IK_mod_grp, no_flip_prim_IK_off_grp)
        no_flip_bend_IK_mod_grp = cmds.group(empty=True, name="{}_{}_bendyIK_noFlip_modify_GRP".format(self.side, self.name))
        cmds.parent(no_flip_bend_IK_mod_grp, no_flip_bend_IK_off_grp)
        
        transforms_utils.align_objs(self.ik_primary_chain[0], no_flip_prim_IK_off_grp)
        cmds.parentConstraint(self.root_trf, no_flip_prim_IK_off_grp, maintainOffset=True)
        cmds.aimConstraint(self.ik_controls["finger_CTRL"].get_control(), no_flip_prim_IK_mod_grp, worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=self.meta_joint, skip=["x"])
        cmds.parent(polevector_prim_IK[1], no_flip_prim_IK_mod_grp)

        transforms_utils.align_objs(self.ik_bendy_chain[0], no_flip_bend_IK_off_grp)
        cmds.parentConstraint(self.root_trf, no_flip_bend_IK_off_grp, maintainOffset=True)
        cmds.aimConstraint(self.ik_controls["finger_CTRL"].get_control(), no_flip_bend_IK_mod_grp, worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=self.meta_joint, skip=["x"])
        cmds.parent(polevector_bend_IK[1], no_flip_bend_IK_mod_grp)

        # twist finger
        for grp in [no_flip_prim_IK_mod_grp, no_flip_bend_IK_mod_grp]:
            orient_cons = cmds.createNode("orientConstraint", name="{}_orientConstraint1".format(grp))
            cmds.parent(orient_cons, grp)
            cmds.connectAttr("{}.constraintRotateX".format(orient_cons), "{}.rotateX".format(grp), force=True)
            cmds.connectAttr("{}.parentInverseMatrix[0]".format(grp), "{}.constraintParentInverseMatrix".format(orient_cons), force=True)
            cmds.connectAttr("{}.rotateOrder".format(grp), "{}.constraintRotateOrder".format(orient_cons), force=True)
            cmds.connectAttr("{}.rotateX".format(self.ik_controls["base_CTRL"].get_control()), "{}.target[0].targetRotateX".format(orient_cons), force=True)
            cmds.connectAttr("{}.parentMatrix[0]".format(self.ik_controls["base_CTRL"].get_control()), "{}.target[0].targetParentMatrix".format(orient_cons), force=True)
            cmds.connectAttr("{}.rotateOrder".format(self.ik_controls["base_CTRL"].get_control()), "{}.target[0].targetRotateOrder".format(orient_cons), force=True)

        # aimConstraint the penultimate  bendyChain's joint to the bendy control
        cmds.aimConstraint(self.ik_controls["bendy_CTRL"].get_control(), self.ik_bendy_chain[len(self.ik_bendy_chain)-2], worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=self.ik_controls["bendy_CTRL"].get_control())

        # TEMPORARY PARENT CONSTRAINT
        cmds.parentConstraint(self.switch_ctrl.get_control(), self.ik_controls["finger_CTRL"].get_offset_grp(), maintainOffset=True)
        

        # clean up the scene
        if cmds.objExists(self.ik_system_grp):
            cmds.parent([self.ik_bendy_chain[0], self.ik_primary_chain[0], ik_primary_handle[0], ik_bendy_handle[0], no_flip_prim_IK_off_grp, no_flip_bend_IK_off_grp], self.ik_system_grp)

        else:
            cmds.group(empty=True, name=self.ik_system_grp)
            cmds.parent([self.ik_bendy_chain[0], self.ik_primary_chain[0], ik_primary_handle[0], ik_bendy_handle[0], no_flip_prim_IK_off_grp, no_flip_bend_IK_off_grp], self.ik_system_grp)

        self.module_main_grp(self.ik_system_grp)

        # clean the scene up
        if cmds.objExists(self.ik_controls_grp):
            transforms_utils.align_objs(self.meta_joint, self.ik_controls_grp)
            cmds.parentConstraint(self.meta_joint, self.ik_controls_grp, maintainOffset=True)

            for axis in ["X", "Y", "Z"]:
                cmds.connectAttr("{}.scale{}".format(self.meta_joint, axis), "{}.scale{}".format(self.ik_controls_grp, axis), force=True)
            cmds.parent(self.ik_controls["base_CTRL"].get_offset_grp(), self.ik_controls_grp)
            cmds.parent(self.ik_controls["finger_CTRL"].get_offset_grp(), self.ik_controls_grp)
            cmds.parent(self.ik_controls["bendy_CTRL"].get_offset_grp(), self.ik_controls_grp)
        else:
            cmds.group(empty=True, name=self.ik_controls_grp)
            transforms_utils.align_objs(self.meta_joint, self.ik_controls_grp)
            cmds.parentConstraint(self.meta_joint, self.ik_controls_grp, maintainOffset=True)

            for axis in ["X", "Y", "Z"]:
                cmds.connectAttr("{}.scale{}".format(self.meta_joint, axis), "{}.scale{}".format(self.ik_controls_grp, axis), force=True) 
            cmds.parent(self.ik_controls["base_CTRL"].get_offset_grp(), self.ik_controls_grp)
            cmds.parent(self.ik_controls["finger_CTRL"].get_offset_grp(), self.ik_controls_grp)
            cmds.parent(self.ik_controls["bendy_CTRL"].get_offset_grp(), self.ik_controls_grp)

        '''
        if cmds.objExists(self.ik_controls_master_grp):
            cmds.parent([self.ik_controls[key]["base_CTRL"].get_offset_grp(), self.ik_controls[key]["finger_CTRL"].get_offset_grp(), self.ik_controls[key]["bendy_CTRL"].get_offset_grp()], self.ik_controls_master_grp)
        else:
            cmds.group(empty=True, name=self.ik_controls_master_grp)
            cmds.parent([self.ik_controls[key]["base_CTRL"].get_offset_grp(), self.ik_controls[key]["finger_CTRL"].get_offset_grp(), self.ik_controls[key]["bendy_CTRL"].get_offset_grp()], self.ik_controls_master_grp)
        '''
        return True

    def ik_stretch_update(self):
        """
        """

        module_scale_attr = "moduleScale"
        attributes_utils.add_vector_attr(self.central_transform, module_scale_attr, keyable=True, lock=False)
        cmds.setAttr("{}.{}X".format(self.central_transform, module_scale_attr), 1)
        cmds.setAttr("{}.{}Y".format(self.central_transform, module_scale_attr), 1)
        cmds.setAttr("{}.{}Z".format(self.central_transform, module_scale_attr), 1)

        stretch_attr = "stretchyFinger"
        attributes_utils.add_separator(self.ik_controls["finger_CTRL"].get_control(), name_sep="stretchyAttribute", by_name=False)
        attributes_utils.add_float_attr(self.ik_controls["finger_CTRL"].get_control(), stretch_attr, 0, 1, 0, keyable=True, lock=False)

        start_loc = cmds.spaceLocator(name="{}_{}_startStretch_LOC".format(self.side, self.name))
        end_loc = cmds.spaceLocator(name="{}_{}_endStretch_LOC".format(self.side, self.name))

        cmds.parentConstraint(self.ik_controls["base_CTRL"].get_control(), start_loc, maintainOffset=False)
        cmds.parentConstraint(self.ik_controls["finger_CTRL"].get_control(), end_loc, maintainOffset=False)

        first_phalanges = OM.MVector(cmds.xform(self.main_chain[0], q=True, ws=True, t=True))
        second_phalanges = OM.MVector(cmds.xform(self.main_chain[1], q=True, ws=True, t=True))
        third_phalanges = OM.MVector(cmds.xform(self.main_chain[2], q=True, ws=True, t=True))
        fourth_phalanges = OM.MVector(cmds.xform(self.main_chain[3], q=True, ws=True, t=True))

        first_second_dist = vectors_utils.distance_between(first_phalanges, second_phalanges)
        second_third_dist = vectors_utils.distance_between(second_phalanges, third_phalanges)
        third_fourth_dist = vectors_utils.distance_between(third_phalanges, fourth_phalanges)

        max_dist = first_second_dist + second_third_dist + third_fourth_dist

        dist_between_node = cmds.createNode("distanceBetween", name="{}_{}_stretchUpdate_DSB".format(self.side, self.name))
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.translate{}".format(start_loc[0], axis), "{}.point1{}".format(dist_between_node, axis), force=True)
            cmds.connectAttr("{}.translate{}".format(end_loc[0], axis), "{}.point2{}".format(dist_between_node, axis), force=True)

        scale_compensate_max_dist_node = cmds.createNode("multiplyDivide", name="{}_{}_normalizeMaxDist_stretchUpdate_MLD".format(self.side, self.name))
        normalize_dist_node = cmds.createNode("multiplyDivide", name="{}_{}_stretchUpdate_MLD".format(self.side, self.name))
        cmds.setAttr("{}.operation".format(normalize_dist_node), 2)
        scale_compensate_dist_node = cmds.createNode("multiplyDivide", name="{}_{}_normalizeDist_stretchUpdate_MLD".format(self.side, self.name))
        stretch_condition_node = cmds.createNode("condition", name="{}_{}_stretchUpdate_CND".format(self.side, self.name))
        cmds.setAttr("{}.operation".format(stretch_condition_node), 2)
        stretch_blend_node = cmds.createNode("blendColors", name="{}_{}_stretchUpdate_BLC".format(self.side, self.name))

        # scale compensate multiply divide connection attributes
        cmds.setAttr("{}.input1X".format(scale_compensate_max_dist_node), max_dist)
        cmds.connectAttr("{}.{}X".format(self.central_transform, module_scale_attr), "{}.input2X".format(scale_compensate_max_dist_node), force=True)

        # stretch update connection attribute
        cmds.connectAttr("{}.distance".format(dist_between_node), "{}.input1X".format(normalize_dist_node), force=True)
        cmds.connectAttr("{}.outputX".format(scale_compensate_max_dist_node), "{}.input2X".format(normalize_dist_node), force=True)

        # scale compensate distance node conenction attribute
        cmds.connectAttr("{}.{}X".format(self.central_transform, module_scale_attr), "{}.input2X".format(scale_compensate_dist_node), force=True)
        cmds.connectAttr("{}.outputX".format(normalize_dist_node), "{}.input1X".format(scale_compensate_dist_node), force=True)

        # condition node connection attribute
        cmds.connectAttr("{}.outputX".format(normalize_dist_node), "{}.firstTerm".format(stretch_condition_node), force=True)
        cmds.setAttr("{}.secondTerm".format(stretch_condition_node), 1.0)
        cmds.connectAttr("{}.{}X".format(self.central_transform, module_scale_attr), "{}.colorIfFalseR".format(stretch_condition_node), force=True)
        cmds.connectAttr("{}.outputX".format(scale_compensate_dist_node), "{}.colorIfTrueR".format(stretch_condition_node), force=True)

        # connection scale to blend node
        cmds.connectAttr("{}.{}".format(self.ik_controls["finger_CTRL"].get_control(), stretch_attr), "{}.blender".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.outColorR".format(stretch_condition_node), "{}.color1R".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Y".format(self.central_transform, module_scale_attr), "{}.color1G".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Z".format(self.central_transform, module_scale_attr), "{}.color1B".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}X".format(self.central_transform, module_scale_attr), "{}.color2R".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Y".format(self.central_transform, module_scale_attr), "{}.color2G".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Z".format(self.central_transform, module_scale_attr), "{}.color2B".format(stretch_blend_node), force=True)

        # connection between blend node and the IK chain
        for i in range(0, len(self.main_chain)):
            cmds.connectAttr("{}.outputR".format(stretch_blend_node), "{}.scaleX".format(self.ik_bendy_chain[i]), force=True)
            cmds.connectAttr("{}.outputR".format(stretch_blend_node), "{}.scaleX".format(self.ik_primary_chain[i]), force=True)
            cmds.connectAttr("{}.outputG".format(stretch_blend_node), "{}.scaleY".format(self.ik_bendy_chain[i]), force=True)
            cmds.connectAttr("{}.outputG".format(stretch_blend_node), "{}.scaleY".format(self.ik_primary_chain[i]), force=True)
            cmds.connectAttr("{}.outputB".format(stretch_blend_node), "{}.scaleZ".format(self.ik_bendy_chain[i]), force=True)
            cmds.connectAttr("{}.outputB".format(stretch_blend_node), "{}.scaleZ".format(self.ik_primary_chain[i]), force=True)

        return [start_loc[0], end_loc[0], module_scale_attr]

    def chains_connection(self):
        """
        create the connections between the two systems (ik/fk) and driver with those two the final chain

        Args:

        Returns:

        """
        name_attr = ""
        if self.central_transform == None or self.central_transform == "":
            central_transform_name = "{}_{}_central_LOC".format(self.side, self.name)
            name_attr = "{}_{}_switch_IK_FK".format(self.side, self.name)
        else:
            central_transform_name = self.central_transform
            name_attr = "{}_{}_switch_IK_FK".format(self.side, self.name)

        if not cmds.objExists(central_transform_name):
            loc = cmds.spaceLocator(name=central_transform_name)
            self.central_transform = loc[0]
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0)
        
        elif cmds.objExists("{}.{}".format(self.central_transform, name_attr)):
            print "central_transform already present"

        else:
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0)

        self.module_main_grp(self.central_transform)
        # cmds.parent(self.central_transform, self.master_system_grp)

        for i, jnt in enumerate(self.main_chain):
            driver_pac = cmds.parentConstraint([self.fk_chain[i], self.ik_bendy_chain[i]], self.driver_chain[i], maintainOffset=True)
            cmds.setAttr("{}.interpType".format(driver_pac[0]), 2)

            if DEBUG_MODE:
                print
                print "{}.{}".format(self.name, name_attr)
                print

            driver_scale_blnd_node = cmds.createNode("blendColors", name="{}_{}_scaleDriverJNT_{}_BLC".format(self.side, self.name, i))
            cmds.connectAttr("{}.{}".format(self.central_transform, name_attr), "{}.blender".format(driver_scale_blnd_node), force=True)
            for channel in [["X", "R"], ["Y", "G"], ["Z", "B"]]:
                cmds.connectAttr("{}.scale{}".format(self.ik_bendy_chain[i], channel[0]), "{}.color2{}".format(driver_scale_blnd_node, channel[1]), force=True)
                cmds.connectAttr("{}.scale{}".format(self.fk_chain[i], channel[0]), "{}.color1{}".format(driver_scale_blnd_node, channel[1]), force=True)
                cmds.connectAttr("{}.output{}".format(driver_scale_blnd_node, channel[1]), "{}.scale{}".format(self.driver_chain[i], channel[0]), force=True)
                cmds.connectAttr("{}.scale{}".format(self.driver_chain[i], channel[0]), "{}.scale{}".format(jnt, channel[0]), force=True)

            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_bendy_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_bendy_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0.0)

            cmds.setDrivenKeyframe(self.ik_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.ik_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0)
            cmds.setDrivenKeyframe(self.fk_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.fk_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1)

            main_pac = cmds.parentConstraint(self.driver_chain[i], jnt, maintainOffset=True)

        return True


    def module_main_grp(self, list_objs):
        """
        re-group all things related to the internal system of the module in one main group

        Args:

        Returns:

        """
        if cmds.objExists(self.main_grp):
            cmds.parent(list_objs, self.main_grp)
        else:
            cmds.group(list_objs, name=self.main_grp)

        cmds.setAttr("{}.visibility".format(self.main_grp), 0)
        
        return self.main_grp

    def run(self):
        """
        """

        self.create_driver_chain()

        self.fk_system()
        self.ik_system()

        self.chains_connection()

        # ik stretchy update
        stretch_update = self.ik_stretch_update()
        cmds.parent([stretch_update[0], stretch_update[1]], self.ik_system_grp)

        # TEMPORARY CONNECTION
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.root_trf, axis), "{}.{}{}".format(self.central_transform, stretch_update[2], axis), force=True)

        return [self.fk_controls, self.ik_controls, self.central_transform, self.ik_controls_grp, self.fk_controls_grp, self.main_grp]
