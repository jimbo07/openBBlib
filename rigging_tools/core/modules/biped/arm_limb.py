from ...controls import controller
from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils
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

class ArmLimb():
    def __init__(
                    self, 
                    name, 
                    main_chain,
                    root_jnt,
                    clavicle_jnt,
                    pelvis_ctrl = "",
                    side = "C", 
                    twist_chain = False, 
                    central_transform = None
                ):
        """
        Class Constructor

        Args:

        Returns:

        """
        self.name = name
        self.main_chain = main_chain
        self.root_jnt = root_jnt
        self.clavicle_jnt = clavicle_jnt
        self.pelvis_ctrl = pelvis_ctrl,
        self.side = side
        self.twist_chain = twist_chain 
        self.central_transform = central_transform
        
        self.world_space_loc = None

        self.driver_chain = []
        self.fk_chain = []
        self.ik_chain = []
        
        self.hand_ik_ctrl = None
        self.poleVector_ctrl = None
        self.shoulder_ctrl = None

        self.fk_controls = []

        self.clavicle_ctrl = None

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

        cmds.pointConstraint(self.ik_chain[0], no_flip_offset_aiming_grp, maintainOffset=False)
        cmds.aimConstraint(self.hand_ik_ctrl.get_control(), no_flip_offset_aiming_grp, aimVector=[0, -1, 0], upVector=[1, 0, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0], worldUpObject=no_flip_pelvis_grp, maintainOffset=False)
        cmds.aimConstraint(self.hand_ik_ctrl.get_control(), no_flip_aiming_grp, aimVector=[0, -1, 0], upVector=[1, 0, 0], worldUpType="objectrotation", worldUpVector=[1, 0, 0], worldUpObject=self.hand_ik_ctrl.get_control(), maintainOffset=False)

        follow_pac = cmds.parentConstraint([no_flip_aiming_grp, self.world_space_loc[0]], pole_vector_offset_grp, maintainOffset=True)

        name_attr = "spaces"
        cmds.addAttr(self.poleVector_ctrl.get_control(), longName=name_attr, attributeType='enum', enumName="foot:world:")
        cmds.setAttr("{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), keyable=True, lock=False)

        cmds.setDrivenKeyframe(follow_pac, attribute="{}W0".format(no_flip_aiming_grp), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=0, value=1.0)
        cmds.setDrivenKeyframe(follow_pac, attribute="{}W0".format(no_flip_aiming_grp), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=1, value=0.0)
        cmds.setDrivenKeyframe(follow_pac, attribute="{}W1".format(self.world_space_loc[0]), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=0, value=0.0)
        cmds.setDrivenKeyframe(follow_pac, attribute="{}W1".format(self.world_space_loc[0]), currentDriver="{}.{}".format(self.poleVector_ctrl.get_control(), name_attr), driverValue=1, value=1.0)        

        return [no_flip_offset_aiming_grp, no_flip_offset_pelvis_grp]

    def fk_system(self):
        """
        building up the fk system

        Args:

        Returns:

        """

        self.fk_controls = []
        
        self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)
        self.fk_system_objs.append(self.fk_chain[0])

        for i, jnt in enumerate(self.fk_chain):
            
            if i == (len(self.fk_chain) - 1):
                break
            ctrl = None
            if i != 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, self.fk_controls[i-1].get_control(), ['s', 'v'], '', True, True, False)
            elif i == 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
            else:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
            self.fk_controls.append(ctrl)
            
            cmds.parentConstraint(ctrl.get_control(), jnt, maintainOffset=True)

        self.fk_system_grp = cmds.group(self.fk_system_objs, name="{}_{}_fkSystem_GRP".format(self.side, self.name))
        cmds.group(self.fk_controls[0].get_offset_grp(), name=self.fk_ctrls_main_grp)
        self.module_main_grp(self.fk_system_grp)

        return True



    def ik_system(self):
        """
        building up the ik system

        Args:

        Returns:
        
        """

        driver_ctrls_offset_grp = []        

        self.ik_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ik", True)

        self.ik_system_objs.append(self.ik_chain[0])

        self.hand_ik_ctrl = controller.Control("{}_main_ik".format(self.main_chain[2][:len(self.main_chain[2])-4]), 5.0, 'cube', self.main_chain[2], '', '', ['s', 'v'], '', True, True, False)
        self.hand_ik_ctrl.make_dynamic_pivot("{}_main_ik".format(self.main_chain[2][:len(self.main_chain[2])-4]), 2.5, self.hand_ik_ctrl.get_control(), self.hand_ik_ctrl.get_control())
        driver_ctrls_offset_grp.append(self.hand_ik_ctrl.get_offset_grp())

        ik_rotate_plane_handle = cmds.ikHandle(name="{}_{}_rotatePlane_IKH".format(self.side, self.name), solver="ikRPsolver", startJoint=self.ik_chain[0], endEffector=self.ik_chain[2])

        self.ik_system_objs.append(ik_rotate_plane_handle[0])

        cmds.parentConstraint(self.hand_ik_ctrl.get_control(), ik_rotate_plane_handle[0], maintainOffset=True)

        cmds.orientConstraint(self.hand_ik_ctrl.get_control(), self.ik_chain[2], maintainOffset=True)

        # building pole vector system
        ik_poleVector = polevectors_utils.pole_vector_complex_plane("{}_{}_ikPVSystem".format(self.side, self.name), self.ik_chain[0], self.ik_chain[1], self.ik_chain[2])
        
        cmds.poleVectorConstraint(ik_poleVector[0], ik_rotate_plane_handle[0])

        self.poleVector_ctrl = controller.Control("{}_{}_poleVector_ik".format(self.side, self.name), 5.0, 'sphere', '', '', '', ['r', 's', 'v'], '', True, True, False)
        
        driver_ctrls_offset_grp.append(self.poleVector_ctrl.get_offset_grp())

        transforms_utils.align_objs(ik_poleVector[0], self.poleVector_ctrl.get_offset_grp(), True, False)

        cmds.parent(ik_poleVector[1], self.poleVector_ctrl.get_control())

        # no flip Ik ---> pole vector system
        # no_flip_fix_grps = polevectors_utils.no_flip_pole_vector(self.name, self.ik_chain[0], self.hand_ik_ctrl.get_control(), self.root_jnt, self.poleVector_ctrl.get_control(), self.poleVector_ctrl.get_offset_grp(), [self.world_space_loc[0]], ["world"], self.side)
        # self.ik_system_objs.extend(no_flip_fix_grps)
        # no_flip_fix_grps = self.no_flip_IK(self.poleVector_ctrl.get_offset_grp())
        # self.ik_system_objs.extend(no_flip_fix_grps)

        # adding the poleVector arrow
        annotation = polevectors_utils.pole_vector_arrow(self.ik_chain[1], self.poleVector_ctrl.get_control(), name="{}_{}_poleVector_ANT".format(self.side, self.name))
        driver_ctrls_offset_grp.append(annotation)
        
        # clean the scene
        self.ik_system_objs.append(self.ik_chain[0])
        
        self.ik_system_grp = cmds.group(self.ik_system_objs, name="{}_{}_ikSystem_GRP".format(self.side, self.name))
        cmds.group(driver_ctrls_offset_grp, name=self.ik_ctrls_main_grp)

        self.module_main_grp(self.ik_system_grp)        
        
        return True
    
    def clavicle_shoulder_system(self):
        """
        building up an auto-clavicle system

        Args:

        Returns:

        """

        self.shoulder_ctrl = controller.Control("{}_start_ik".format(self.main_chain[0][:len(self.main_chain[0])-4]), 5.0, 'circleFourArrows', self.main_chain[0], self.main_chain[0], '', ['r', 's', 'v'], '', True, True, False)

        self.clavicle_ctrl = controller.Control("{}".format(self.clavicle_jnt[:len(self.clavicle_jnt)-4]), 5.0, 'pin', self.clavicle_jnt, self.clavicle_jnt, '', ['s', 'v'], '', True, True, False)
        cmds.parentConstraint(self.clavicle_ctrl.get_control(), self.clavicle_jnt, maintainOffset=True)
        cmds.parentConstraint(self.clavicle_ctrl.get_control(), self.ik_chain[0], maintainOffset=True)

        cmds.parentConstraint(self.clavicle_ctrl.get_control(), self.fk_controls[0].get_offset_grp(), maintainOffset=True)

        # temporary constraint with the root space --- should abe attached trgough more spaces
        cmds.parentConstraint(self.root_jnt, self.clavicle_ctrl.get_offset_grp(), maintainOffset=True)
        
        # attribute related to the clavicle follow
        name_attr="follow"
        attributes_utils.add_float_attr(self.clavicle_ctrl.get_control(), name_attr, min_val=0, max_val=10, def_val=5)

        # Temporary fix for the flipping issue of the clavicle/shoulder --- it shouldn't really work like that :P
        if self.side == "L":
            clav_aim_cs = cmds.aimConstraint( self.shoulder_ctrl.get_control(), self.clavicle_ctrl.get_modify_grp(), maintainOffset=True, weight=1, aimVector=[-1, 0, 0], upVector=[0, -1, 0])
        else:
            clav_aim_cs = cmds.aimConstraint( self.shoulder_ctrl.get_control(), self.clavicle_ctrl.get_modify_grp(), maintainOffset=True, weight=1, aimVector=[1, 0, 0], upVector=[0, 1, 0])
        

        mul_div_node = cmds.createNode("multiplyDivide", name="{}_{}_clavicleShoulder_system_mld".format(self.side, self.name))

        cmds.setDrivenKeyframe(mul_div_node, attribute="input2X", currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(mul_div_node, attribute="input2X", currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)
        cmds.setDrivenKeyframe(mul_div_node, attribute="input2Y", currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(mul_div_node, attribute="input2Y", currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)
        cmds.setDrivenKeyframe(mul_div_node, attribute="input2Z", currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(mul_div_node, attribute="input2Z", currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)

        cmds.connectAttr("{}.constraintRotateX".format(clav_aim_cs[0]), "{}.input1X".format(mul_div_node), force=True)
        cmds.connectAttr("{}.constraintRotateY".format(clav_aim_cs[0]), "{}.input1Y".format(mul_div_node), force=True)
        cmds.connectAttr("{}.constraintRotateZ".format(clav_aim_cs[0]), "{}.input1Z".format(mul_div_node), force=True)

        cmds.connectAttr("{}.outputX".format(mul_div_node), "{}.rotateX".format(self.clavicle_ctrl.get_modify_grp()), force=True)
        cmds.connectAttr("{}.outputY".format(mul_div_node), "{}.rotateY".format(self.clavicle_ctrl.get_modify_grp()), force=True)
        cmds.connectAttr("{}.outputZ".format(mul_div_node), "{}.rotateZ".format(self.clavicle_ctrl.get_modify_grp()), force=True)

        # attribute related to the shoulder follow
        name_attr="follow"
        attributes_utils.add_float_attr(self.shoulder_ctrl.get_control(), name_attr, min_val=0, max_val=10, def_val=2)

        # follow feature for the shoulder control --- chest/hand_ik
        follow_loc = cmds.spaceLocator(name="{}_{}_shoulderFollowWrist_LOC".format(self.side, self.name))
        cmds.pointConstraint(self.hand_ik_ctrl.get_control(), follow_loc[0], maintainOffset=False)
        cmds.parent(follow_loc[0], self.main_grp)
        should_parent_const = []
        if self.pelvis_ctrl != "":
            should_parent_const = cmds.parentConstraint([follow_loc[0], self.root_jnt], self.shoulder_ctrl.get_offset_grp(), maintainOffset=True)
        else:
            cmds.parentConstraint(self.pelvis_ctrl, self.shoulder_ctrl.get_offset_grp(), maintainOffset=True)
            should_parent_const = cmds.parentConstraint([follow_loc[0], self.root_jnt], self.shoulder_ctrl.get_modify_grp(), maintainOffset=True)

        cmds.setDrivenKeyframe(should_parent_const[0], attribute="{}W0".format(follow_loc[0]), currentDriver="{}.{}".format(self.shoulder_ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(should_parent_const[0], attribute="{}W0".format(follow_loc[0]), currentDriver="{}.{}".format(self.shoulder_ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)
        cmds.setDrivenKeyframe(should_parent_const[0], attribute="{}W1".format(self.root_jnt), currentDriver="{}.{}".format(self.shoulder_ctrl.get_control(), name_attr), driverValue=0.0, value=1.0)
        cmds.setDrivenKeyframe(should_parent_const[0], attribute="{}W1".format(self.root_jnt), currentDriver="{}.{}".format(self.shoulder_ctrl.get_control(), name_attr), driverValue=10.0, value=0.0)

        # clean scene
        self.clav_shoul_grp = cmds.group(empty=True, name="{}_{}_clavicleSystem_GRP".format(self.side, self.name))
        cmds.parent([self.clavicle_ctrl.get_offset_grp(), self.shoulder_ctrl.get_offset_grp()], self.clav_shoul_grp)

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
            driver_pac = cmds.parentConstraint([self.fk_chain[i], self.ik_chain[i]], self.driver_chain[i], maintainOffset=True)

            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0.0)

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
        callback the twist chain sub-module for creating the twist chain between limb bits

        Args:

        Returns:

        """
        # test with new twisty chain
        name_bit_twist_system = self.main_chain[0][2 : len(self.main_chain[0])-4]
        upperArm_twist = twist_chain.TwistChain(
                                                    "{}_{}".format(self.name, name_bit_twist_system),
                                                    self.main_chain[0],
                                                    self.main_chain[1],
                                                    self.side,
                                                    5,
                                                    self.clavicle_jnt,
                                                    self.main_chain[1],
                                                    [0, 1, 0],
                                                    [0, 1, 0],
                                                    [0, 1, 0],
                                                    [0, 1, 0]
                                                )
        upperArm_twist.run()

        name_bit_twist_system = self.main_chain[1][2 : len(self.main_chain[1])-4]
        lowerArm_twist = twist_chain.TwistChain(
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
        lowerArm_twist.run()

        return True
    
    def module_main_grp(self, list_objs):
        """
        parent all the system's bits under the same group

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

        self.create_driver_joint_chain()

        self.fk_system()
        self.ik_system()

        self.chains_connection()

        self.clavicle_shoulder_system()

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
            cmds.parent([self.ik_ctrls_main_grp, self.fk_ctrls_main_grp, self.clav_shoul_grp, self.switch_ctrls_grp], "controls_GRP")


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

    def set_main_chain(self, chain):
        """
        function for set the main chain which is used to build up the limb module

        Args:

        Returns:
        
        """
        self.main_chain = chain
        return self.main_chain 
