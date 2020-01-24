from ...controls import controller
from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils, vectors_utils
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
        self.shoulder_loc = None

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

        # cmds.error("number of joint: {}".format(len(self.fk_chain)))

        for i, jnt in enumerate(self.fk_chain):
            
            if i == (len(self.fk_chain) - 1):
                break
            ctrl = None
            if i != 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, self.fk_controls[i-1].get_control(), ['v'], '', True, True, False)
            elif i == 0:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['v'], '', True, True, False)
            else:
                ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 5.0, 'circle', jnt, jnt, '', ['v'], '', True, True, False)
            self.fk_controls.append(ctrl)
            
            cmds.parentConstraint(ctrl.get_control(), jnt, maintainOffset=True)
            cmds.scaleConstraint(ctrl.get_control(), jnt, maintainOffset=True)

        self.fk_system_grp = cmds.group(empty=True, name="{}_{}_fkSystem_GRP".format(self.side, self.name))
        cmds.parent(self.fk_system_objs, self.fk_system_grp)
        cmds.group(empty=True, name=self.fk_ctrls_main_grp)
        cmds.parent(self.fk_controls[0].get_offset_grp(), self.fk_ctrls_main_grp)
        self.module_main_grp(self.fk_system_grp)

        return True

    def ik_stretch_update(self):
        """
        """

        module_scale_attr = "moduleScale"
        attributes_utils.add_vector_attr(self.central_transform, module_scale_attr, keyable=True, lock=False)
        cmds.setAttr("{}.{}X".format(self.central_transform, module_scale_attr), 1)
        cmds.setAttr("{}.{}Y".format(self.central_transform, module_scale_attr), 1)
        cmds.setAttr("{}.{}Z".format(self.central_transform, module_scale_attr), 1)

        stretch_attr = "stretchyArm"
        attributes_utils.add_separator(self.hand_ik_ctrl.get_control(), name_sep="stretchyAttribute", by_name=False)
        attributes_utils.add_float_attr(self.hand_ik_ctrl.get_control(), stretch_attr, 0, 1, 0, keyable=True, lock=False)

        start_loc = cmds.spaceLocator(name="{}_{}_startStretch_LOC".format(self.side, self.name))
        end_loc = cmds.spaceLocator(name="{}_{}_endStretch_LOC".format(self.side, self.name))

        cmds.parentConstraint(self.shoulder_loc, start_loc, maintainOffset=False)
        cmds.parentConstraint(self.hand_ik_ctrl.get_control(), end_loc, maintainOffset=False)

        shoulder = OM.MVector(cmds.xform(self.main_chain[0], q=True, ws=True, t=True))
        elbow = OM.MVector(cmds.xform(self.main_chain[1], q=True, ws=True, t=True))
        wrist = OM.MVector(cmds.xform(self.main_chain[2], q=True, ws=True, t=True))

        shoulder_elbow_dist = vectors_utils.distance_between(shoulder, elbow)
        elbow_wrist_dist = vectors_utils.distance_between(elbow, wrist)

        max_dist = shoulder_elbow_dist + elbow_wrist_dist

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
        cmds.connectAttr("{}.{}".format(self.hand_ik_ctrl.get_control(), stretch_attr), "{}.blender".format(stretch_blend_node), force=True)
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

        return [start_loc[0], end_loc[0]]

    def ik_system(self):
        """
        building up the ik system

        Args:

        Returns:
        
        """

        driver_ctrls_offset_grp = []        

        self.ik_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ik", True)
        self.ik_system_objs.append(self.ik_chain[0])

        self.shoulder_loc = cmds.spaceLocator(name="{}_{}_shoulderPosition_LOC".format(self.side, self.name))
        transforms_utils.align_objs(self.main_chain[0],  self.shoulder_loc)
        cmds.parentConstraint(self.clavicle_jnt, self.shoulder_loc, maintainOffset=True)
        cmds.parentConstraint(self.shoulder_loc, self.ik_chain[0], maintainOffset=True)
        self.ik_system_objs.append(self.shoulder_loc[0])

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
        
        self.ik_system_grp = cmds.group(empty=True, name="{}_{}_ikSystem_GRP".format(self.side, self.name))
        cmds.parent(self.ik_system_objs, self.ik_system_grp)
        cmds.group(empty=True, name=self.ik_ctrls_main_grp)
        cmds.parent(driver_ctrls_offset_grp, self.ik_ctrls_main_grp)

        self.module_main_grp(self.ik_system_grp)        

        return True
    
    # def clavicle_shoulder_system(self):
    def auto_clavicle_system(self, switch_attr):
        """
        building up an auto-clavicle system

        Args:

        Returns:

        """

        # self.shoulder_ctrl = controller.Control("{}_start_ik".format(self.main_chain[0][:len(self.main_chain[0])-4]), 5.0, 'circleFourArrows', self.main_chain[0], self.main_chain[0], '', ['r', 's', 'v'], '', True, True, False)
        self.clavicle_ctrl = controller.Control("{}".format(self.clavicle_jnt[:len(self.clavicle_jnt)-4]), 5.0, 'pin', self.clavicle_jnt, self.clavicle_jnt, '', ['t', 's', 'v'], '', True, True, False)
        cmds.parentConstraint(self.clavicle_ctrl.get_control(), self.clavicle_jnt, maintainOffset=True)
        
        auto_attribute = "autoClavicle"
        attributes_utils.add_float_attr(self.clavicle_ctrl.get_control(), auto_attribute, 0.0, 10.0, 7.0, keyable=True, lock=False)
        # cmds.parentConstraint(self.clavicle_ctrl.get_control(), self.shoulder_loc, maintainOffset=True)

        start_clav_fol_jnt = cmds.createNode("joint", name="{}_{}_startAutoClavicle_JNT".format(self.side, self.name))
        transforms_utils.align_objs(self.clavicle_jnt, start_clav_fol_jnt)

        end_clav_fol_jnt = cmds.createNode("joint", name="{}_{}_endAutoClavicle_JNT".format(self.side, self.name))
        transforms_utils.align_objs(self.main_chain[2], end_clav_fol_jnt)

        cmds.parent(end_clav_fol_jnt, start_clav_fol_jnt)

        # root space locator
        spine_follow_loc = cmds.spaceLocator(name="{}_{}_spineFollow_autoClavicle_LOC".format(self.side, self.name))
        transforms_utils.align_objs(self.clavicle_jnt, spine_follow_loc[0])
        cmds.parentConstraint(self.root_jnt, spine_follow_loc[0], maintainOffset=True)

        # auto clav ik space
        auto_clav_follow_loc = cmds.spaceLocator(name="{}_{}_autoClavFollow_autoClavicle_LOC".format(self.side, self.name))
        transforms_utils.align_objs(self.hand_ik_ctrl.get_control(), auto_clav_follow_loc[0])
        switch_pac = cmds.pointConstraint([self.root_jnt, self.hand_ik_ctrl.get_control()], auto_clav_follow_loc[0], maintainOffset=True)
        # switch_pac = cmds.parentConstraint([self.fk_controls[0].get_control(), self.hand_ik_ctrl.get_control()], auto_clav_follow_loc[0], maintainOffset=True)
        # cmds.setAttr("{}.interpType".format(switch_pac[0]), 2)

        # ik handle for clavicle automatation
        ik_handle_clav_follow = cmds.ikHandle(name="{}_{}_autoClavicle".format(self.side, self.name), solver="ikSCsolver", startJoint=start_clav_fol_jnt, endEffector=end_clav_fol_jnt)
        cmds.parentConstraint(auto_clav_follow_loc[0], ik_handle_clav_follow[0], maintainOffset=True)
        cmds.pointConstraint(self.root_jnt, start_clav_fol_jnt, maintainOffset=True)

        # cmds.pointConstraint(self.root_jnt, self.clavicle_ctrl.get_offset_grp(), maintainOffset=True)
                
        offset_pac = cmds.parentConstraint([spine_follow_loc[0], start_clav_fol_jnt], self.clavicle_ctrl.get_offset_grp(), maintainOffset=True)
        cmds.setAttr("{}.interpType".format(offset_pac[0]), 2)
        # modify_pac = cmds.parentConstraint(start_clav_fol_jnt, self.clavicle_ctrl.get_modify_grp(), maintainOffset=True)

        # follow for the clavicle in IK
        cmds.setDrivenKeyframe(offset_pac[0], attribute="{}W0".format(spine_follow_loc[0]), currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), auto_attribute), driverValue=0.0, value=10.0)
        cmds.setDrivenKeyframe(offset_pac[0], attribute="{}W0".format(spine_follow_loc[0]), currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), auto_attribute), driverValue=10.0, value=0.0)
        cmds.setDrivenKeyframe(offset_pac[0], attribute="{}W1".format(start_clav_fol_jnt), currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), auto_attribute), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(offset_pac[0], attribute="{}W1".format(start_clav_fol_jnt), currentDriver="{}.{}".format(self.clavicle_ctrl.get_control(), auto_attribute), driverValue=10.0, value=1.0)

        cmds.setDrivenKeyframe(switch_pac[0], attribute="{}W0".format(self.root_jnt), currentDriver="{}.{}".format(self.central_transform, switch_attr), driverValue=0.0, value=0.0)
        cmds.setDrivenKeyframe(switch_pac[0], attribute="{}W0".format(self.root_jnt), currentDriver="{}.{}".format(self.central_transform, switch_attr), driverValue=1.0, value=1.0)
        cmds.setDrivenKeyframe(switch_pac[0], attribute="{}W1".format(self.hand_ik_ctrl.get_control()), currentDriver="{}.{}".format(self.central_transform, switch_attr), driverValue=0.0, value=1.0)
        cmds.setDrivenKeyframe(switch_pac[0], attribute="{}W1".format(self.hand_ik_ctrl.get_control()), currentDriver="{}.{}".format(self.central_transform, switch_attr), driverValue=1.0, value=0.0)

        # clean scene
        self.clav_shoul_grp = cmds.group(empty=True, name="{}_{}_clavicleSystem_GRP".format(self.side, self.name))
        cmds.parent(self.clavicle_ctrl.get_offset_grp(), self.clav_shoul_grp)
        cmds.parent([start_clav_fol_jnt, ik_handle_clav_follow[0], spine_follow_loc[0], auto_clav_follow_loc[0]], self.ik_system_grp)

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
            
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0, keyable=True, lock=False)
        
        elif cmds.objExists("{}.{}".format(self.central_transform, name_attr)):
            print "central_transform already present"
        
        else:
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0, keyable=True, lock=False)

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

        return name_attr

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
        upper_twist_jnt_chain = upperArm_twist.run()

        for jnt in upper_twist_jnt_chain:
            cmds.connectAttr("{}.moduleScaleY".format(self.central_transform), "{}.scaleY".format(jnt), force=True)
            cmds.connectAttr("{}.moduleScaleZ".format(self.central_transform), "{}.scaleZ".format(jnt), force=True)

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
        lower_twist_jnt_chain = lowerArm_twist.run()

        for jnt in lower_twist_jnt_chain:
            cmds.connectAttr("{}.moduleScaleY".format(self.central_transform), "{}.scaleY".format(jnt), force=True)
            cmds.connectAttr("{}.moduleScaleZ".format(self.central_transform), "{}.scaleZ".format(jnt), force=True)

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

        print("###--- Module BipedArm --- START ---###")

        # temporary
        self.world_space_loc = cmds.spaceLocator(name="{}_{}_worldSpace_LOC".format(self.side, self.name))
        world_space_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.world_space_loc[0])
        cmds.parentConstraint(self.root_jnt, world_space_loc_offset_grp[0], maintainOffset=True)

        self.module_main_grp(world_space_loc_offset_grp[0])

        self.create_driver_joint_chain()

        self.fk_system()
        self.ik_system()

        # temporary fix
        cmds.parentConstraint(self.shoulder_loc, self.fk_controls[0].get_offset_grp(), maintainOffset=True)

        chains_connection_ops = self.chains_connection()

        self.auto_clavicle_system(chains_connection_ops)

        # ik stretchy update
        stretch_update = self.ik_stretch_update()
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
