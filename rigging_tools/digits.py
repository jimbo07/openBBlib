from ...utils import attributes_utils, joints_utils, dag_node, transforms_utils, polevectors_utils
from ...controls import controller


reload(attributes_utils)
reload(controller)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)
reload(polevectors_utils)

import pprint

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class Digits():
    def __init__(self,
                name,
                root_space,
                ball_jnt,
                thumb_chain,
                index_chain,
                middle_chain,
                ring_chain,
                pinky_chain,
                switch_ctrl_parent,
                switch_ctrl_pos,
                side = "C", 
                central_transform = None):
        """
        """
        self.name = name
        self.root_space = root_space
        self.ball_jnt = ball_jnt
        self.thumb_chain = thumb_chain
        self.index_chain = index_chain
        self.middle_chain = middle_chain
        self.ring_chain = ring_chain
        self.pinky_chain = pinky_chain
        self.switch_ctrl_parent = switch_ctrl_parent
        self.switch_ctrl_pos = switch_ctrl_pos
        self.side = side
        self.central_transform = central_transform

        self.main_chains = {
            "thumb":self.thumb_chain,
            "index":self.index_chain,
            "middle":self.middle_chain,
            "ring":self.ring_chain,
            "pinky":self.pinky_chain
        }

        self.driver_chains = {}
        self.fk_chains = {}
        self.ik_primary_chains = {}
        self.ik_bendy_chains = {}

        self.switch_ctrl = None

        ########################################################################################
        ####################---- FK controls section pre-initialization ----####################
        self.fk_controls = {}

        self.fk_controls_grps = {}
        for key in self.main_chains:
            if self.main_chains[key] == None or self.main_chains[key] == []:
                self.fk_controls_grps[key] = ""
            else:
                self.fk_controls_grps[key] = "{}_{}_{}DigitFKControls_GRP".format(self.side, self.name, key)

        self.fk_controls_master_grp = "{}_{}_digitsFKControls_GRP".format(self.side, self.name)
        ####################---- FK controls section pre-initialization ----####################
        ########################################################################################


        ########################################################################################
        ####################---- FK system mechanics section pre-initialization ----####################
        self.fk_system_grps = {}
        for key in self.main_chains:
            if self.main_chains[key] == None or self.main_chains[key] == []:
                self.fk_system_grps[key] = ""
            else:
                self.fk_system_grps[key] = "{}_{}_{}Digit_FKSystem_GRP".format(self.side, self.name, key)
        ####################---- FK system mechanics section pre-initialization ----####################
        ################################################################################################

        ########################################################################################
        ####################---- IK controls section pre-initialization ----####################
        self.ik_controls = {}

        self.ik_controls_grps = {}
        for key in self.main_chains:
            if self.main_chains[key] == None or self.main_chains[key] == []:
                self.ik_controls_grps[key] = ""
            else:
                self.ik_controls_grps[key] = "{}_{}_{}DigitIKControls_GRP".format(self.side, self.name, key)

        self.ik_controls_master_grp = "{}_{}_digitsIKControls_GRP".format(self.side, self.name)
        ####################---- FK controls section pre-initialization ----####################
        ########################################################################################

        ################################################################################################
        ####################---- IK system mechanics section pre-initialization ----####################
        self.ik_system_grps = {}
        for key in self.main_chains:
            if self.main_chains[key] == None or self.main_chains[key] == []:
                self.ik_system_grps[key] = ""
            else:
                self.ik_system_grps[key] = "{}_{}_{}Digit_IKSystem_GRP".format(self.side, self.name, key)
        ####################---- IK system mechanics section pre-initialization ----####################
        ################################################################################################


        ###########################################################################################################
        ####################---- main grps for system mechanics section pre-initialization ----####################
        self.main_system_grps = {}
        for key in self.main_chains:
            if self.main_chains[key] == None or self.main_chains[key] == []:
                self.main_system_grps[key] = ""
            else:
                self.main_system_grps[key] = "{}_{}_{}DigitSystems_GRP".format(self.side, self.name, key)
        ####################---- main grps for system mechanics section pre-initialization ----####################
        ###########################################################################################################


        self.master_system_grp = "{}_{}_systems_GRP".format(self.side, self.name)
    
    def create_driver_chains(self):
        """
        """
        if DEBUG_MODE:
            pprint.pprint(self.main_chains)
        for key in self.main_chains:
            if self.main_chains[key] != []:
                if DEBUG_MODE:
                    pprint.pprint(self.main_chains[key])
                tmp_chain = joints_utils.related_clean_joint_chain(self.main_chains[key], self.side, "driver", True)
                self.driver_chains[key] = tmp_chain
                self.module_main_grp(key, self.driver_chains[key][0])
            else:
                self.driver_chains[key] = []


        if DEBUG_MODE:
            print self.driver_chains

        return True

    def fk_system(self):
        """
        """
        for key in self.main_chains.keys():
            if self.main_chains[key] == []:
                self.fk_chains[key] = []
                self.fk_controls[key] = []
            else:
                tmp_chain = joints_utils.related_clean_joint_chain(self.main_chains[key], self.side, "fk", True)
                self.fk_chains[key] = tmp_chain
                
                if DEBUG_MODE:
                    print len(self.fk_chains[key])

                self.fk_controls[key] = []
                for i in range(0, len(self.fk_chains[key])):
                    if DEBUG_MODE:
                        print self.fk_chains[key][i]
                                        
                    if i != len(self.fk_chains[key]) - 1:
                        tmp_ctrl = controller.Control("{}".format(self.fk_chains[key][i][:len(self.fk_chains[key][i])-4]), 1.0, 'pin', self.fk_chains[key][i], self.fk_chains[key][i], '', ['s', 'v'], '', True, True, False)
                        self.fk_controls[key].append(tmp_ctrl)
                        cmds.parentConstraint(self.fk_controls[key][i].get_control(), self.fk_chains[key][i], maintainOffset=True)
                        if i != 0:
                            cmds.parent(self.fk_controls[key][i].get_offset_grp(), self.fk_controls[key][i-1].get_control())
                
                if DEBUG_MODE:
                    print self.fk_controls[key]
                
                # TEMPORARY PARENT CONSTRAINT
                if self.root_space != "":
                    cmds.parentConstraint(self.root_space, self.fk_controls[key][0].get_offset_grp(), maintainOffset=True)

                # clean up the scene
                if cmds.objExists(self.fk_system_grps[key]):
                    cmds.parent(self.fk_chains[key][0], self.fk_system_grps[key])
                else:
                    cmds.group(empty=True, name=self.fk_system_grps[key])
                    cmds.parent(self.fk_chains[key][0], self.fk_system_grps[key])

                self.module_main_grp(key, self.fk_system_grps[key])

                if cmds.objExists(self.fk_controls_master_grp):
                    cmds.parent(self.fk_controls[key][0].get_offset_grp(), self.fk_controls_master_grp)
                else:
                    cmds.group(empty=True, name=self.fk_controls_master_grp)
                    cmds.parent(self.fk_controls[key][0].get_offset_grp(), self.fk_controls_master_grp)


        if DEBUG_MODE:
            pprint.pprint(self.fk_chains)

        return True

    def ik_system(self):
        """
        self.ik_primary_chains = {}
        self.ik_bendy_chains = {}
        """
        for key in self.main_chains.keys():
            if self.main_chains[key] == []:
                self.ik_primary_chains[key] = []
                self.ik_bendy_chains[key] = []
                self.ik_controls[key] = {}
            else:
                # building up the joint chains
                tmp_primary_chain = joints_utils.related_clean_joint_chain(self.main_chains[key], self.side, "ikPrimary", True)
                tmp_bendy_chain = joints_utils.related_clean_joint_chain(self.main_chains[key], self.side, "ikBendy", True)
                self.ik_primary_chains[key] = tmp_primary_chain
                self.ik_bendy_chains[key] = tmp_bendy_chain

                # building the IKHandles
                ik_primary_handle = cmds.ikHandle(name="{}_{}_{}PrimaryChain_IKH".format(self.side, self.name, key), solver="ikRPsolver", startJoint=self.ik_primary_chains[key][0], endEffector=self.ik_primary_chains[key][-1])
                ik_bendy_handle = cmds.ikHandle(name="{}_{}_{}BednyChain_IKH".format(self.side, self.name, key), solver="ikRPsolver", startJoint=self.ik_bendy_chains[key][0], endEffector=self.ik_bendy_chains[key][len(self.ik_bendy_chains[key])-2])

                tmp_dict_ctrls = {
                    "base_CTRL":None,
                    "finger_CTRL":None,
                    "bendy_CTRL":None
                }

                # building the base_CTRL / finger_CTRL / bendy_CTRL
                base_CTRL = controller.Control("{}_{}_{}Base_ik".format(self.side, self.name, key), 1.0, 'pin', self.ik_primary_chains[key][0], self.ik_primary_chains[key][0], '', ['s', 'v'], '', True, True, False)
                tmp_dict_ctrls["base_CTRL"] = base_CTRL
                finger_CTRL = controller.Control("{}_{}_{}_ik".format(self.side, self.name, key), 1.0, 'square', self.ik_primary_chains[key][-1], "", '', ['r', 's', 'v'], '', True, True, False)
                tmp_dict_ctrls["finger_CTRL"] = finger_CTRL
                bendy_CTRL = controller.Control("{}_{}_{}Bendy_ik".format(self.side, self.name, key), 1.0, 'pin', self.ik_bendy_chains[key][-1], self.ik_bendy_chains[key][-1], '', ['t', 's', 'v'], '', True, True, False)
                tmp_dict_ctrls["bendy_CTRL"] = bendy_CTRL

                self.ik_controls[key] = tmp_dict_ctrls

                if DEBUG_MODE:
                    pprint.pprint(self.ik_controls) 

                cmds.parentConstraint(self.ik_controls[key]["base_CTRL"].get_control(), self.ik_primary_chains[key][0], maintainOffset=True)
                cmds.parentConstraint(self.ik_controls[key]["base_CTRL"].get_control(), self.ik_bendy_chains[key][0], maintainOffset=True)
                cmds.parentConstraint(self.ik_primary_chains[key][-1], self.ik_controls[key]["bendy_CTRL"].get_offset_grp(), maintainOffset=True)
                cmds.parentConstraint(self.ik_controls[key]["finger_CTRL"].get_control(), ik_primary_handle[0], maintainOffset=True)
                cmds.parentConstraint(self.ik_controls[key]["bendy_CTRL"].get_control(), ik_bendy_handle[0], maintainOffset=True)

                # poleVectors systems
                polevector_prim_IK = polevectors_utils.pole_vector_complex_plane("{}_{}_{}PrimaryIKHandle".format(self.side, self.name, key), self.ik_primary_chains[key][0], self.ik_primary_chains[key][1], self.ik_primary_chains[key][-1], 1.2)
                polevector_bend_IK = polevectors_utils.pole_vector_complex_plane("{}_{}_{}BendyIKHandle".format(self.side, self.name, key), self.ik_bendy_chains[key][0], self.ik_bendy_chains[key][1], self.ik_bendy_chains[key][2], 1.2)
                cmds.poleVectorConstraint(polevector_prim_IK[0], ik_primary_handle[0])
                cmds.poleVectorConstraint(polevector_bend_IK[0], ik_bendy_handle[0])

                    # noflip poleVector system
                no_flip_prim_IK_off_grp = cmds.group(empty=True, name="{}_{}_{}PrimaryIK_noFlip_offset_GRP".format(self.side, self.name, key))
                no_flip_bend_IK_off_grp = cmds.group(empty=True, name="{}_{}_{}BendyIK_noFlip_offset_GRP".format(self.side, self.name, key))
                no_flip_prim_IK_mod_grp = cmds.group(empty=True, name="{}_{}_{}PrimaryIK_noFlip_modify_GRP".format(self.side, self.name, key))
                cmds.parent(no_flip_prim_IK_mod_grp, no_flip_prim_IK_off_grp)
                no_flip_bend_IK_mod_grp = cmds.group(empty=True, name="{}_{}_{}BendyIK_noFlip_modify_GRP".format(self.side, self.name, key))
                cmds.parent(no_flip_bend_IK_mod_grp, no_flip_bend_IK_off_grp)

                transforms_utils.align_objs(self.ik_primary_chains[key][0], no_flip_prim_IK_off_grp)
                cmds.parentConstraint(self.root_space, no_flip_prim_IK_off_grp, maintainOffset=True)
                cmds.aimConstraint(self.ik_controls[key]["finger_CTRL"].get_control(), no_flip_prim_IK_mod_grp, worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=self.ball_jnt)
                cmds.parent(polevector_prim_IK[1], no_flip_prim_IK_mod_grp)

                transforms_utils.align_objs(self.ik_bendy_chains[key][0], no_flip_bend_IK_off_grp)
                cmds.parentConstraint(self.root_space, no_flip_bend_IK_off_grp, maintainOffset=True)
                cmds.aimConstraint(self.ik_controls[key]["finger_CTRL"].get_control(), no_flip_bend_IK_mod_grp, worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=self.ball_jnt)
                cmds.parent(polevector_bend_IK[1], no_flip_bend_IK_mod_grp)

                # aimConstraint the penultimate  bendyChain's joint to the bendy control
                cmds.aimConstraint(self.ik_controls[key]["bendy_CTRL"].get_control(), self.ik_bendy_chains[key][len(self.ik_bendy_chains[key])-2], worldUpType="objectrotation", worldUpVector=[0, 1, 0], maintainOffset=True, worldUpObject=self.ik_controls[key]["bendy_CTRL"].get_control())

                # TEMPORARY PARENT CONSTRAINT
                cmds.parentConstraint(self.root_space, self.ik_controls[key]["base_CTRL"].get_offset_grp(), maintainOffset=True)

                # clean up the scene
                if cmds.objExists(self.ik_system_grps[key]):
                    cmds.parent([self.ik_bendy_chains[key][0], self.ik_primary_chains[key][0], ik_primary_handle[0], ik_bendy_handle[0], no_flip_prim_IK_off_grp, no_flip_bend_IK_off_grp], self.ik_system_grps[key])

                else:
                    cmds.group(empty=True, name=self.ik_system_grps[key])
                    cmds.parent([self.ik_bendy_chains[key][0], self.ik_primary_chains[key][0], ik_primary_handle[0], ik_bendy_handle[0], no_flip_prim_IK_off_grp, no_flip_bend_IK_off_grp], self.ik_system_grps[key])

                self.module_main_grp(key, self.ik_system_grps[key])

                if cmds.objExists(self.ik_controls_master_grp):
                    cmds.parent([self.ik_controls[key]["base_CTRL"].get_offset_grp(), self.ik_controls[key]["finger_CTRL"].get_offset_grp(), self.ik_controls[key]["bendy_CTRL"].get_offset_grp()], self.ik_controls_master_grp)
                else:
                    cmds.group(empty=True, name=self.ik_controls_master_grp)
                    cmds.parent([self.ik_controls[key]["base_CTRL"].get_offset_grp(), self.ik_controls[key]["finger_CTRL"].get_offset_grp(), self.ik_controls[key]["bendy_CTRL"].get_offset_grp()], self.ik_controls_master_grp)
        
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
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0)
        
        elif cmds.objExists("{}.{}".format(self.central_transform, name_attr)):
            print "central_transform already present"

        else:
            attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0)

        cmds.parent(self.central_transform, self.master_system_grp)

        for key in self.main_chains:
            if self.main_chains[key] != None or self.main_chains[key] != []:
                for i, jnt in enumerate(self.main_chains[key]):
                    driver_pac = cmds.parentConstraint([self.fk_chains[key][i], self.ik_bendy_chains[key][i]], self.driver_chains[key][i], maintainOffset=True)

                    cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chains[key][i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=0.0)
                    cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.fk_chains[key][i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1.0)
                    cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_bendy_chains[key][i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0.0, value=1.0)
                    cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.ik_bendy_chains[key][i]), currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0.0)

                    cmds.setDrivenKeyframe(self.ik_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=1)
                    cmds.setDrivenKeyframe(self.ik_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=0)
                    cmds.setDrivenKeyframe(self.fk_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=0, value=0)
                    cmds.setDrivenKeyframe(self.fk_controls_master_grp, attribute="visibility", currentDriver="{}.{}".format(self.central_transform, name_attr), driverValue=1, value=1)

                    main_pac = cmds.parentConstraint(self.driver_chains[key][i], jnt, maintainOffset=True)


    def module_main_grp(self, key, list_objs):
        """
        re-group all things related to the internal system of the module in one main group

        Args:

        Returns:

        """
        if cmds.objExists(self.main_system_grps[key]):
            cmds.parent(list_objs, self.main_system_grps[key])
        else:
            cmds.group(empty=True, name=self.main_system_grps[key])
            cmds.parent(list_objs, self.main_system_grps[key])

        cmds.setAttr("{}.visibility".format(self.main_system_grps[key]), 0)
        
        return self.main_system_grps[key]

    def run(self):
        """
        """
        self.create_driver_chains()

        self.fk_system()
        self.ik_system()

        # clean up the scene
        for key in self.main_system_grps:
            if self.main_system_grps[key] != "":
                if cmds.objExists(self.master_system_grp):
                    cmds.parent(self.main_system_grps[key], self.master_system_grp)
                else:
                    cmds.group(empty=True, name=self.master_system_grp)
                    cmds.parent(self.main_system_grps[key], self.master_system_grp)

        # make connections between chains
        self.chains_connection()

        # Temporary switch control
        self.switch_ctrl = controller.Control("{}_{}_switch".format(self.side, self.name), 3.0, 'semicircle', '', '', '', ['s', 'v'], '', True, True, False)

        attributes_utils.add_separator(self.switch_ctrl.get_control(), "switchAttribute", by_name=False)
        switch_attr = "switch_IK_FK"
        # attributes_utils.add_float_attr(self.central_transform, name_attr, 0, 1, 0)
        attributes_utils.add_float_attr(self.switch_ctrl.get_control(), switch_attr, 0, 1, 0)
        cmds.connectAttr("{}.{}".format(self.switch_ctrl.get_control(), switch_attr), "{}.{}_{}_switch_IK_FK".format(self.central_transform, self.side, self.name), force=True)

        cmds.xform(self.switch_ctrl.get_offset_grp(), worldSpace=True, translation=self.switch_ctrl_pos)
        cmds.parentConstraint(self.switch_ctrl_parent, self.switch_ctrl.get_offset_grp(), maintainOffset=True)

        if DEBUG_MODE:
            pprint.pprint(self.ik_controls)
            # print self.ik_controls["index"]["finger_CTRL"].get_offset_grp() 

        # cmds.error()

        for key in self.ik_controls:
            if self.ik_controls[key] != {}:
                if DEBUG_MODE:
                    print self.ik_controls[key]["finger_CTRL"].get_offset_grp()
                
                driver_pac = cmds.parentConstraint([self.ball_jnt, self.switch_ctrl.get_control()], self.ik_controls[key]["finger_CTRL"].get_offset_grp(), maintainOffset=True)
                attributes_utils.add_float_attr(self.ik_controls[key]["finger_CTRL"].get_control(), "follow", 0, 10, 0)
                cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.ball_jnt), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), "follow"), driverValue=0.0, value=1.0)
                cmds.setDrivenKeyframe(driver_pac, attribute="{}W0".format(self.ball_jnt), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), "follow"), driverValue=10.0, value=0.0)
                cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.switch_ctrl.get_control()), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), "follow"), driverValue=0.0, value=0.0)
                cmds.setDrivenKeyframe(driver_pac, attribute="{}W1".format(self.switch_ctrl.get_control()), currentDriver="{}.{}".format(self.ik_controls[key]["finger_CTRL"].get_control(), "follow"), driverValue=10.0, value=1.0)


        attributes_utils.add_separator(self.switch_ctrl.get_control(), "FK_curlAttributes", by_name=False)        
        for key in self.fk_controls:
            if self.fk_controls[key] != []:
                name_attr = "{}Curl".format(key)
                attributes_utils.add_float_attr(self.switch_ctrl.get_control(), name_attr)
                for ctrl in self.fk_controls[key]:
                    cmds.connectAttr("{}.{}".format(self.switch_ctrl.get_control(), name_attr), "{}.rotateZ".format(ctrl.get_modify_grp()), force=True)

        self.switch_ctrls_grp = "switchIKFK_drivers_GRP"
        if cmds.objExists(self.switch_ctrls_grp):
            cmds.parent(self.switch_ctrl.get_offset_grp(), self.switch_ctrls_grp)
        else:
            cmds.group(empty=True, name=self.switch_ctrls_grp)
            cmds.parent(self.switch_ctrl.get_offset_grp(), self.switch_ctrls_grp)

        # Temporary stuff
        cmds.setAttr("{}.visibility".format(self.master_system_grp), 0)
        if cmds.objExists("rig_GRP"):
            cmds.parent(self.master_system_grp, "rig_GRP")

        if cmds.objExists("controls_GRP"):
            cmds.parent([self.fk_controls_master_grp, self.ik_controls_master_grp], "controls_GRP")

        return [self.fk_controls, self.ik_controls]
