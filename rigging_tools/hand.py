import pprint
from collections import OrderedDict

from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils, curves_utils
from ...controls import controller


reload(attributes_utils)
reload(controller)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)
reload(polevectors_utils)
reload(curves_utils)

import pprint

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class Hand():
    def __init__(
        self, 
        name, 
        root_trf, 
        side="C", 
        meta_jnt_index="",
        meta_jnt_middle="",
        meta_jnt_ring="",
        meta_jnt_pinky=""
        ):
        """
        """
        self.name = name
        self.root_trf = root_trf
        self.side = side
        self.meta_jnt_index = meta_jnt_index
        self.meta_jnt_middle = meta_jnt_middle
        self.meta_jnt_ring = meta_jnt_ring
        self.meta_jnt_pinky = meta_jnt_pinky
        self.end_cup_ctrl = None
        self.start_cup_ctrl = None
        
        self.meta_jnts_relatives = OrderedDict([
            ('meta_jnt_index', {'jnt_name':self.meta_jnt_index}),
            ('meta_jnt_middle', {'jnt_name':self.meta_jnt_middle}),
            ('meta_jnt_ring', {'jnt_name':self.meta_jnt_ring}),
            ('meta_jnt_pinky', {'jnt_name':self.meta_jnt_pinky})
        ])

        self.main_grp = "{}_{}_system_GRP".format(self.side, self.name)
        self.controls_grp = "{}_{}_controls_GRP".format(self.side, self.name)

    def hand_system(self):
        """
        """
        meta_jnts_children_pos = []
        if self.meta_jnt_index == "" or self.meta_jnt_middle == "" or self.meta_jnt_ring == "" or self.meta_jnt_pinky == "":
            print "#### ---- One or more than one meta_jnts joint not provided. Module skipped!!! ---- ####"
        else:

            for i, key in enumerate(self.meta_jnts_relatives): 
                tmp_relatives = cmds.listRelatives(self.meta_jnts_relatives[key]['jnt_name'], children=True)
                tmp_joints = []
                for obj in tmp_relatives:
                    if cmds.nodeType(obj) == "joint":
                        tmp_joints.append(obj)
                        meta_jnts_children_pos.append(cmds.xform(obj, worldSpace=True, query=True, translation=True))
                self.meta_jnts_relatives[key]['list_children'] = tmp_joints


            crv = cmds.curve(point = meta_jnts_children_pos, degree=3)
            cup_driver_crv = cmds.rename(crv, "{}_{}_nucklesDriver_CRV".format(self.side, self.name))

            # query the cup_driver_crv's CVs
            degs = cmds.getAttr("{}.degree".format(cup_driver_crv))
            spans = cmds.getAttr("{}.spans".format(cup_driver_crv))
            cvs = degs+spans

            locator_drivers = []
            cup_joints = []
            # creating the joints driver
            for i, key in enumerate(self.meta_jnts_relatives):
                # creating the spaceLocator which will drive the aiming of the 
                driver_loc = cmds.spaceLocator(name="{}_{}_{}_LOC".format(self.side, self.name, key))
                locator_drivers.append(driver_loc[0])
                transforms_utils.align_objs(self.meta_jnts_relatives[key]["list_children"][0], driver_loc)

                # attach the spaceLocator to curve
                point = OM.MPoint(meta_jnts_children_pos[i][0], meta_jnts_children_pos[i][1], meta_jnts_children_pos[i][2])
                parameter = curves_utils.get_param_at_point(cup_driver_crv+"Shape", point)
                motion_path_node = cmds.createNode("motionPath", name="{}_{}_{}_MPT".format(self.side, self.name, key))
                cmds.setAttr("{}.uValue".format(motion_path_node), parameter)
                cmds.connectAttr("{}Shape.worldSpace[0]".format(cup_driver_crv), "{}.geometryPath".format(motion_path_node), force=True)
                cmds.connectAttr("{}.xCoordinate".format(motion_path_node), "{}.translateX".format(driver_loc[0]), force=True)
                cmds.connectAttr("{}.yCoordinate".format(motion_path_node), "{}.translateY".format(driver_loc[0]), force=True)
                cmds.connectAttr("{}.zCoordinate".format(motion_path_node), "{}.translateZ".format(driver_loc[0]), force=True)

                # do aiming between the driver locator and the meta_jnt joint
                cmds.aimConstraint(driver_loc[0], self.meta_jnts_relatives[key]["jnt_name"], maintainOffset=True, worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=driver_loc[0])
                # scale fix
                for axis in ["X", "Y", "Z"]:
                    cmds.connectAttr("{}.scale{}".format(self.root_trf, axis), "{}.scale{}".format(self.meta_jnts_relatives[key]["jnt_name"], axis), force=True)

                if i == 0:
                    joint_cup_end = cmds.createNode("joint", name="{}_{}_jointCup_endDriver_JNT".format(self.side, self.name))
                    cup_joints.append(joint_cup_end)
                    transforms_utils.align_objs(self.meta_jnts_relatives[key]["list_children"][0], joint_cup_end)
                    cmds.makeIdentity(joint_cup_end, apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
                    self.end_cup_ctrl = controller.Control("{}_{}_endCup".format(self.side, self.name), 5.0, 'cube', joint_cup_end, joint_cup_end, "", ['s', 'v'], '', True, True, False)
                    cmds.parentConstraint(self.end_cup_ctrl.get_control(), joint_cup_end, maintainOffset=True)
                if i == (cvs - 1):
                    joint_cup_start = cmds.createNode("joint", name="{}_{}_jointCup_startDriver_JNT".format(self.side, self.name))
                    cup_joints.append(joint_cup_start)
                    transforms_utils.align_objs(self.meta_jnts_relatives[key]["list_children"][0], joint_cup_start)
                    cmds.makeIdentity(joint_cup_start, apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
                    self.start_cup_ctrl = controller.Control("{}_{}_startCup".format(self.side, self.name), 5.0, 'cube', joint_cup_start, joint_cup_start, "", ['s', 'v'], '', True, True, False)
                    cmds.parentConstraint(self.start_cup_ctrl.get_control(), joint_cup_start, maintainOffset=True)

            # clean things up
            drivers_loc_grp = cmds.group(empty=True, name="{}_{}_metaJointDriverLocs_GRP".format(self.side, self.name))
            cmds.parent(locator_drivers, drivers_loc_grp)
            cup_joints_grp = cmds.group(empty=True, name="{}_{}_cupDriverJoints_GRP".format(self.side, self.name))
            cmds.parent(cup_joints, cup_joints_grp)
            drivers_grp = cmds.group(empty=True, name="{}_{}_driversSystem_GRP".format(self.side, self.name))
            cmds.parent([cup_driver_crv, drivers_loc_grp, cup_joints_grp], drivers_grp)

            # make skinCluster for drive the crv
            cmds.skinCluster(cup_joints, cup_driver_crv)                

            for i in range(0, len(locator_drivers)):
                if i == (len(locator_drivers) - 1):
                    cmds.aimConstraint(locator_drivers[i-1], locator_drivers[i], maintainOffset=True, worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root_trf)
                else:
                    cmds.aimConstraint(locator_drivers[i+1], locator_drivers[i], maintainOffset=True, worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root_trf)


            self.module_main_grp([drivers_grp])
            
            # cleaning up teh scene
            if cmds.objExists(self.controls_grp):
                cmds.parentConstraint(self.root_trf, self.controls_grp, maintainOffset=False)
                for axis in ["X", "Y", "Z"]:
                    cmds.connectAttr("{}.scale{}".format(self.root_trf, axis), "{}.scale{}".format(self.controls_grp, axis), force=True)
                cmds.parent([self.end_cup_ctrl.get_offset_grp(), self.start_cup_ctrl.get_offset_grp()], self.controls_grp)
            else:
                cmds.group(empty=True, name=self.controls_grp)
                cmds.parentConstraint(self.root_trf, self.controls_grp, maintainOffset=False)
                for axis in ["X", "Y", "Z"]:
                    cmds.connectAttr("{}.scale{}".format(self.root_trf, axis), "{}.scale{}".format(self.controls_grp, axis), force=True)
                cmds.parent([self.end_cup_ctrl.get_offset_grp(), self.start_cup_ctrl.get_offset_grp()], self.controls_grp)

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

        self.hand_system()

        # Temporary stuff
        if cmds.objExists("rig_GRP"):
            cmds.parent(self.main_grp, "rig_GRP")

        if cmds.objExists("controls_GRP"):
            cmds.parent(self.controls_grp, "controls_GRP")

        return True
