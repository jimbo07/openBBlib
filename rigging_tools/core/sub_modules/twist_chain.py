from ..utils import attributes_utils, joints_utils, dag_node, transforms_utils
from decimal import *

reload(attributes_utils)
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

class TwistChain():
    def __init__(
                    self,
                    name,
                    start_trf,
                    end_trf,
                    side = "C", 
                    numb_twist_jnt = 5, 
                    obj_start_up_vector = "",
                    obj_end_up_vector = "",
                    start_axis_up_vector = [0, 1, 0],
                    start_axis_world_up_vector = [0, 1, 0],
                    end_axis_up_vector = [0, 1, 0],
                    end_axis_world_up_vector = [0, 1, 0]
                ):
        """
        Constructor class

        Args:

        Returns:
        
        """

        self.name = name
        self.start_trf = start_trf
        self.end_trf = end_trf
        self.side = side
        self.numb_twist_jnt = numb_twist_jnt 
        self.obj_start_up_vector = obj_start_up_vector
        self.obj_end_up_vector = obj_end_up_vector
        self.start_axis_up_vector = start_axis_up_vector
        self.start_axis_world_up_vector = start_axis_world_up_vector
        self.end_axis_up_vector = end_axis_up_vector
        self.end_axis_world_up_vector = end_axis_world_up_vector
        
        self.start_twist_grp = None
        self.twist_joitns_chain = []
        
        self.main_grp = "{}_{}_twistSystem_GRP".format(self.side, self.name)


    def twist_system(self):
        """
        core part of the clas for building up the twist behaviour of the chain

        Args:

        Returns:
        
        """
        self.twist_joitns_chain = joints_utils.joint_chain_in_between("{}_{}_twistSystem".format(self.side, self.name), self.start_trf, self.end_trf, self.numb_twist_jnt, "X")

        # parenting them in another way
        for i in range(2, self.numb_twist_jnt):
            cmds.parent(self.twist_joitns_chain[i], self.twist_joitns_chain[0])

        cmds.aimConstraint(self.end_trf, self.twist_joitns_chain[0], aimVector=[1, 0, 0], upVector=self.start_axis_up_vector, worldUpType="objectrotation", worldUpVector=self.start_axis_world_up_vector, worldUpObject=self.obj_start_up_vector, maintainOffset=True)
        cmds.aimConstraint(self.start_trf, self.twist_joitns_chain[-1], aimVector=[1, 0, 0], upVector=self.end_axis_up_vector, worldUpType="objectrotation", worldUpVector=self.end_axis_world_up_vector, worldUpObject=self.obj_end_up_vector, maintainOffset=True)
        start_point_cons = cmds.pointConstraint(self.start_trf, self.twist_joitns_chain[0], maintainOffset=True)
        end_point_cons = cmds.pointConstraint(self.end_trf, self.twist_joitns_chain[-1], maintainOffset=True)

        # orient constraint average
        factor = (1.0 / (self.numb_twist_jnt-1))
        for i in range(1, self.numb_twist_jnt-1):
            orient_const = cmds.orientConstraint([self.twist_joitns_chain[0], self.twist_joitns_chain[-1]], self.twist_joitns_chain[i], skip=["y", "z"], maintainOffset=True)
            point_const = cmds.pointConstraint([self.twist_joitns_chain[0], self.twist_joitns_chain[-1]], self.twist_joitns_chain[i], skip=["y", "z"], maintainOffset=True)
            cmds.setAttr("{}.interpType".format(orient_const[0]), 2)

            if i != 1:
                factor = factor + (1.0 / (self.numb_twist_jnt-1))

            if DEBUG_MODE:
                print "factor number is: {}".format(factor)

            cmds.setAttr("{}.{}W0".format(orient_const[0], self.twist_joitns_chain[0]), 1.0 - factor)
            cmds.setAttr("{}.{}W1".format(orient_const[0], self.twist_joitns_chain[-1]), factor)
            cmds.setAttr("{}.{}W0".format(point_const[0], self.twist_joitns_chain[0]), 1.0 - factor)
            cmds.setAttr("{}.{}W1".format(point_const[0], self.twist_joitns_chain[-1]), factor)

            # turn to 0 the offsets:
            cmds.setAttr("{}.offsetX".format(point_const[0]), 0.0)
            cmds.setAttr("{}.offsetY".format(point_const[0]), 0.0)
            cmds.setAttr("{}.offsetZ".format(point_const[0]), 0.0)

        # clean scene
        self.module_main_grp(self.twist_joitns_chain[0])

        for axis in ["X", "Y", "Z"]:
            if (cmds.getAttr("{}.offset{}".format(start_point_cons[0], axis))) != 0:
                cmds.setAttr("{}.offset{}".format(start_point_cons[0], axis), 0.0)
            if (cmds.getAttr("{}.offset{}".format(end_point_cons[0], axis))) != 0:
                cmds.setAttr("{}.offset{}".format(end_point_cons[0], axis), 0.0)

        return True

    def module_main_grp(self, list_objs):
        """
        building up the main group for the sub-module which will contain all the parts built before

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
        Method that run the entire more for building up it

        Args:

        Returns:
        
        """
        self.twist_system()

        # Temporary stuff
        master_grp = "twistSystems_GRP"
        if cmds.objExists(master_grp):
            cmds.parent(self.main_grp, master_grp)
        else:
            cmds.group(empty=True, name=master_grp)
            cmds.parent(self.main_grp, master_grp)
            if cmds.objExists("rig_GRP"):
                cmds.parent(master_grp, "rig_GRP")
        
        return self.twist_joitns_chain
