from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils
from ...controls import controller
from . import digit

reload(attributes_utils)
reload(controller)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)
reload(polevectors_utils)
reload(digit)

import pprint

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class Digits():
    def __init__(
        self,
        name,
        root_trf,
        meta_index_jnt,
        meta_middle_jnt,
        meta_ring_jnt,
        meta_pinky_jnt,
        thumb_chain,
        index_chain,
        middle_chain,
        ring_chain,
        pinky_chain,
        switch_ctrl_parent,
        switch_ctrl_pos,
        side = "C", 
        central_transform = None
        ):
        """
        """
        self.name = name
        self.root_trf = root_trf
        self.meta_index_jnt = meta_index_jnt
        self.meta_middle_jnt = meta_middle_jnt
        self.meta_ring_jnt = meta_ring_jnt
        self.meta_pinky_jnt = meta_pinky_jnt
        self.thumb_chain = thumb_chain
        self.index_chain = index_chain
        self.middle_chain = middle_chain
        self.ring_chain = ring_chain
        self.pinky_chain = pinky_chain
        self.switch_ctrl_parent = switch_ctrl_parent
        self.switch_ctrl_pos = switch_ctrl_pos
        self.side = side
        self.central_transform = central_transform

        self.input_digits = {
            "thumb":{
                "chain":self.thumb_chain
            },
            "index":{
                "chain":self.index_chain,
                "meta_jnt":self.meta_index_jnt
            },
            "middle":{
                "chain":self.middle_chain,
                "meta_jnt":self.meta_middle_jnt
            },
            "ring":{
                "chain":self.ring_chain,
                "meta_jnt":self.meta_ring_jnt
            },
            "pinky":{
                "chain":self.pinky_chain,
                "meta_jnt":self.meta_pinky_jnt
            }
        }


        self.switch_ctrl = None

        self.master_system_grp = "{}_{}_systems_GRP".format(self.side, self.name)

        self.main_system_grps = {}
        
        self.ik_system_grps = {}
        self.ik_controls = {}
        self.ik_controls_grps = {}

        self.fk_system_grps = {}
        self.fk_controls = {}
        self.fk_controls_grps = {}

        self.central_transforms = {}

    def run(self):
        """
        """

        # Temporary switch control
        self.switch_ctrl = controller.Control("{}_{}_switch".format(self.side, self.name), 3.0, 'semicircle', self.switch_ctrl_pos, self.switch_ctrl_pos, '', ['s', 'v'], '', True, True, False)

        attributes_utils.add_separator(self.switch_ctrl.get_control(), "switchAttribute", by_name=False)
        switch_attr = "switch_IK_FK"
        attributes_utils.add_float_attr(self.switch_ctrl.get_control(), switch_attr, 0, 1, 0)
        attributes_utils.add_separator(self.switch_ctrl.get_control(), "curlAttributes", by_name=False)

        cmds.parentConstraint(self.switch_ctrl_parent, self.switch_ctrl.get_offset_grp(), maintainOffset=True)

        for key in self.input_digits:
            if self.input_digits[key]["chain"] == None or self.input_digits[key]["chain"] == []:
                self.main_system_grps[key] = ""
                self.ik_system_grps[key] = ""
                self.ik_controls[key] = ""
                self.ik_controls_grps[key] = ""
                self.fk_system_grps[key] = ""
                self.fk_controls[key] = ""
                self.fk_controls_grps[key] = ""
                self.central_transforms[key] = ""
            else:
                meta_joint = ""
                if key == "thumb":
                    meta_joint = self.root_trf
                else:
                    meta_joint = self.input_digits[key]["meta_jnt"]

                digit_sample = digit.Digit(
                    self.name+"_"+key,
                    self.root_trf,
                    meta_joint,
                    self.input_digits[key]["chain"],
                    self.switch_ctrl,
                    self.side, 
                    None
                )

                digit_output = digit_sample.run()

                self.main_system_grps[key] = digit_output[-1]
                self.ik_system_grps[key] = ""
                self.ik_controls[key] = digit_output[1]
                self.ik_controls_grps[key] = digit_output[3]
                self.fk_system_grps[key] = ""
                self.fk_controls[key] = digit_output[0]
                self.fk_controls_grps[key] = digit_output[4]
                self.central_transforms[key] = digit_output[2]

                # visibility IK/FK switch driver
                cmds.connectAttr("{}.{}".format(self.switch_ctrl.get_control(), switch_attr), "{}.{}_{}_switch_IK_FK".format(self.central_transforms[key], self.side, self.name+"_"+key), force=True)
                cmds.setDrivenKeyframe(self.ik_controls_grps[key], attribute="visibility", currentDriver="{}.{}".format(self.switch_ctrl.get_control(), switch_attr), driverValue=0, value=1)
                cmds.setDrivenKeyframe(self.ik_controls_grps[key], attribute="visibility", currentDriver="{}.{}".format(self.switch_ctrl.get_control(), switch_attr), driverValue=1, value=0)
                cmds.setDrivenKeyframe(self.fk_controls_grps[key], attribute="visibility", currentDriver="{}.{}".format(self.switch_ctrl.get_control(), switch_attr), driverValue=0, value=0)
                cmds.setDrivenKeyframe(self.fk_controls_grps[key], attribute="visibility", currentDriver="{}.{}".format(self.switch_ctrl.get_control(), switch_attr), driverValue=1, value=1)

                curl_attr = "{}_curl".format(self.name+"_"+key)
                attributes_utils.add_float_attr(self.switch_ctrl.get_control(), curl_attr)
                for fk_ctrl in self.fk_controls[key]:
                    cmds.connectAttr("{}.{}".format(self.switch_ctrl.get_control(), curl_attr), "{}.rotateZ".format(fk_ctrl.get_modify_grp()), force=True)

                # follow attribute for each single ik finger control
                follow_attr = "follow"
                attributes_utils.add_float_attr(self.ik_controls[key]["finger_CTRL"].get_control(), follow_attr, 0, 10, 0)
                driver_pc = cmds.parentConstraint([self.root_trf, self.switch_ctrl.get_control()], self.ik_controls[key]["finger_CTRL"].get_offset_grp(), maintainOffset=True)
                cmds.setAttr("{}.interpType".format(driver_pc[0]), 2)
                cmds.setDrivenKeyframe(driver_pc[0], attribute="{}W0".format(self.root_trf), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), follow_attr), driverValue=0.0, value=1.0)
                cmds.setDrivenKeyframe(driver_pc[0], attribute="{}W0".format(self.root_trf), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), follow_attr), driverValue=10.0, value=0.0)
                cmds.setDrivenKeyframe(driver_pc[0], attribute="{}W1".format(self.switch_ctrl.get_control()), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), follow_attr), driverValue=0.0, value=0.0)
                cmds.setDrivenKeyframe(driver_pc[0], attribute="{}W1".format(self.switch_ctrl.get_control()), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), follow_attr), driverValue=10.0, value=1.0)

                # Temporary stuff - cleaning up the scene
                if cmds.objExists("rig_GRP"):
                    cmds.parent(self.main_system_grps[key], "rig_GRP")

                if cmds.objExists("controls_GRP"):
                    cmds.parent([self.ik_controls_grps[key], self.fk_controls_grps[key], self.switch_ctrl.get_offset_grp()], "controls_GRP")

        return True
