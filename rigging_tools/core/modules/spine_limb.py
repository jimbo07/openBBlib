
from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils
from ...controls import controller

reload(attributes_utils)
reload(controller)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True


class SpineLimb():
    def __init__(
                    self, 
                    name, 
                    main_chain, 
                    side = "C", 
                    root_space = None,
                    num_fk_ctrls = -1, 
                    num_ik_middle_ctrls = 3, 
                    central_transform = None
                ):
        """
        Class constructor

        Args:

        Returns:

        """
        self.name = name
        self.side = side
        
        self.main_chain = main_chain
        self.driver_chain = []
        self.fk_chain = []
        self.ik_spline_chain = []
        
        self.num_fk_ctrls = num_fk_ctrls
        self.num_ik_middle_ctrls = num_ik_middle_ctrls

        self.central_transform = central_transform
        self.world_space_loc = None
        
        self.root_space = root_space 

        self.start_ik_ctrl = None    
        self.end_ik_ctrl = None
        self.fk_ctrls = []

        self.switch_ctrl = None
        self.switchIKFK_drivers_grp = None

        self.fk_controls = []

        self.fk_system_objs = []
        self.ik_system_objs = []

        self.ik_ctrls_main_grp = "{}_{}_ikControls_GRP".format(self.side, self.name)
        self.fk_ctrls_main_grp = "{}_{}_fkControls_GRP".format(self.side, self.name)

        self.main_grp = "{}_{}_system_GRP".format(self.side, self.name)

        self.world_space_loc = None
        

    def create_driver_joint_chain(self):
        """
        building up the final driver chain which will drive the final skeleton one

        Args:

        Returns:

        """
        self.driver_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "driver", True)
        return self.driver_chain

    def fk_system(self):
        """
        building up the fk system

        Args:

        Returns:

        """       
        self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)
        self.fk_system_objs.append(self.fk_chain[0])

        if self.num_fk_ctrls == -1 or self.num_fk_ctrls == len(self.fk_chain):
            for i, jnt in enumerate(self.fk_chain):
                if i == 0:
                    ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 3.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
                    self.fk_controls.append(ctrl)
                    cmds.parentConstraint(self.fk_controls[i].get_control(), jnt, maintainOffset=True)
                else:
                    ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 3.0, 'circle', jnt, jnt, self.fk_controls[i-1].get_control(), ['s', 'v'], '', True, True, False)
                    self.fk_controls.append(ctrl)
                    cmds.parentConstraint(self.fk_controls[i].get_control(), jnt, maintainOffset=True)
        else:
            print "NEEDS TO BE IMPLEMENTED YET"

        # clean up the scene
        cmds.group(empty=True, name=self.fk_ctrls_main_grp)
        cmds.parent(self.fk_controls[0].get_offset_grp(), self.fk_ctrls_main_grp)
        fk_system_grp = cmds.group(self.fk_system_objs, name="{}_{}_fkSystem_GRP".format(self.side, self.name))
        
        self.module_main_grp(fk_system_grp)

        # connect to root
        if self.root_space == "" or self.root_space == None:
            print "###--- No root space found. It'll skipped ---###"
        else:
            name_attr = "spaces"
            transforms_utils.make_spaces(self.fk_controls[0].get_control(), self.fk_controls[0].get_offset_grp(), name_attr, [self.world_space_loc[0], self.root_space], naming=["world", "root"])
            cmds.setAttr("{}.{}".format(self.fk_controls[0].get_control(), name_attr), 1)

        return True

    def ik_system(self):
        """
        building up the ik system

        Args:

        Returns:

        """
        self.ik_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "ikSpine", True)
        self.ik_system_objs.append(self.ik_chain[0])

        # re-orient the last joint as his father
        cmds.joint(self.ik_chain[-1], edit=True, orientJoint="none", children=True, zeroScaleOrient=True)

        curve_points = []
        for jnt in self.ik_chain:
            point = cmds.xform(jnt, query=True, worldSpace=True, translation=True)
            curve_points.append(point)
        
        # create curves and rebuilding them
        ik_spline_crv = cmds.curve(degree=1, point=curve_points)
        ik_spline_crv = cmds.rename(ik_spline_crv, "{}_{}_ikSplineHandle_crv".format(self.side, self.name))

        cmds.rebuildCurve(
                            ik_spline_crv,
                            caching=True,
                            replaceOriginal=True,
                            rebuildType=0,
                            endKnots=True,
                            keepRange=False,
                            keepControlPoints=True,
                            keepEndPoints=True,
                            keepTangents=False,
                            spans=len(self.ik_chain),
                            degree=1,
                            tolerance=0.01
                        )
        cmds.delete(ik_spline_crv, constructionHistory=True)

        rebuilded_crv = cmds.rebuildCurve(
                                            ik_spline_crv,
                                            caching=True,
                                            replaceOriginal=False,
                                            rebuildType=0,
                                            endKnots=True,
                                            keepRange=False,
                                            keepControlPoints=False,
                                            keepEndPoints=True,
                                            keepTangents=False,
                                            spans=len(self.ik_chain)/2,
                                            degree=7,
                                            tolerance=0.01
                                        )
        driver_ik_spline_crv = cmds.rename(rebuilded_crv, "{}_{}_ikSplineHandle_driver_crv".format(self.side, self.name))
        cmds.delete(driver_ik_spline_crv, constructionHistory=True)

        self.ik_system_objs.extend([ik_spline_crv, driver_ik_spline_crv])

        # wire deformer
        wire_def = cmds.wire(ik_spline_crv, wire=driver_ik_spline_crv, name="{}_{}_ikSplineCrvDriver_wre".format(self.side, self.name))
        cmds.setAttr("{}.dropoffDistance[0]".format(wire_def[0]), 9999999999)

        self.ik_system_objs.append("{}BaseWire".format(driver_ik_spline_crv))

        # creating locator for twisting ikSpline
        start_twist_loc = cmds.spaceLocator(name="{}_{}_startTwist_ikSpline_LOC".format(self.side, self.name))
        transforms_utils.align_objs(self.ik_chain[0], start_twist_loc[0])

        end_twist_loc = cmds.spaceLocator(name="{}_{}_endTwist_ikSpline_LOC".format(self.side, self.name))
        transforms_utils.align_objs(self.ik_chain[-1], end_twist_loc[0])

        # ik spline solver  ---  -scv false -pcv false -snc true
        ik_spline_solver = cmds.ikHandle(name="{}_{}_splineSolver_IKH".format(self.side, self.name), solver='ikSplineSolver', startJoint=self.ik_chain[0], endEffector=self.ik_chain[-1], createCurve=False, simplifyCurve=False, parentCurve=False, snapCurve=True, curve=ik_spline_crv)
        cmds.setAttr("{}.dTwistControlEnable".format(ik_spline_solver[0]), 1)
        cmds.setAttr("{}.dWorldUpType".format(ik_spline_solver[0]), 4)

        self.ik_system_objs.append(ik_spline_solver[0])

        # twist ik spline solver
        cmds.connectAttr("{}.worldMatrix[0]".format(start_twist_loc[0]), "{}.dWorldUpMatrix".format(ik_spline_solver[0]), force=True)
        cmds.connectAttr("{}.worldMatrix[0]".format(end_twist_loc[0]), "{}.dWorldUpMatrixEnd".format(ik_spline_solver[0]), force=True)

        # make joint at parameter
        driver_joints = []
        parameter = 0.0

        driver_crv_dag_path = dag_node.DagNode(driver_ik_spline_crv)
        fn_curves = OM.MFnNurbsCurve(driver_crv_dag_path.get_dag_path())
        point = OM.MPoint()
        parameter = 0.0
        for i in range(0, self.num_ik_middle_ctrls + 2):
            if i == 0:
                point = fn_curves.getPointAtParam(parameter, 0)
                jnt = cmds.createNode("joint", name="{}_{}_{}_spineDriver_JNT".format(self.side, self.name, i))
                cmds.xform(jnt, translation=[point.x, point.y, point.z])
                driver_joints.append(jnt)
            else: # if i == self.num_ik_middle_ctrls-1:
                parameter += 1.0/float(self.num_ik_middle_ctrls + 1)
                point = fn_curves.getPointAtParam(parameter, 0)
                jnt = cmds.createNode("joint", name="{}_{}_{}_spineDriver_JNT".format(self.side, self.name, i))
                cmds.xform(jnt, translation=[point.x, point.y, point.z])
                driver_joints.append(jnt)


        driver_joints_grp = cmds.group(driver_joints, name="{}_{}_ikSystem_driverJoints_GRP".format(self.side, self.name))
        self.ik_system_objs.append(driver_joints_grp)

        # parenting twist locators under the first and the end driver joints
        cmds.parent(start_twist_loc[0], driver_joints[0]) 
        cmds.parent(end_twist_loc[0], driver_joints[-1])

        # stretchy spine
        stretchy_mld_node = cmds.createNode("multiplyDivide", name="{}_{}_ikSpline_stretch_mld".format(self.side, self.name))
        stretchy_cvi_node = cmds.createNode("curveInfo", name="{}_{}_ikSpline_stretch_cvi".format(self.side, self.name))
        cmds.connectAttr("{}Shape.worldSpace[0]".format(ik_spline_crv), "{}.inputCurve".format(stretchy_cvi_node), force=True)
        rest_arcLenght_val = cmds.getAttr("{}.arcLength".format(stretchy_cvi_node))
        cmds.connectAttr("{}.arcLength".format(stretchy_cvi_node), "{}.input1X".format(stretchy_mld_node), force=True)
        cmds.setAttr("{}.input2X".format(stretchy_mld_node), rest_arcLenght_val)
        cmds.setAttr("{}.operation".format(stretchy_mld_node), 2)

        for jnt in self.ik_chain:
            cmds.connectAttr("{}.outputX".format(stretchy_mld_node) , "{}.scaleX".format(jnt), force=True)
        
        # skinCluster which drives the driver curve
        cmds.skinCluster(driver_joints, driver_ik_spline_crv)

        # building controls
        ik_controls = []
        # ik_controls_offset_grps = []
        for i, jnt in enumerate(driver_joints):
            if i == 0:
                self.start_ik_ctrl = controller.Control("{}_{}_start_ik".format(self.side, self.name), 5.0, 'cube', jnt, jnt, '', ['s', 'v'], '', True, True, False)
                self.start_ik_ctrl.make_dynamic_pivot("{}_{}_startPivot_ik_".format(self.side, self.name), 2.5, self.start_ik_ctrl.get_control(), self.start_ik_ctrl.get_control())
                ik_controls.append(self.start_ik_ctrl)
                cmds.parentConstraint(self.start_ik_ctrl.get_control(), jnt, maintainOffset=True)
            elif i == len(driver_joints) - 1:
                self.end_ik_ctrl = controller.Control("{}_{}_end_ik".format(self.side, self.name), 5.0, 'cube', jnt, jnt, '', ['s', 'v'], '', True, True, False)
                self.end_ik_ctrl.make_dynamic_pivot("{}_{}_endPivot_ik_".format(self.side, self.name), 2.5, self.end_ik_ctrl.get_control(), self.end_ik_ctrl.get_control())
                ik_controls.append(self.end_ik_ctrl)
                cmds.parentConstraint(self.end_ik_ctrl.get_control(), jnt, maintainOffset=True)
            else:
                middle_ctrl = controller.Control("{}_{}_middle{}_ik".format(self.side, self.name, i-1), 5.0, 'square', jnt, jnt, '', ['s', 'v'], '', True, True, False)
                ik_controls.append(middle_ctrl)
                cmds.parentConstraint(middle_ctrl.get_control(), jnt, maintainOffset=True)

        # follow feature of middle controls
        pac_middleCtrls_follow = []
        follow_factor = 0
        for i, ctrl in enumerate(ik_controls):
            if i == 0:
                continue
            elif i == len(ik_controls) - 1:
                continue
            else:
                pac = cmds.parentConstraint([self.world_space_loc[0], ik_controls[0].get_control(), ik_controls[-1].get_control()], ctrl.get_offset_grp(), maintainOffset=True)
                cmds.setAttr("{}.interpType".format(pac[0]), 2)
                name_attr = "startEndFollow"
                attributes_utils.add_float_attr(ctrl.get_control(), name_attr, -5.0, 10.0, 0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W0".format(self.world_space_loc[0]), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=-5.0, value=1.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W0".format(self.world_space_loc[0]), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W0".format(self.world_space_loc[0]), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=10.0, value=0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W1".format(ik_controls[0].get_control()), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=-5.0, value=0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W1".format(ik_controls[0].get_control()), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=0.0, value=1.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W1".format(ik_controls[0].get_control()), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=10.0, value=0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W2".format(ik_controls[-1].get_control()), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=-5.0, value=0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W2".format(ik_controls[-1].get_control()), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=0.0, value=0.0)
                cmds.setDrivenKeyframe(pac, attribute="{}W2".format(ik_controls[-1].get_control()), currentDriver="{}.{}".format(ctrl.get_control(), name_attr), driverValue=10.0, value=1.0)
                follow_factor += 10.0/float(self.num_ik_middle_ctrls + 1.0)
                cmds.setAttr("{}.{}".format(ctrl.get_control(), name_attr), follow_factor)

        # clean up the scene
        cmds.group(empty=True, name=self.ik_ctrls_main_grp)
        for ctrl  in ik_controls:
            cmds.parent(ctrl.get_offset_grp(), self.ik_ctrls_main_grp)

        ik_system_grp = cmds.group(empty=True, name="{}_{}_ikSystem_GRP".format(self.side, self.name))
        cmds.parent(self.ik_system_objs, ik_system_grp)

        self.module_main_grp(ik_system_grp)

        # connect to root
        if self.root_space == "" or self.root_space == None:
            print "###--- No root space found. It'll skipped ---###"
        else:
            name_attr = "spaces"
            transforms_utils.make_spaces(self.start_ik_ctrl.get_control(), self.start_ik_ctrl.get_offset_grp(), name_attr, [self.world_space_loc[0], self.root_space], naming=["world", "root"])
            cmds.setAttr("{}.{}".format(self.start_ik_ctrl.get_control(), name_attr), 1)

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
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
            cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_chain[i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1.0, value=0.0)

            cmds.setDrivenKeyframe(self.ik_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.ik_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls_main_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1)

            main_pac = cmds.parentConstraint(self.driver_chain[i], jnt, maintainOffset=True)

        # clean up the scene
        grp_objs.append(self.central_transform)
        grp_objs.append(self.driver_chain[0])

        self.module_main_grp(grp_objs)


        # self.module_main_grp(grp_objs)

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

        print("###--- Module Spine --- START ---###")

        # temporary
        self.world_space_loc = cmds.spaceLocator(name="{}_{}_worldSpace_LOC".format(self.side, self.name))
        world_space_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.world_space_loc[0])

        self.module_main_grp(world_space_loc_offset_grp[0])

        self.create_driver_joint_chain()

        self.fk_system()
        self.ik_system()

        self.chains_connection()

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

    def get_root_space(self):
        """
        function for retrieving the children/obj constrained to the root joint of the module

        Args:

        Returns:
        
        """
        return self.root_space

    def get_num_fk_ctrls(self):
        """
        function for retrieving the number of fk controls of the module

        Args:

        Returns:
        
        """
        return self.num_fk_ctrls

    def get_num_ik_middle_ctrls(self):
        """
        function for retrieving the number of ik middle controls of the module

        Args:

        Returns:
        
        """
        return self.num_ik_middle_ctrls

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

    def set_root_space(self, objs_list):
        """
        function for set the children/obj constrained to the root joint of the module

        Args:

        Returns:
        
        """
        self.root_space = objs_list 
        return self.root_space

    def set_num_fk_ctrls(self, number):
        """
        function for set the number of fk controls of the module

        Args:

        Returns:
        
        """
        self.num_fk_ctrls = number
        return self.num_fk_ctrls

    def set_num_ik_middle_ctrls(self, number):
        """
        function for set the number of ik middle controls of the module

        Args:

        Returns:
        
        """
        self.num_ik_middle_ctrls = number
        return self.num_ik_middle_ctrls

    def set_main_chain(self, chain):
        """
        function for set the main chain which is used to build up the limb module

        Args:

        Returns:
        
        """
        self.main_chain = chain
        return self.main_chain


