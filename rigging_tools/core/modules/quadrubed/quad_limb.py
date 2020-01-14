from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils
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

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class QuadLimb():
    def __init__(
                    self, 
                    name, 
                    main_chain, 
                    root_jnt, 
                    side = "C", 
                    scapula_joints = [], 
                    ankle_loc = "",
                    ball_loc = "", 
                    tip_loc = "", 
                    heel_loc = "", 
                    inner_loc = "", 
                    outer_loc = "",
                    twist_chain = False, 
                    central_transform = None
                ):

        self.name = name
        self.side = side

        self.root_jnt = root_jnt

        self.main_chain = main_chain        
        self.driver_chain = []
        self.fk_chain = []
        self.ik_spring_chain = []
        self.ik_rotate_plane_chain = []
        self.foot_chain = []
        
        self.scapula_joints = scapula_joints
        self.twist_chain = twist_chain 

        self.ankle_loc = ankle_loc
        self.ball_loc = ball_loc
        self.tip_loc = tip_loc
        self.heel_loc = heel_loc
        self.inner_loc = inner_loc
        self.outer_loc = outer_loc

        self.central_transform = central_transform
        self.world_space_loc = None
        
        self.start_ctrl = None    
        self.end_ctrl = None
        self.main_ctrl = None
        self.poleVector_ctrl = None
        self.scapula_ctrl = None

        self.scapula_ctrls_grp = None

        self.fk_system_objs = []
        self.ik_system_objs = []

        self.ik_system_grp = None
        self.fk_system_grp = None

        self.ik_ctrls_main_grp = "{}_{}_ikControls_GRP".format(self.side, self.name)
        self.fk_ctrls_main_grp = "{}_{}_fkControls_GRP".format(self.side, self.name)

        self.switch_ctrl = None
        self.switch_ctrls_grp = ""

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
    '''
    def no_flip_IK(self, pole_vector_offset_grp):
        """
        building up a system of transforms which helps the flipping issue of the ik systems

        Args:

        Returns:
        
        """
        no_flip_offset_aiming_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_aiming_offset_GRP".format(self.side, self.name))
        no_flip_aiming_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_aiming_GRP".format(self.side, self.name))
        cmds.parent(no_flip_aiming_grp, no_flip_offset_aiming_grp)

        no_flip_offset_pelvis_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_pelvis_offset_GRP".format(self.side, self.name))
        no_flip_pelvis_grp = cmds.group(empty=True, name="{}_{}_noFlipIK_pelvis_GRP".format(self.side, self.name))
        cmds.parent(no_flip_pelvis_grp, no_flip_offset_pelvis_grp)

        cmds.parentConstraint(self.root_jnt, no_flip_offset_pelvis_grp, maintainOffset=False)

        cmds.pointConstraint(self.ik_rotate_plane_chain[0], no_flip_offset_aiming_grp, maintainOffset=False)
        cmds.aimConstraint(self.ankle_loc, no_flip_offset_aiming_grp, aimVector=[0, -1, 0], upVector=[1, 0, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0], worldUpObject=no_flip_pelvis_grp, maintainOffset=False)
        cmds.aimConstraint(self.ankle_loc, no_flip_aiming_grp, aimVector=[0, -1, 0], upVector=[1, 0, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0], worldUpObject=self.ankle_loc, maintainOffset=False)

        follow_pac = cmds.parentConstraint([no_flip_aiming_grp, self.world_space_loc[0]], pole_vector_offset_grp, maintainOffset=True)

        name_attr = "spaces"
        cmds.addAttr(self.poleVector_ctrl.get_control(), longName=name_attr, attributeType='enum', enumName="foot:world:")
        cmds.setAttr("{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), keyable=True, lock=False)

        cmds.setDrivenKeyframe(follow_pac, attribute="{}W0".format(no_flip_aiming_grp), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=0, value=1.0)
        cmds.setDrivenKeyframe(follow_pac, attribute="{}W0".format(no_flip_aiming_grp), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=1, value=0.0)
        cmds.setDrivenKeyframe(follow_pac, attribute="{}W1".format(self.world_space_loc[0]), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=0, value=0.0)
        cmds.setDrivenKeyframe(follow_pac, attribute="{}W1".format(self.world_space_loc[0]), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=1, value=1.0)        

        return [no_flip_offset_aiming_grp, no_flip_offset_pelvis_grp]
    '''
    def fk_system(self):
        """
        building up the fk system

        Args:

        Returns:

        """

        driver_ctrls = []
        driver_ctrls_offset_grp = []

        # grp_objs = []

        self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)
        self.fk_system_objs.append(self.fk_chain[0])

        for i, jnt in enumerate(self.fk_chain):
            
            if i == (len(self.fk_chain) - 1):
                break
            ctrl = None
            if i != 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, driver_ctrls[i-1], ['s', 'v'], '', True, True, False)
            else:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
            driver_ctrls.append(ctrl.get_control())
            driver_ctrls_offset_grp.append(ctrl.get_offset_grp())
            
            cmds.parentConstraint(ctrl.get_control(), jnt, maintainOffset=True)
            
        # clean scene
        # grp_objs.append(driver_ctrls_offset_grp[0])
        # grp_objs.append(self.fk_chain[0])

        self.fk_system_grp = cmds.group(self.fk_system_objs, name="{}_{}_fkSystem_GRP".format(self.side, self.name))
        cmds.group(driver_ctrls_offset_grp[0], name=self.fk_ctrls_main_grp)
        
        self.module_main_grp(self.fk_system_grp)

        # TEMPORARY --- constraint start ctrl to his root
        cmds.parentConstraint(self.root_jnt, driver_ctrls_offset_grp[0], maintainOffset=True)

        return [driver_ctrls, driver_ctrls_offset_grp, self.fk_system_grp]

    def roll_locs_hierarchy(self):
        """
        creating the right hierarchy for dealing with the foot rolls

        Args:

        Returns:

        """
        rolls_grps = []

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

        rolls_grp = cmds.group(empty=True, name="{}_{}_rolls_GRP".format(self.side, self.name))
        cmds.parent(ankle_roll_offset_grps[0], self.ball_loc)
        cmds.parent(ball_roll_offset_grps[0], self.outer_loc)
        cmds.parent(outer_roll_offset_grps[0], self.inner_loc)
        cmds.parent(inner_roll_offset_grps[0], self.tip_loc)
        cmds.parent(tip_roll_offset_grps[0], self.heel_loc)
        cmds.parent(heel_roll_offset_grps[0], rolls_grp)

        return [rolls_grps, rolls_grp]

    def foot_roll_system(self, rools_data):
        """
        building up the foot rolls system

        Args:

        Returns:

        """
        # reversing the chain
        tmp_foot_chain = [self.main_chain[3], self.main_chain[4], self.main_chain[5]]
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
        self.ik_system_objs.append(rolls_locs_data_tmp[0][3][0])

        driver_ctrls_offset_grp = []        

        self.ik_spring_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ik_spring", True)
        self.ik_rotate_plane_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ik_rotate_plane", True)

        self.ik_system_objs.extend([self.ik_spring_chain[0], self.ik_rotate_plane_chain[0]])

        # creating ctrl for shoulder/hip and his grps   ####  circleFourArrows  ####
        self.start_ctrl = controller.Control("{}_start_ik".format(self.main_chain[0][:len(self.main_chain[0])-4]), 5.0, 'circleFourArrows', self.main_chain[0], "", '', ['r', 's', 'v'], '', True, True, False)
        # self.start_ctrl = ctrl.get_control()
        # start_ctrl_offset_grp = ctrl.get_offset_grp()
        driver_ctrls_offset_grp.append(self.start_ctrl.get_offset_grp())

        # creating ctrls for ankle/wrist rotation/translation and his grps
        self.end_ctrl = controller.Control("{}_end_ik".format(self.main_chain[3][:len(self.main_chain[3])-4]), 5.0, 'sphere', self.main_chain[3], self.main_chain[3], '', ['t', 's', 'v'], '', True, True, False)
        # self.end_ctrl = ctrl.get_control()
        # end_ctrl_offset_grp = ctrl.get_offset_grp()
        driver_ctrls_offset_grp.append(self.end_ctrl.get_offset_grp())

        self.main_ctrl = controller.Control("{}_main_ik".format(self.main_chain[3][:len(self.main_chain[3])-4]), 5.0, 'cube', '', '', '', ['s', 'v'], '', True, True, False)
        self.main_ctrl.make_dynamic_pivot("{}_main_ik".format(self.main_chain[3][:len(self.main_chain[3])-4]), 2.5, self.main_ctrl.get_control(), self.main_ctrl.get_control())
        # self.main_ctrl = ctrl.get_control()
        # main_ctrl_offset_grp = ctrl.get_offset_grp()
        driver_ctrls_offset_grp.append(self.main_ctrl.get_offset_grp())

        transforms_utils.align_objs(self.main_chain[3], self.main_ctrl.get_offset_grp(), True, False)
        transforms_utils.align_objs(self.main_ctrl.get_control(), rolls_locs_data_tmp[0][0][0], True, False)

        # the --- rolls_locs_data_tmp[0][2] --- is the heel offset group
        cmds.parentConstraint(self.main_ctrl.get_control(), rolls_locs_data_tmp[0][3][0], maintainOffset=True)

        # set-up a foot roll system
        self.foot_roll_system(rolls_locs_data_tmp)
        cmds.parentConstraint(self.ik_spring_chain[3], self.foot_chain[0], maintainOffset=True)

        # building transforms system for aiming/hock the ankle/wrist
        top_grp_aim = cmds.group(empty=True, name="{}_{}_hockPosition_GRP".format(self.side, self.name))
        aiming_grp_aim = cmds.group(empty=True, name="{}_{}_hockAiming_GRP".format(self.side, self.name))
        
        aim_up_vector_offset_grp = cmds.group(empty=True, name="{}_{}_hockUpVector_offset_GRP".format(self.side, self.name))
        aim_up_vector = cmds.group(empty=True, name="{}_{}_hockUpVector_GRP".format(self.side, self.name))

        cmds.parent(aiming_grp_aim, top_grp_aim)
        cmds.parent(aim_up_vector, aim_up_vector_offset_grp)

        self.ik_system_objs.append(top_grp_aim)
        self.ik_system_objs.append(aim_up_vector_offset_grp)

        transforms_utils.align_objs(self.ik_spring_chain[3], aim_up_vector_offset_grp)

        cmds.parentConstraint(self.ankle_loc, aim_up_vector_offset_grp, maintainOffset=True)
        
        transforms_utils.align_objs(self.ik_spring_chain[3], top_grp_aim)

        cmds.delete(cmds.aimConstraint(self.ik_spring_chain[2], top_grp_aim, worldUpType="objectrotation", worldUpVector=[0, 0, 1], maintainOffset=False, worldUpObject=aim_up_vector))

        # top_grp_override_aim = cmds.group(empty=True, name="{}_{}_hockPosition_override_grp".format(self.side, self.name))
        aiming_grp_override_aim = cmds.group(empty=True, name="{}_{}_hockAiming_override_GRP".format(self.side, self.name))

        self.ik_system_objs.append(aiming_grp_override_aim)

        # cmds.parent(aiming_grp_override_aim, top_grp_override_aim)
        transforms_utils.align_objs(self.ik_spring_chain[2], aiming_grp_override_aim)

        cmds.parentConstraint(self.ankle_loc, aiming_grp_override_aim, maintainOffset=True)

        cmds.pointConstraint(self.ankle_loc, top_grp_aim, maintainOffset=True)
        aim_const = cmds.aimConstraint([aiming_grp_override_aim, self.ik_spring_chain[2]], aiming_grp_aim, worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=aim_up_vector)

        # building the ik system
        ik_spring_handle = cmds.ikHandle(name="{}_{}_springChain_IKH".format(self.side, self.name), solver="ikSpringSolver", startJoint=self.ik_spring_chain[0], endEffector=self.ik_spring_chain[3])    
        ik_rotate_plane_handle = cmds.ikHandle(name="{}_{}_rotatePlaneChain_IKH".format(self.side, self.name), solver="ikRPsolver", startJoint=self.ik_rotate_plane_chain[0], endEffector=self.ik_rotate_plane_chain[2])

        self.ik_system_objs.append(ik_spring_handle[0])
        self.ik_system_objs.append(ik_rotate_plane_handle[0])

        # adding hock attribute
        attributes_utils.add_separator(self.main_ctrl.get_control(), "hockAttributes")
        name_attr = "hockFollow"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), name_attr, 0.0, 10.0, 5.0)
        cmds.setDrivenKeyframe(aim_const, attribute="{}W0".format(aiming_grp_override_aim), currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=0.0, value=1.0)
        cmds.setDrivenKeyframe(aim_const, attribute="{}W0".format(aiming_grp_override_aim), currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=10.0, value=0.0)
        cmds.setDrivenKeyframe(aim_const, attribute="{}W1".format(self.ik_spring_chain[2]), currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(aim_const, attribute="{}W1".format(self.ik_spring_chain[2]), currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)

        # spring bias attributes
        name_attr = "hockUpAngle"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), name_attr, 0.0, 10.0, 5.0)
        cmds.setDrivenKeyframe(ik_spring_handle[0], attribute="springAngleBias[0].springAngleBias_FloatValue", currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(ik_spring_handle[0], attribute="springAngleBias[0].springAngleBias_FloatValue", currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)

        name_attr = "hockBotAngle"
        attributes_utils.add_float_attr(self.main_ctrl.get_control(), name_attr, 0.0, 10.0, 5.0)
        cmds.setDrivenKeyframe(ik_spring_handle[0], attribute="springAngleBias[1].springAngleBias_FloatValue", currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(ik_spring_handle[0], attribute="springAngleBias[1].springAngleBias_FloatValue", currentDriver="{}.{}".format(self.main_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)
        

        # finalizing/constraint section
        cmds.parentConstraint(aiming_grp_aim, self.end_ctrl.get_offset_grp(), maintainOffset=True)

        cmds.parentConstraint(self.start_ctrl.get_control(), self.ik_spring_chain[0], maintainOffset=True)
        cmds.parentConstraint(self.start_ctrl.get_control(), self.ik_rotate_plane_chain[0], maintainOffset=True)

        cmds.parentConstraint(self.end_ctrl.get_control(), ik_rotate_plane_handle[0], maintainOffset=True)
        cmds.parentConstraint(self.ankle_loc, ik_spring_handle[0], maintainOffset=True)

        cmds.orientConstraint(self.ankle_loc, self.ik_rotate_plane_chain[3], maintainOffset=True)
        cmds.aimConstraint(self.ankle_loc, self.ik_rotate_plane_chain[2], maintainOffset=True, worldUpType="objectrotation", worldUpVector=[0, 0, 1], worldUpObject=aim_up_vector)

        # building pole vector system
        ik_spring_pv = polevectors_utils.pole_vector_complex_plane("{}_{}_ikSpring".format(self.side, self.name), self.ik_spring_chain[0], self.ik_spring_chain[1], self.ik_spring_chain[3])
        ik_rotate_plane_pv = polevectors_utils.pole_vector_complex_plane("{}_{}_ikRotatePlane".format(self.side, self.name), self.ik_rotate_plane_chain[0], self.ik_rotate_plane_chain[1], self.ik_rotate_plane_chain[2])
        
        cmds.poleVectorConstraint(ik_spring_pv[0], ik_spring_handle[0])
        cmds.poleVectorConstraint(ik_rotate_plane_pv[0], ik_rotate_plane_handle[0])

        self.poleVector_ctrl = controller.Control("{}_{}_poleVector_ik".format(self.side, self.name), 5.0, 'sphere', '', '', '', ['r', 's', 'v'], '', True, True, False)

        # self.poleVector_ctrl = ctrl.get_control()
        # main_pv_driver_off_grp = ctrl.get_offset_grp()
        
        driver_ctrls_offset_grp.append(self.poleVector_ctrl.get_offset_grp())

        cmds.delete(cmds.pointConstraint([ik_spring_pv[0], ik_rotate_plane_pv[0]], self.poleVector_ctrl.get_offset_grp(), maintainOffset=False))

        cmds.parent([ik_spring_pv[1], ik_rotate_plane_pv[1]], self.poleVector_ctrl.get_control())

        # no flip Ik ---> pole vector system
        # no_flip_fix_grps = self.no_flip_IK(self.poleVector_ctrl.get_offset_grp())
        no_flip_fix_grps = polevectors_utils.no_flip_pole_vector(self.name, self.ik_rotate_plane_chain[0], self.main_ctrl.get_control(), self.root_jnt, self.poleVector_ctrl.get_control(), self.poleVector_ctrl.get_offset_grp(), [self.world_space_loc[0]], ["world"], self.side)
        driver_ctrls_offset_grp.extend(no_flip_fix_grps)

        # parent constraint the foot part of the ik_rotate_plane_chain to the reverse chain
        cmds.parentConstraint(self.foot_chain[1], self.ik_rotate_plane_chain[4], maintainOffset=True)
        cmds.parentConstraint(self.foot_chain[2], self.ik_rotate_plane_chain[5], maintainOffset=True)

        # adding the poleVector arrow
        annotation = polevectors_utils.pole_vector_arrow(self.ik_rotate_plane_chain[1], self.poleVector_ctrl.get_control(), name="{}_{}_poleVector_ANT".format(self.side, self.name))
        driver_ctrls_offset_grp.append(annotation)
        
        # clean the scene
        self.ik_system_objs.append(self.ik_spring_chain[0])
        self.ik_system_objs.append(self.ik_rotate_plane_chain[0])
        
        self.ik_system_grp = cmds.group(self.ik_system_objs, name="{}_{}_ikSystem_GRP".format(self.side, self.name))
        cmds.group(driver_ctrls_offset_grp, name=self.ik_ctrls_main_grp)

        self.module_main_grp(self.ik_system_grp)        

        # TEMPORARY --- constraint start ctrl to his root
        name_attr = "spaces"
        transforms_utils.make_spaces(self.start_ctrl.get_control(), self.start_ctrl.get_offset_grp(), name_attr, [self.world_space_loc[0], self.root_jnt], naming=["world", "root"])
        cmds.setAttr("{}.{}".format(self.start_ctrl.get_control(), name_attr), 1)

        return True

    def scapula_system(self):
        """
        """
        if self.scapula_joints == None or self.scapula_joints == []:
            
            print "###--- Scapula system skipped ---###"
        
        else:
            scap_ik_single_chain = cmds.ikHandle(name="{}_{}_scapula_IKH".format(self.side, self.name), solver="ikSCsolver", startJoint=self.scapula_joints[0], endEffector=self.scapula_joints[1])    
            
            self.scapula_ctrl = controller.Control("{}".format(self.scapula_joints[0][:len(self.scapula_joints[0])-5]), 5.0, 'sphere', "", "", '', ['r', 's', 'v'], '', True, True, False)
            transforms_utils.align_objs(self.scapula_joints[1], self.scapula_ctrl.get_offset_grp())

            # cmds.parentConstraint(self.scapula_ctrl, scap_ik_single_chain[0], maintainOffset=True)
            cmds.parent(scap_ik_single_chain[0], self.scapula_ctrl.get_control())
            cmds.setAttr("{}.visibility".format(scap_ik_single_chain[0]), 0)

            pac_follow = cmds.parentConstraint([self.root_jnt, self.main_chain[0]], self.scapula_ctrl.get_offset_grp(), maintainOffset=True)

            name_attr = "rootFatherFollow"
            attributes_utils.add_float_attr(self.scapula_ctrl.get_control(), name_attr, 0.0, 10.0, 3.0)
            cmds.setDrivenKeyframe(pac_follow, attribute="{}W0".format(self.root_jnt), currentDriver="{}.{}".format(self.scapula_ctrl.get_control(), name_attr), driverValue=0.0, value=1.0)
            cmds.setDrivenKeyframe(pac_follow, attribute="{}W0".format(self.root_jnt), currentDriver="{}.{}".format(self.scapula_ctrl.get_control(), name_attr), driverValue=10.0, value=0.0)
            cmds.setDrivenKeyframe(pac_follow, attribute="{}W1".format(self.main_chain[0]), currentDriver="{}.{}".format(self.scapula_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
            cmds.setDrivenKeyframe(pac_follow, attribute="{}W1".format(self.main_chain[0]), currentDriver="{}.{}".format(self.scapula_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)
            # transforms_utils.make_spaces(self.scapula_ctrl, ctrl.get_offset_grp(), 'spaces', [self.world_space_loc, self.root_jnt, self.main_chain[0]], naming="world:root:father")

            self.scapula_ctrls_grp = cmds.group(empty=True, name="{}_{}_scapControls_GRP".format(self.side, self.name))
            cmds.parent(self.scapula_ctrl.get_offset_grp(), self.scapula_ctrls_grp)
            
        return True

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

            cmds.addAttr(self.central_transform, longName=name_attr, attributeType='enum', enumName="IK:FK:")
            cmds.setAttr("{}.{}".format(self.central_transform, name_attr), keyable=True, lock=False)
        
        elif cmds.objExists("{}.{}".format(self.central_transform, name_attr)):
            print "central_transform already present"
        
        else:
            cmds.addAttr(self.central_transform, longName=name_attr, attributeType='enum', enumName="IK:FK:")
            cmds.setAttr("{}.{}".format(self.central_transform, name_attr), keyable=True, lock=False)


        for i, jnt in enumerate(self.main_chain):
            driver_pac = cmds.parentConstraint([self.fk_chain[i], self.ik_rotate_plane_chain[i]], self.driver_chain[i], maintainOffset=True)

            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_rotate_plane_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_rotate_plane_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0.0)

            cmds.setDrivenKeyframe(self.ik_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.ik_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1)

            main_pac = cmds.parentConstraint(self.driver_chain[i], jnt, maintainOffset=True)

        # clean scene
        grp_objs.append(self.central_transform)
        grp_objs.append(self.driver_chain[0])

        self.module_main_grp(grp_objs)

        return True

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
                                                    [0, 0, 1],
                                                    [0, 1, 0],
                                                    [0, 0, 1]
                                                )
        upperLeg_twist.run()

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
                                                    [0, 0, 1],
                                                    [0, 1, 0],
                                                    [0, 0, 1]
                                                )
        lowerLeg_twist.run()

        name_bit_twist_system = self.main_chain[2][2 : len(self.main_chain[2])-4]
        ankleLeg_twist = twist_chain.TwistChain(
                                                    "{}_{}".format(self.name, name_bit_twist_system), 
                                                    self.main_chain[2], 
                                                    self.main_chain[3], 
                                                    self.side, 
                                                    5,
                                                    self.main_chain[2],
                                                    self.main_chain[3],
                                                    [0, 1, 0],
                                                    [0, 0, 1],
                                                    [0, 1, 0],
                                                    [0, 0, 1]
                                                )
        ankleLeg_twist.run()

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

        print("###--- Module QuadLimb --- START ---###")

        # temporary
        self.world_space_loc = cmds.spaceLocator(name="{}_{}_worldSpace_LOC".format(self.side, self.name))
        world_space_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.world_space_loc[0])
        cmds.parentConstraint(self.root_jnt, world_space_loc_offset_grp[0], maintainOffset=True)

        self.module_main_grp(world_space_loc_offset_grp[0])

        mel.eval("ikSpringSolver;")

        self.create_driver_joint_chain()

        self.fk_system()
        self.ik_system()

        self.chains_connection()

        self.scapula_system()

        if self.twist_chain:
            self.twist_chain_modules()

        # Temporary switch control
        self.switch_ctrl = controller.Control("{}_{}_switch".format(self.side, self.name), 3.0, 's', self.main_chain[-1], '', '', ['t', 'r', 's', 'v'], '', True, True, False)
        cmds.parentConstraint(self.main_chain[-1], self.switch_ctrl.get_offset_grp(), maintainOffset=True)

        switch_attr = "switch_IK_FK"
        attributes_utils.add_enum_attr(self.switch_ctrl.get_control(), switch_attr, "IK:FK:")
        cmds.connectAttr("{}.{}".format(self.switch_ctrl.get_control(), switch_attr), "{}.{}_{}_switch_IK_FK".format(self.central_transform, self.side, self.name), force=True)

        self.switch_ctrls_grp = "switchIKFK_drivers_GRP"
        if cmds.objExists(self.switch_ctrls_grp):
            cmds.parent(self.switch_ctrl.get_offset_grp(), self.switch_ctrls_grp)
        else:
            cmds.group(empty=True, name=self.switch_ctrls_grp)
            cmds.parent(self.switch_ctrl.get_offset_grp(), self.switch_ctrls_grp)

        # Temporary stuff
        if cmds.objExists("rig_GRP"):
            cmds.parent(self.main_grp, "rig_GRP")

        if cmds.objExists("controls_GRP"):
            cmds.parent([self.ik_ctrls_main_grp, self.fk_ctrls_main_grp, self.switch_ctrls_grp], "controls_GRP")
            if self.scapula_joints == [] or self.scapula_joints == None:
                print "###--- No scapula system detected, parenting operation skipped ---###"
            else:
                cmds.parent(self.scapula_ctrls_grp, "controls_GRP")


    def get_name(self):
        """
        function for retrieving the name of the limb

        Args:

        Returns:
        
        """
        return self.name
        
    def get_side(self):
        """
        function for retrieving the side of the limb

        Args:

        Returns:
        
        """
        return self.side
        
    def get_main_chain(self):
        """
        function for retrieving the main_chain which are used for building the module

        Args:

        Returns:
        
        """
        return self.main_chain

    def get_rolls_locs(self):
        """
        function for retrieving the locators used for the rolls

        Args:

        Returns:
        
        """
        return self.rolls_locs

    def set_name(self, name):
        """
        function for set the name of the limb

        Args:

        Returns:
        
        """
        self.name = name
        return self.name
        
    def set_side(self, side):
        """
        function for set the side of the limb

        Args:

        Returns:
        
        """
        self.side = side
        return self.side
        
    def set_rolls_locs(self, locs):
        """
        function for set the list of locators used for rolls

        Args:

        Returns:
        
        """
        self.rolls_locs = locs
        return self.rolls_locs 

    def set_main_chain(self, chain):
        """
        function for set the main chain which is used to build up the limb module

        Args:

        Returns:
        
        """
        self.main_chain = chain
        return self.main_chain 
