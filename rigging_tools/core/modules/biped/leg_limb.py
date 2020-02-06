import pprint

from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils, vectors_utils
from ...controls import controller
from ...sub_modules import stretchy_joint, twist_chain


reload(attributes_utils)
reload(controller)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)
reload(stretchy_joint)
reload(twist_chain)
reload(polevectors_utils)
reload(vectors_utils)

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class LegLimb():
    def __init__(
                    self, 
                    name, 
                    main_chain, 
                    root_jnt, 
                    side = "C", 
                    ankle_loc = "",
                    ball_loc = "", 
                    tip_loc = "", 
                    heel_loc = "", 
                    inner_loc = "", 
                    outer_loc = "",
                    twist_chain = False, 
                    central_transform = None,
                    base_control = "baseOffset_CTRL"
                ):
        """
        Class Constructor

        Args:

        Returns:

        """
        self.name = name
        self.main_chain = main_chain        
        self.root_jnt = root_jnt
        self.side = side
        self.ankle_loc = ankle_loc
        self.ball_loc = ball_loc
        self.tip_loc = tip_loc
        self.heel_loc = heel_loc
        self.inner_loc = inner_loc
        self.outer_loc = outer_loc
        self.twist_chain = twist_chain 
        self.central_transform = central_transform
        self.base_control = base_control

        self.world_space_loc = None

        self.driver_chain = []
        self.fk_chain = []
        self.ik_chain = []
        self.foot_chain = []

        self.hip_loc = None    
        self.main_ctrl = None
        self.poleVector_ctrl = None

        self.switch_ctrl = None
        self.switchIKFK_drivers_grp = None

        self.fk_system_objs = []
        self.ik_system_objs = []

        self.ik_system_grp = None
        self.fk_system_grp = None

        self.ik_ctrls_main_grp = "{}_{}_ikControls_GRP".format(self.side, self.name)
        self.fk_ctrls_main_grp = "{}_{}_fkControls_GRP".format(self.side, self.name)

        self.main_grp = "{}_{}_system_GRP".format(self.side, self.name)

    def create_driver_joint_chain(self):
        """
        Creating the drive chain, the ultimate chain of joints that will guide the main skeleleton

        Args:

        Returns:

        """
        self.driver_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "driver", True)
        return self.driver_chain
                   
    def create_locator_poleVector_system(self, name, root_joint, center_joint, end_joint):
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
        cmds.setAttr("{}.translateZ".format(loc_name), -30)
        
        cmds.parent(loc_name, world=True)
        cmds.delete(grp2)
    
        grp_name = transforms_utils.offset_grps_hierarchy(loc_name)
        cmds.setAttr("{}.visibility".format(grp_name[0]), 0)
        
        return [loc_name, grp_name[0]]

    def fk_system(self):
        """
        building up the fk system

        Args:

        Returns:

        """

        driver_ctrls = []
        driver_ctrls_offset_grp = []

        self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)
        self.fk_system_objs.append(self.fk_chain[0])

        for i, jnt in enumerate(self.fk_chain):
            
            if i == (len(self.fk_chain) - 1):
                break
            ctrl = None
            if i != 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, driver_ctrls[i-1], ['v'], '', True, True, False)
            else:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['v'], '', True, True, False)
            driver_ctrls.append(ctrl.get_control())
            driver_ctrls_offset_grp.append(ctrl.get_offset_grp())
            
            cmds.parentConstraint(ctrl.get_control(), jnt, maintainOffset=True)
            cmds.scaleConstraint(ctrl.get_control(), jnt, maintainOffset=True)

        self.fk_system_grp = cmds.group(self.fk_system_objs, name="{}_{}_fkSystem_GRP".format(self.side, self.name))
        cmds.group(empty=True, name=self.fk_ctrls_main_grp)
        transforms_utils.align_objs(self.root_jnt, self.fk_ctrls_main_grp)
        cmds.parent(driver_ctrls_offset_grp[0], self.fk_ctrls_main_grp)
        cmds.parentConstraint(self.root_jnt, self.fk_ctrls_main_grp, maintainOffset=True)
        # scale fix
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.root_jnt, axis), "{}.scale{}".format(self.fk_ctrls_main_grp, axis), force=True)
        self.module_main_grp(self.fk_system_grp)

        return [driver_ctrls, driver_ctrls_offset_grp, self.fk_system_grp]

    def roll_locs_hierarchy(self):
        """
        creating the right hierarchy for dealing with the foot rolls

        Args:

        Returns:

        """
        rolls_grps = []

        old_parent = cmds.listRelatives(self.ankle_loc, parent=True)

        transforms_utils.align_objs(self.main_chain[2], self.ankle_loc)

        ankle_roll_offset_grps = transforms_utils.offset_grps_hierarchy(self.ankle_loc)
        rolls_grps.append(ankle_roll_offset_grps)
        ball_roll_offset_grps = transforms_utils.offset_grps_hierarchy(self.ball_loc)
        rolls_grps.append(ball_roll_offset_grps)
        tip_roll_offset_grps = transforms_utils.offset_grps_hierarchy(self.tip_loc)
        rolls_grps.append(tip_roll_offset_grps)
        heel_roll_offset_grps = transforms_utils.offset_grps_hierarchy(self.heel_loc)
        rolls_grps.append(heel_roll_offset_grps)
        inner_roll_offset_grps = transforms_utils.offset_grps_hierarchy(self.inner_loc)
        rolls_grps.append(inner_roll_offset_grps)
        outer_roll_offset_grps = transforms_utils.offset_grps_hierarchy(self.outer_loc)
        rolls_grps.append(outer_roll_offset_grps)

        cmds.parent(ankle_roll_offset_grps[0], self.ball_loc)
        cmds.parent(ball_roll_offset_grps[0], self.outer_loc)
        cmds.parent(outer_roll_offset_grps[0], self.inner_loc)
        cmds.parent(inner_roll_offset_grps[0], self.tip_loc)
        cmds.parent(tip_roll_offset_grps[0], self.heel_loc)

        main_rolls_grp = cmds.group(empty=True, name="{}_{}_rollsSystem_GRP".format(self.side, self.name))
        transforms_utils.align_objs(self.root_jnt, main_rolls_grp)
        cmds.parentConstraint(self.root_jnt, main_rolls_grp, maintainOffset=True)
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.root_jnt, axis), "{}.scale{}".format(main_rolls_grp, axis), force=True)
        
        cmds.parent(heel_roll_offset_grps[0], main_rolls_grp)
        
        rolls_grps.append(main_rolls_grp)

        cmds.delete(old_parent)

        return [rolls_grps]

    def foot_roll_system(self, rools_data):
        """
        building up the foot rolls system

        Args:

        Returns:

        """
        # reversing the chain
        tmp_foot_chain = [self.main_chain[2], self.main_chain[3], self.main_chain[4]]
        self.foot_chain = joints_utils.related_clean_joint_chain(tmp_foot_chain, self.side, "footRoll", True)

        # ik handles
        ball_ik_handle = cmds.ikHandle(name="{}_{}_ballRoll_IKH".format(self.side, self.name), solver="ikSCsolver", startJoint=self.foot_chain[0], endEffector=self.foot_chain[1])
        cmds.parent(ball_ik_handle[0], self.ball_loc)
        tip_ik_handle = cmds.ikHandle(name="{}_{}_tipRoll_IKH".format(self.side, self.name), solver="ikSCsolver", startJoint=self.foot_chain[1], endEffector=self.foot_chain[2])    
        cmds.parent(tip_ik_handle[0], self.outer_loc)

        # foot rools attribute
        attributes_utils.add_separator(self.main_ctrl.get_control(), "footAttributes")
        ball_roll_attr = "ballRoll"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), ball_roll_attr)
        tip_roll_attr = "tipRoll"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), tip_roll_attr)
        inner_roll_attr = "innerSideRoll"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), inner_roll_attr)
        outer_roll_attr = "outerSideRoll"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), outer_roll_attr)
        heel_roll_attr = "heelRoll"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), heel_roll_attr)

        cmds.connectAttr("{}.{}".format(self.main_ctrl.get_control(), ball_roll_attr), "{}.rotateX".format(self.ball_loc), force=True)
        cmds.connectAttr("{}.{}".format(self.main_ctrl.get_control(), tip_roll_attr), "{}.rotateX".format(self.tip_loc), force=True)
        cmds.connectAttr("{}.{}".format(self.main_ctrl.get_control(), inner_roll_attr), "{}.rotateZ".format(self.inner_loc), force=True)
        cmds.connectAttr("{}.{}".format(self.main_ctrl.get_control(), outer_roll_attr), "{}.rotateZ".format(self.outer_loc), force=True)
        cmds.connectAttr("{}.{}".format(self.main_ctrl.get_control(), heel_roll_attr), "{}.rotateX".format(self.heel_loc), force=True)

        self.ik_system_objs.append(self.foot_chain[0])

        return True

    def ik_system(self):
        """
        building up the ik system

        Args:

        Returns:
        
        """
        # initial setup for roll locators hierarchy
        rolls_locs_data_tmp = self.roll_locs_hierarchy()
        self.ik_system_objs.append(rolls_locs_data_tmp[0][-1])

        driver_ctrls_offset_grp = []        

        self.ik_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ik", True)

        self.ik_system_objs.append(self.ik_chain[0])

        # creating ctrl for shoulder/hip and his grps   ####  circleFourArrows  ####
        self.hip_loc = cmds.spaceLocator(name="{}_{}_hipPosition_LOC".format(self.side, self.name))
        hip_loc_off_grp = cmds.group(empty=True, name="{}_{}_hipPosition_offset_GRP".format(self.side, self.name))
        transforms_utils.align_objs(self.main_chain[0],  self.hip_loc)
        transforms_utils.align_objs(self.root_jnt,  hip_loc_off_grp)
        cmds.parent(self.hip_loc[0], hip_loc_off_grp)

        cmds.parentConstraint(self.root_jnt, hip_loc_off_grp, maintainOffset=True)
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.root_jnt, axis), "{}.scale{}".format(hip_loc_off_grp, axis), force=True)

        self.ik_system_objs.append(hip_loc_off_grp)


        self.main_ctrl = controller.Control("{}_main_ik".format(self.main_chain[2][:len(self.main_chain[2])-4]), 5.0, 'cube', self.main_chain[2], '', '', ['s', 'v'], '', True, True, False)
        self.main_ctrl.make_dynamic_pivot("{}_main_ik".format(self.main_chain[2][:len(self.main_chain[2])-4]), 2.5, self.main_ctrl.get_control(), self.main_ctrl.get_control())
        driver_ctrls_offset_grp.append(self.main_ctrl.get_offset_grp())

        transforms_utils.align_objs(self.main_ctrl.get_control(), rolls_locs_data_tmp[0][0][0], True, False)

        # the --- rolls_locs_data_tmp[0][2] --- is the heel offset group
        cmds.parentConstraint(self.main_ctrl.get_control(), rolls_locs_data_tmp[0][3][0], maintainOffset=True)

        # set-up a foot roll system
        self.foot_roll_system(rolls_locs_data_tmp[0][3][0])
        cmds.parentConstraint(self.ik_chain[2], self.foot_chain[0], maintainOffset=True)
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.ik_chain[2], axis), "{}.scale{}".format(self.foot_chain[0], axis), force=True)

        ik_rotate_plane_handle = cmds.ikHandle(name="{}_{}_rotatePlane_IKH".format(self.side, self.name), solver="ikRPsolver", startJoint=self.ik_chain[0], endEffector=self.ik_chain[2])

        self.ik_system_objs.append(ik_rotate_plane_handle[0])

        cmds.parentConstraint(self.hip_loc[0], self.ik_chain[0], maintainOffset=True)

        cmds.parentConstraint(self.ankle_loc, ik_rotate_plane_handle[0], maintainOffset=True)

        cmds.orientConstraint(self.ankle_loc, self.ik_chain[2], maintainOffset=True)

        # building pole vector system
        ik_poleVector = self.create_locator_poleVector_system("{}_{}_ikPVSystem".format(self.side, self.name), self.ik_chain[0], self.ik_chain[1], self.ik_chain[2])
        
        cmds.poleVectorConstraint(ik_poleVector[0], ik_rotate_plane_handle[0])

        self.poleVector_ctrl = controller.Control("{}_{}_poleVector_ik".format(self.side, self.name), 5.0, 'sphere', '', '', '', ['r', 's', 'v'], '', True, True, False)
        
        driver_ctrls_offset_grp.append(self.poleVector_ctrl.get_offset_grp())

        transforms_utils.align_objs(ik_poleVector[0], self.poleVector_ctrl.get_offset_grp(), True, False)

        cmds.parent(ik_poleVector[1], self.poleVector_ctrl.get_control())

        # no flip Ik ---> pole vector system
        no_flip_fix_grps = polevectors_utils.no_flip_pole_vector(self.name, self.ik_chain[0], self.main_ctrl.get_control(), self.root_jnt, self.poleVector_ctrl.get_control(), self.poleVector_ctrl.get_offset_grp(), [self.world_space_loc[0]], ["world"], self.side)
        scale_fix_no_flip_off_grp = cmds.group(empty=True, name="{}_{}_scaleFix_noFlipIK_aiming_offset_GRP".format(self.side, self.name))
        transforms_utils.align_objs(self.root_jnt, scale_fix_no_flip_off_grp)
        cmds.parentConstraint(self.root_jnt, scale_fix_no_flip_off_grp, maintainOffset=True)
        cmds.parent(no_flip_fix_grps[0], scale_fix_no_flip_off_grp)
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.root_jnt, axis), "{}.scale{}".format(scale_fix_no_flip_off_grp, axis), force=True)
            cmds.connectAttr("{}.scale{}".format(self.root_jnt, axis), "{}.scale{}".format(no_flip_fix_grps[1], axis), force=True)

        self.ik_system_objs.extend([scale_fix_no_flip_off_grp, no_flip_fix_grps[1]])
        

        # adding the poleVector arrow
        annotation = polevectors_utils.pole_vector_arrow(self.ik_chain[1], self.poleVector_ctrl.get_control(), name="{}_{}_poleVector_ANT".format(self.side, self.name))
        driver_ctrls_offset_grp.append(annotation)
        
        # parent constraint the foot part of the ik_chain to the reverse chain
        cmds.parentConstraint(self.foot_chain[1], self.ik_chain[3], maintainOffset=True)
        cmds.parentConstraint(self.foot_chain[2], self.ik_chain[4], maintainOffset=True)

        # clean the scene
        # self.ik_system_objs.append(self.ik_spring_chain[0])
        self.ik_system_objs.append(self.ik_chain[0])
        
        self.ik_system_grp = cmds.group(empty=True, name="{}_{}_ikSystem_GRP".format(self.side, self.name))
        cmds.parent(self.ik_system_objs, self.ik_system_grp)
        cmds.group(empty=True, name=self.ik_ctrls_main_grp)
        transforms_utils.align_objs(self.root_jnt, self.ik_ctrls_main_grp)
        cmds.parent(driver_ctrls_offset_grp, self.ik_ctrls_main_grp)
        
        cmds.parentConstraint(self.base_control, self.ik_ctrls_main_grp, maintainOffset=True)

        self.module_main_grp(self.ik_system_grp)        
        
        return True

    def ik_stretch_update(self, module_scale_attr):
        """
        """

        stretch_attr = "stretchyLeg"
        attributes_utils.add_separator(self.main_ctrl.get_control(), name_sep="stretchyAttribute", by_name=False)
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), stretch_attr, 0, 1, 0, keyable=True, lock=False)

        start_loc = cmds.spaceLocator(name="{}_{}_startStretch_LOC".format(self.side, self.name))
        end_loc = cmds.spaceLocator(name="{}_{}_endStretch_LOC".format(self.side, self.name))

        cmds.parentConstraint(self.hip_loc, start_loc, maintainOffset=False)
        cmds.parentConstraint(self.main_ctrl.get_control(), end_loc, maintainOffset=False)

        hip = OM.MVector(cmds.xform(self.main_chain[0], q=True, ws=True, t=True))
        knee = OM.MVector(cmds.xform(self.main_chain[1], q=True, ws=True, t=True))
        ankle = OM.MVector(cmds.xform(self.main_chain[2], q=True, ws=True, t=True))

        hip_knee_dist = vectors_utils.distance_between(hip, knee)
        knee_ankle_dist = vectors_utils.distance_between(knee, ankle)

        max_dist = hip_knee_dist + knee_ankle_dist

        dist_between_node = cmds.createNode("distanceBetween", name="{}_{}_stretchUpdate_DSB")
        cmds.connectAttr("{}.worldMatrix[0]".format(start_loc[0]), "{}.inMatrix1".format(dist_between_node), force=True)
        cmds.connectAttr("{}.worldMatrix[0]".format(end_loc[0]), "{}.inMatrix2".format(dist_between_node), force=True)

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
        cmds.connectAttr("{}.{}".format(self.main_ctrl.get_control(), stretch_attr), "{}.blender".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.outColorR".format(stretch_condition_node), "{}.color1R".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Y".format(self.central_transform, module_scale_attr), "{}.color1G".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Z".format(self.central_transform, module_scale_attr), "{}.color1B".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}X".format(self.central_transform, module_scale_attr), "{}.color2R".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Y".format(self.central_transform, module_scale_attr), "{}.color2G".format(stretch_blend_node), force=True)
        cmds.connectAttr("{}.{}Z".format(self.central_transform, module_scale_attr), "{}.color2B".format(stretch_blend_node), force=True)

        # connection between blend node and the IK chain
        cmds.connectAttr("{}.outputR".format(stretch_blend_node), "{}.scaleX".format(self.ik_chain[0]), force=True)
        cmds.connectAttr("{}.outputR".format(stretch_blend_node), "{}.scaleX".format(self.ik_chain[1]), force=True)
        cmds.connectAttr("{}.outputG".format(stretch_blend_node), "{}.scaleY".format(self.ik_chain[0]), force=True)
        cmds.connectAttr("{}.outputG".format(stretch_blend_node), "{}.scaleY".format(self.ik_chain[1]), force=True)
        cmds.connectAttr("{}.outputB".format(stretch_blend_node), "{}.scaleZ".format(self.ik_chain[0]), force=True)
        cmds.connectAttr("{}.outputB".format(stretch_blend_node), "{}.scaleZ".format(self.ik_chain[1]), force=True)

        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.{}{}".format(self.central_transform, module_scale_attr, axis), "{}.scale{}".format(self.ik_chain[2], axis), force=True)
            cmds.connectAttr("{}.{}{}".format(self.central_transform, module_scale_attr, axis), "{}.scale{}".format(self.ik_ctrls_main_grp, axis), force=True)

        return [start_loc[0], end_loc[0]]

    def chains_connection(self):
        """
        create the connections between the two systems (ik/fk) and driver with those two the final chain

        Args:

        Returns:

        """
        grp_objs = []

        if self.central_transform == None or self.central_transform == "":
            central_transform_name = "{}_{}_central_LOC".format(self.side, self.name)
            name_attr = "{}_{}_switch_IK_FK".format(self.side, self.name)
        else:
            central_transform_name = self.central_transform
            name_attr = "{}_{}_switch_IK_FK".format(self.side, self.name)

        if not cmds.objExists(central_transform_name):
            loc = cmds.spaceLocator(name=central_transform_name)
            self.central_transform = loc[0]

            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0, keyable=True, lock=False)
        
        elif cmds.objExists("{}.{}".format(self.central_transform, name_attr)):
            print "central_transform already present"
        
        else:
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0, keyable=True, lock=False)

        module_scale_attr = "moduleScale"
        attributes_utils.add_vector_attr(self.central_transform, module_scale_attr, keyable=True, lock=False)
        cmds.setAttr("{}.{}X".format(self.central_transform, module_scale_attr), 1)
        cmds.setAttr("{}.{}Y".format(self.central_transform, module_scale_attr), 1)
        cmds.setAttr("{}.{}Z".format(self.central_transform, module_scale_attr), 1)

        for i, jnt in enumerate(self.main_chain):
            driver_pac = cmds.parentConstraint([self.fk_chain[i], self.ik_chain[i]], self.driver_chain[i], maintainOffset=True)
            cmds.setAttr("{}.interpType".format(driver_pac[0]), 2)

            driver_scale_blnd_node = cmds.createNode("blendColors", name="{}_{}_scaleDriverJNT_{}_BLC".format(self.side, self.name, i))
            cmds.connectAttr("{}.{}".format(self.central_transform, name_attr), "{}.blender".format(driver_scale_blnd_node), force=True)
            for channel in [["X", "R"], ["Y", "G"], ["Z", "B"]]:
                cmds.connectAttr("{}.scale{}".format(self.ik_chain[i], channel[0]), "{}.color2{}".format(driver_scale_blnd_node, channel[1]), force=True)
                cmds.connectAttr("{}.scale{}".format(self.fk_chain[i], channel[0]), "{}.color1{}".format(driver_scale_blnd_node, channel[1]), force=True)
                cmds.connectAttr("{}.output{}".format(driver_scale_blnd_node, channel[1]), "{}.scale{}".format(self.driver_chain[i], channel[0]), force=True)
                cmds.connectAttr("{}.scale{}".format(self.driver_chain[i], channel[0]), "{}.scale{}".format(jnt, channel[0]), force=True)

            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0.0)

            # cmds.setDrivenKeyframe(driver_scc, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0.0)
            # cmds.setDrivenKeyframe(driver_scc, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=1.0)
            # cmds.setDrivenKeyframe(driver_scc, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
            # cmds.setDrivenKeyframe(driver_scc, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=0.0)

            cmds.setDrivenKeyframe(self.ik_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1)
            cmds.setDrivenKeyframe(self.ik_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=1)

            main_pac = cmds.parentConstraint(self.driver_chain[i], jnt, maintainOffset=True)

        # clean scene
        grp_objs.append(self.central_transform)
        grp_objs.append(self.driver_chain[0])

        self.module_main_grp(grp_objs)

        return [name_attr, module_scale_attr]

    def twist_chain_modules(self):
        """
        adding the twist chain feature calling back the sub-module

        Args:

        Returns:

        """
        # test with new twisty chain
        name_bit_twist_system = self.main_chain[0][2 : len(self.main_chain[0])-4]
        upperLeg_twist = twist_chain.TwistChain(
                                                    "{}_{}".format(self.name, name_bit_twist_system),
                                                    self.main_chain[0],
                                                    self.main_chain[1],
                                                    self.side,
                                                    5,
                                                    self.root_jnt,
                                                    self.main_chain[1],
                                                    [0, 1, 0],
                                                    [0, 1, 0],
                                                    [0, 1, 0],
                                                    [0, 1, 0]
                                                )
        upper_twist_jnt_chain = upperLeg_twist.run()

        for jnt in upper_twist_jnt_chain:
            if cmds.objExists("{}.moduleScaleY".format(self.central_transform)):
                cmds.connectAttr("{}.moduleScaleY".format(self.central_transform), "{}.scaleY".format(jnt), force=True)
            else:
                print "scale Y on twist chain skipped"
            if cmds.objExists("{}.moduleScaleZ".format(self.central_transform)):
                cmds.connectAttr("{}.moduleScaleZ".format(self.central_transform), "{}.scaleZ".format(jnt), force=True)
            else:
                print "scale Z on twist chain skipped"

        name_bit_twist_system = self.main_chain[1][2 : len(self.main_chain[1])-4]
        lowerLeg_twist = twist_chain.TwistChain(
                                                    "{}_{}".format(self.name, name_bit_twist_system), 
                                                    self.main_chain[1], 
                                                    self.main_chain[2], 
                                                    self.side, 
                                                    5,
                                                    self.main_chain[1],
                                                    self.main_chain[2],
                                                    [0, 1, 0],
                                                    [0, 1, 0],
                                                    [0, 1, 0],
                                                    [0, 1, 0]
                                                )
        lower_twist_jnt_chain = lowerLeg_twist.run()

        for jnt in lower_twist_jnt_chain:
            if cmds.objExists("{}.moduleScaleY".format(self.central_transform)):
                cmds.connectAttr("{}.moduleScaleY".format(self.central_transform), "{}.scaleY".format(jnt), force=True)
            else:
                print "scale Y on twist chain skipped"
            if cmds.objExists("{}.moduleScaleZ".format(self.central_transform)):
                cmds.connectAttr("{}.moduleScaleZ".format(self.central_transform), "{}.scaleZ".format(jnt), force=True)
            else:
                print "scale Z on twist chain skipped"

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
        run the module and get the final result

        Args:

        Returns:

        """

        print("###--- Module BipedLeg --- START ---###")

        # temporary
        self.world_space_loc = cmds.spaceLocator(name="{}_{}_worldSpace_LOC".format(self.side, self.name))
        world_space_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.world_space_loc[0])
        cmds.parentConstraint(self.root_jnt, world_space_loc_offset_grp[0], maintainOffset=True)

        self.module_main_grp(world_space_loc_offset_grp[0])

        mel.eval("ikSpringSolver;")

        self.create_driver_joint_chain()

        self.fk_system()
        self.ik_system()

        chains_connection_ops = self.chains_connection()

        # ik stretchy update
        stretch_update = self.ik_stretch_update(chains_connection_ops[1])
        cmds.parent(stretch_update, self.ik_system_grp)

        if self.twist_chain:
            self.twist_chain_modules()

        # Temporary switch control
        self.switch_ctrl = controller.Control("{}_{}_switch".format(self.side, self.name), 3.0, 's', self.main_chain[-1], '', '', ['t', 'r', 's', 'v'], '', True, True, False)
        cmds.parentConstraint(self.main_chain[-1], self.switch_ctrl.get_offset_grp(), maintainOffset=True)

        switch_attr = "switch_IK_FK"
        attributes_utils.add_float_attr(self.switch_ctrl.get_control(), switch_attr, 0, 1, 0, keyable=True, lock=False)
        cmds.connectAttr("{}.{}".format(self.switch_ctrl.get_control(), switch_attr), "{}.{}_{}_switch_IK_FK".format(self.central_transform, self.side, self.name), force=True)

        self.switch_ctrls_grp = "switchIKFK_drivers_GRP"
        if cmds.objExists(self.switch_ctrls_grp):
            cmds.parent(self.switch_ctrl.get_offset_grp(), self.switch_ctrls_grp)
        else:
            cmds.group(empty=True, name=self.switch_ctrls_grp)
            cmds.parent(self.switch_ctrl.get_offset_grp(), self.switch_ctrls_grp)

        # TEMPORARY CONNECTION - scale fix
        for axis in ["X", "Y", "Z"]:
            cmds.connectAttr("{}.scale{}".format(self.root_jnt, axis), "{}.{}{}".format(self.central_transform, chains_connection_ops[1], axis), force=True)

        # Temporary stuff
        if cmds.objExists("rig_GRP"):
            cmds.parent(self.main_grp, "rig_GRP")
        
        if cmds.objExists("controls_GRP"):
            cmds.parent([self.ik_ctrls_main_grp, self.fk_ctrls_main_grp, self.switch_ctrls_grp], "controls_GRP")
