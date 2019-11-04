from ..utils import attributes_utils, joints_utils, dag_node, transforms_utils

reload(attributes_utils)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as om
    from maya import OpenMaya as omOld
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class StretchyJoint():
    def __init__(
                    self, 
                    name, 
                    start_trf, 
                    end_trf, 
                    up_trf = "", 
                    side = "m", 
                    twist_chain_enable = False, 
                    numb_twist_jnt = 5, 
                    twist_start_up_vector = "",
                    twist_end_up_vector = "",
                    start_up_vector = [0, 1, 0],
                    start_world_up_vector = [0, 1, 0],
                    end_up_vector = [0, 0, 1],
                    end_world_up_vector = [0, 0, 1],
                    delete_main_trf = False
                ):
        """
        """
        self.name = name
        self.start_trf = start_trf
        self.end_trf = end_trf
        self.up_trf = up_trf
        self.side = side
        self.twist_chain_enable = twist_chain_enable
        self.numb_twist_jnt = numb_twist_jnt
        
        self.twist_start_up_vector = twist_start_up_vector
        self.twist_end_up_vector = twist_end_up_vector

        self.start_up_vector = start_up_vector
        self.start_world_up_vector = start_world_up_vector
        self.end_up_vector = end_up_vector
        self.end_world_up_vector = end_world_up_vector

        self.delete_main_trf = delete_main_trf

        self.start_loc = None
        self.end_loc = None
        self.up_loc = None

        self.start_jnt = None
        self.end_jnt = None

        self.twist_jnts_chain = None
        self.start_twist_grp = None

        self.module_stretchy_objs = []
        self.module_twist_objs = []

        self.main_grp = "{}_{}_stretchySystem_grp".format(self.side, self.name)

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
        
    def get_start_trf(self):
        """
        function for retrieving the main_chain which are used for building the module

        Args:

        Returns:
        
        """
        return self.start_trf

    def get_end_trf(self):
        """
        function for retrieving the children/obj constrained to the root joint of the module

        Args:

        Returns:
        
        """
        return self.end_trf

    def get_up_trf(self):
        """
        function for retrieving the children/obj constrained to the root joint of the module

        Args:

        Returns:
        
        """
        return self.up_trf

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

    def set_start_trf(self, transform):
        """
        function for set the children/obj constrained to the root joint of the module

        Args:

        Returns:
        
        """
        self.start_trf = transform 
        return self.start_trf

    def set_end_trf(self, transform):
        """
        function for set the children/obj constrained to the end joint of the module

        Args:

        Returns:
        
        """
        self.end_trf = transform
        return self.end_trf

    def set_up_trf(self, transform):
        """
        function for set the children/obj constrained to the end joint of the module

        Args:

        Returns:
        
        """
        self.up_trf = transform
        return self.up_trf

    def stretchy(self):
        """
        """

        joint_chain = joints_utils.related_clean_joint_chain([self.start_trf, self.end_trf], self.side, self.name, True)
        self.start_jnt = joint_chain[0]
        self.end_jnt = joint_chain[1]

        if DEBUG_MODE:
            print self.start_trf
            print self.end_trf
            print self.start_jnt
            print self.end_jnt

        # re-orient the last joint as his father
        cmds.joint(self.end_jnt, edit=True, orientJoint="none", children=True, zeroScaleOrient=True)

        cmds.joint(self.start_jnt, edit=True, orientJoint="xyz", secondaryAxisOrient="zdown", children=True, zeroScaleOrient=True)
        cmds.joint(self.end_jnt, edit=True, orientJoint="none", children=True, zeroScaleOrient=True)
        
        # start loc
        self.start_loc = cmds.spaceLocator(name="{}_{}_start_loc".format(self.side, self.name))
        start_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.start_loc[0])
        cmds.delete(cmds.pointConstraint(self.start_trf, start_loc_offset_grp[0], maintainOffset=False))
        cmds.delete(cmds.orientConstraint(self.start_jnt, start_loc_offset_grp[0], maintainOffset=False))

        # end loc
        self.end_loc = cmds.spaceLocator(name="{}_{}_end_loc".format(self.side, self.name))
        end_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.end_loc[0])
        # cmds.delete(cmds.parentConstraint(self.end_trf, end_loc_offset_grp[0], maintainOffset=False))
        cmds.delete(cmds.pointConstraint(self.end_trf, end_loc_offset_grp[0], maintainOffset=False))
        cmds.delete(cmds.orientConstraint(self.end_jnt, end_loc_offset_grp[0], maintainOffset=False))

        # up loc
        if self.up_trf == "":
            self.up_loc = cmds.spaceLocator(name="{}_{}_up_loc".format(self.side, self.name))
            up_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.up_loc[0])
            cmds.delete(cmds.parentConstraint(self.start_trf, up_loc_offset_grp[0], maintainOffset=False))
            cmds.setAttr("{}.translateY".format(up_loc_offset_grp[1]), 10)
        else:
            self.up_loc = cmds.spaceLocator(name="{}_{}_up_loc".format(self.side, self.name))
            up_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.up_loc[0])
            cmds.delete(cmds.parentConstraint(self.up_trf, up_loc_offset_grp[0], maintainOffset=False))
            cmds.delete(cmds.orientConstraint(self.start_jnt, up_loc_offset_grp[0], maintainOffset=False))

        cmds.parentConstraint(self.start_loc, up_loc_offset_grp[0], maintainOffset=True)

        self.module_stretchy_objs.extend([self.start_jnt, start_loc_offset_grp[0], end_loc_offset_grp[0], up_loc_offset_grp[0]])

        # building Ik system
        ik_handle_stretchy = cmds.ikHandle(name="{}_{}_stretchy_ikh".format(self.side, self.name), solver="ikRPsolver", startJoint=self.start_jnt, endEffector=self.end_jnt)
        cmds.poleVectorConstraint(self.up_loc, ik_handle_stretchy[0])
        cmds.parentConstraint(self.start_loc, self.start_jnt, maintainOffset=True)
        cmds.parentConstraint(self.end_loc, ik_handle_stretchy[0], maintainOffset=True)

        self.module_stretchy_objs.append(ik_handle_stretchy[0])

        # building the stretchy behaviour
        distance_node = cmds.createNode("distanceBetween", name="{}_{}_dsb".format(self.side, self.name))
        cmds.connectAttr("{}Shape.worldPosition[0]".format(self.start_loc[0]), "{}.point1".format(distance_node), force=True)
        cmds.connectAttr("{}Shape.worldPosition[0]".format(self.end_loc[0]), "{}.point2".format(distance_node), force=True)

        # self.module_stretchy_objs.append(distance_node)

        stretchy_mld_node = cmds.createNode("multiplyDivide", name="{}_{}_mld".format(self.side, self.name))
        cmds.setAttr("{}.operation".format(stretchy_mld_node), 2)
        self.module_stretchy_objs.append(stretchy_mld_node)
        
        cmds.connectAttr("{}.distance".format(distance_node), "{}.input1X".format(stretchy_mld_node), force=True)
        actual_distance_attr = "actualDistanceValue"
        attributes_utils.add_float_attr(self.start_jnt, actual_distance_attr)
        start_distance_attr = "startDistanceValue"
        attributes_utils.add_float_attr(self.start_jnt, start_distance_attr)

        cmds.connectAttr("{}.distance".format(distance_node), "{}.{}".format(self.start_jnt, actual_distance_attr), force=True)
        cmds.connectAttr("{}.distance".format(distance_node), "{}.{}".format(self.start_jnt, start_distance_attr), force=True)
        cmds.disconnectAttr("{}.distance".format(distance_node), "{}.{}".format(self.start_jnt, start_distance_attr))

        cmds.connectAttr("{}.{}".format(self.start_jnt, start_distance_attr), "{}.input2X".format(stretchy_mld_node), force=True)
        cmds.connectAttr("{}.outputX".format(stretchy_mld_node), "{}.scaleX".format(self.start_jnt), force=True)

        # clean scene
        if self.delete_main_trf:
            if self.up_trf == "":
                cmds.delete([self.start_trf, self.end_trf])
            else:
                cmds.delete([self.start_trf, self.end_trf, self.up_trf])
        
        stretchy_grp = cmds.group(self.module_stretchy_objs, name="{}_{}_stretchy_grp".format(self.side, self.name))
        # cmds.setAttr("{}.visibility".format(stretchy_grp), 0)
        self.module_main_grp(stretchy_grp)

        return True

    def twist_chain(self):
        """
        """
        #building chain of joint
        self.twist_jnts_chain = joints_utils.joint_chain_in_between("{}_{}".format(self.side, self.name), self.start_jnt, self.end_jnt, self.numb_twist_jnt, "X")
        self.module_twist_objs.append(self.twist_jnts_chain[0])        
        '''
        # cmds.parent(self.twist_jnts_chain, world=True)
        
        # parenting them in another way
        self.start_twist_grp = cmds.group(empty=True, name="{}_{}_twistStart_grp".format(self.side, self.name))
        cmds.delete(cmds.parentConstraint(self.start_loc, self.start_twist_grp, maintainOffset=False))

        #for i in range(1, self.numb_twist_jnt):
        cmds.parent(self.twist_jnts_chain, self.start_twist_grp)

        self.module_twist_objs.append(self.start_twist_grp) 
        '''
#######################################################################
        '''
        # aimConstraint -mo -weight 1 -aimVector 1 0 0 -upVector 0 1 0 -worldUpType "object" -worldUpObject locator2;
        cmds.aimConstraint(self.end_loc[0], self.start_twist_grp, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="object", worldUpObject=self.up_loc[0], maintainOffset=True)
        cmds.pointConstraint(self.start_loc[0], self.start_twist_grp, maintainOffset=True)

        # set-up twist feature
        # cmds.orientConstraint(self.end_loc[0], self.twist_jnts_chain[-1], maintainOffset=True)
        mlm_node = cmds.createNode("multMatrix", name="{}_{}_opMatTwist_MLM".format(self.side, self.name))
        dcm_node = cmds.createNode("decomposeMatrix", name="{}_{}_opMatTwist_DCM".format(self.side, self.name))
        qte_node = cmds.createNode("quatToEuler", name="{}_{}_opMatTwist_QTE".format(self.side, self.name))

        cmds.connectAttr("{}.worldMatrix[0]".format(self.end_loc[0]), "{}.matrixIn[0]".format(mlm_node), force=True)
        cmds.connectAttr("{}.worldInverseMatrix[0]".format(self.start_loc[0]), "{}.matrixIn[1]".format(mlm_node), force=True)

        cmds.connectAttr("{}.matrixSum".format(mlm_node), "{}.inputMatrix".format(dcm_node), force=True)
        cmds.connectAttr("{}.outputQuatX".format(dcm_node), "{}.inputQuatX".format(qte_node), force=True)
        cmds.connectAttr("{}.outputQuatW".format(dcm_node), "{}.inputQuatW".format(qte_node), force=True)

        factor = 0.0
        for i in range(0, self.numb_twist_jnt):
            factor_unit = (1.0/self.numb_twist_jnt)
            mld_node = cmds.createNode("multiplyDivide", name="{}_{}{}_opMatTwist_MLD".format(self.side, self.name, i))
            cmds.connectAttr("{}.outputRotateX".format(qte_node), "{}.input1X".format(mld_node), force=True)
            cmds.connectAttr("{}.outputX".format(mld_node), "{}.rotateX".format(self.twist_jnts_chain[i]), force=True)

            if i == 0:
                cmds.setAttr("{}.input2X".format(mld_node), 0.0)
            else:
                factor = factor + factor_unit
                cmds.setAttr("{}.input2X".format(mld_node), factor)
        '''
#######################################################
        '''
        cmds.aimConstraint(self.end_loc[0], start_twist_grp, aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.start_loc[0], maintainOffset=True)
        cmds.pointConstraint(self.start_loc[0], start_twist_grp, maintainOffset=True)

        pos_factor = 0.0
        for i in range(0, self.numb_twist_jnt):
            unit = 1.0 / self.numb_twist_jnt
            point_const = cmds.pointConstraint([self.start_loc[0], self.end_loc[0]], self.twist_jnts_chain[i], maintainOffset=True)
            cmds.setAttr("{}.offsetX".format(point_const[0]), 0.0)
            cmds.setAttr("{}.offsetY".format(point_const[0]), 0.0)
            cmds.setAttr("{}.offsetZ".format(point_const[0]), 0.0)
            
            if i == 0:
                cmds.setAttr("{}.{}W0".format(point_const[0], self.start_loc[0]), 1.0)
                cmds.setAttr("{}.{}W1".format(point_const[0], self.end_loc[0]), 0.0)
            elif i == self.numb_twist_jnt - 1:
                cmds.setAttr("{}.{}W0".format(point_const[0], self.start_loc[0]), 0.0)
                cmds.setAttr("{}.{}W1".format(point_const[0], self.end_loc[0]), 1.0)
            else:
                pos_factor = pos_factor + unit
                print pos_factor
                cmds.setAttr("{}.{}W0".format(point_const[0], self.start_loc[0]), 1.0 - pos_factor)
                cmds.setAttr("{}.{}W1".format(point_const[0], self.end_loc[0]), pos_factor)

        multi_mat_node = cmds.createNode("multMatrix", name="{}_{}_twistSystem_mlt".format(self.side, self.name))
        decomp_mat_node = cmds.createNode("decomposeMatrix", name="{}_{}_twistSystem_dcm".format(self.side, self.name))
        quar_to_eul_node = cmds.createNode("quatToEuler", name="{}_{}_twistSystem_qte".format(self.side, self.name))

        cmds.connectAttr("{}Shape.worldMatrix[0]".format(self.end_loc[0]), "{}.matrixIn[0]".format(multi_mat_node), force=True)
        cmds.connectAttr("{}Shape.worldInverseMatrix[0]".format(self.start_loc[0]), "{}.matrixIn[1]".format(multi_mat_node), force=True)

        cmds.connectAttr("{}.matrixSum".format(multi_mat_node), "{}.inputMatrix".format(decomp_mat_node), force=True)
        cmds.connectAttr("{}.outputQuatX".format(decomp_mat_node), "{}.inputQuatX".format(quar_to_eul_node), force=True)
        cmds.connectAttr("{}.outputQuatW".format(decomp_mat_node), "{}.inputQuatW".format(quar_to_eul_node), force=True)

        factor = 0.0
        for i in range(0, self.numb_twist_jnt):
            unit = 1.0 / self.numb_twist_jnt
            mld_node = cmds.createNode("multiplyDivide", name="{}_{}_twistSystem_mld".format(self.side, self.name))
            cmds.connectAttr("{}.outputRotateX".format(quar_to_eul_node), "{}.input1X".format(mld_node), force=True)
            
            if i == 0:
                cmds.setAttr("{}.input2X".format(mld_node), 0.0)
            else:
                factor = factor + unit
                cmds.setAttr("{}.input2X".format(mld_node), factor)

            # cmds.connectAttr("{}.outputRotateX".format(quar_to_eul_node), "{}.input1X".format(mld_node), force=True)
            cmds.connectAttr("{}.outputX".format(mld_node), "{}.rotateX".format(self.twist_jnts_chain[i]), force=True)
        '''

#######################################################################

        
        # parenting them in another way
        for i in range(2, self.numb_twist_jnt):
            cmds.parent(self.twist_jnts_chain[i], self.twist_jnts_chain[0])

        '''
        self.twist_start_up_vector = twist_start_up_vector
        self.twist_end_up_vector = twist_end_up_vector

        self.start_up_vector = start_up_vector
        self.start_world_up_vector = start_world_up_vector
        self.end_up_vector = end_up_vector
        self.end_world_up_vector = end_world_up_vector
        '''

        # cmds.aimConstraint(self.end_loc[0], self.twist_jnts_chain[0], aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.start_loc[0], maintainOffset=True)
        # cmds.aimConstraint(self.twist_jnts_chain[0], self.twist_jnts_chain[-1], aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.start_trf, maintainOffset=True)
        cmds.aimConstraint(self.end_loc[0], self.twist_jnts_chain[0], aimVector=[1, 0, 0], upVector=self.start_up_vector, worldUpType="objectrotation", worldUpVector=self.start_world_up_vector, worldUpObject=self.twist_start_up_vector, maintainOffset=True)
        cmds.aimConstraint(self.start_loc[0], self.twist_jnts_chain[-1], aimVector=[1, 0, 0], upVector=self.end_up_vector, worldUpType="objectrotation", worldUpVector=self.end_world_up_vector, worldUpObject=self.twist_end_up_vector, maintainOffset=True)
        # cmds.orientConstraint(self.end_loc[0], self.twist_jnts_chain[-1], maintainOffset=True)
        cmds.pointConstraint(self.start_loc[0], self.twist_jnts_chain[0], maintainOffset=True)

        # orient constraint average
        factor = 1.0 / self.numb_twist_jnt
        for i in range(1, self.numb_twist_jnt - 1):
            orient_const = cmds.orientConstraint([self.twist_jnts_chain[0], self.twist_jnts_chain[-1]], self.twist_jnts_chain[i], skip=["y", "z"], maintainOffset=True)
            cmds.setAttr("{}.interpType".format(orient_const[0]), 2)

            if i != 1:
                factor += factor

            cmds.setAttr("{}.{}W0".format(orient_const[0], self.twist_jnts_chain[0]), 1.0 - factor)
            cmds.setAttr("{}.{}W1".format(orient_const[0], self.twist_jnts_chain[-1]), factor)

        # clean scene
        twsit_stretchy_system_grp = cmds.group(self.module_twist_objs, name="{}_{}_twistStretchy_grp".format(self.side, self.name))
        # cmds.setAttr("{}.visibility".format(twsit_stretchy_system_grp), 0)
        self.module_main_grp(twsit_stretchy_system_grp)
        
        return True

    def module_main_grp(self, list_objs):
        """
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
        if self.twist_chain_enable:
            print("###--- Module StretchyJoint --- TwistChain --- START ---###")
        else:
            print("###--- Module StretchyJoint --- START ---###")

        self.stretchy()

        if self.twist_chain_enable:
            self.twist_chain()

        # Temporary stuff
        stretchy_grp = "stretchySystems_grp"
        if not cmds.objExists(stretchy_grp):
            cmds.group(empty=True, name=stretchy_grp)
            cmds.parent(self.main_grp, stretchy_grp)
            if cmds.objExists("rig_grp"):
                cmds.parent(stretchy_grp, "rig_grp")
        else:
            cmds.parent(self.main_grp, stretchy_grp)


'''
#### ---- OLD TWIST CHAIN ---- ####

curve_points = []
for jnt in [self.start_jnt, self.end_jnt]:
    point = cmds.xform(jnt, query=True, worldSpace=True, translation=True)
    curve_points.append(point)

# create curves and rebuilding them
ik_spline_crv = cmds.curve(degree=1, point=curve_points)
ik_spline_crv = cmds.rename(ik_spline_crv, "{}_{}_stretchy_crv".format(self.side, self.name))
self.module_twist_objs.append(ik_spline_crv)

#building chain of joint
self.twist_jnts_chain = joints_utils.joint_chain_in_between("{}_{}".format(self.side, self.name), self.start_jnt, self.end_jnt, self.numb_twist_jnt, "X")
self.module_twist_objs.append(self.twist_jnts_chain[0])

# ik spline solver
ik_spline_solver = cmds.ikHandle(name="{}_{}_stretchySplineSolver_ikh".format(self.side, self.name), solver='ikSplineSolver', startJoint=self.twist_jnts_chain[0], endEffector=self.twist_jnts_chain[-1], createCurve=False, curve=ik_spline_crv)
cmds.setAttr("{}.dTwistControlEnable".format(ik_spline_solver[0]), 1)
cmds.setAttr("{}.dWorldUpType".format(ik_spline_solver[0]), 4)
self.module_twist_objs.append(ik_spline_solver[0])

# twist ik spline solver
cmds.connectAttr("{}.worldMatrix[0]".format(self.start_loc[0]), "{}.dWorldUpMatrix".format(ik_spline_solver[0]), force=True)
cmds.connectAttr("{}.worldMatrix[0]".format(self.end_loc[0]), "{}.dWorldUpMatrixEnd".format(ik_spline_solver[0]), force=True) 

# stretchy spline chain
stretchy_mld_node = cmds.createNode("multiplyDivide", name="{}_{}_stretchy_mld".format(self.side, self.name))
stretchy_cvi_node = cmds.createNode("curveInfo", name="{}_{}_stretchy_cvi".format(self.side, self.name))
cmds.connectAttr("{}Shape.worldSpace[0]".format(ik_spline_crv), "{}.inputCurve".format(stretchy_cvi_node), force=True)
rest_arcLenght_val = cmds.getAttr("{}.arcLength".format(stretchy_cvi_node))
cmds.connectAttr("{}.arcLength".format(stretchy_cvi_node), "{}.input1X".format(stretchy_mld_node), force=True)
cmds.setAttr("{}.input2X".format(stretchy_mld_node), rest_arcLenght_val)
cmds.setAttr("{}.operation".format(stretchy_mld_node), 2)

for jnt in self.twist_jnts_chain:
    cmds.connectAttr("{}.outputX".format(stretchy_mld_node) , "{}.scaleX".format(jnt), force=True)

cmds.skinCluster([self.start_jnt, self.end_jnt], ik_spline_crv)

cmds.setAttr("{}.dWorldUpVectorY".format(ik_spline_solver[0]), 0)
cmds.setAttr("{}.dWorldUpVectorEndY".format(ik_spline_solver[0]), 0)
cmds.setAttr("{}.dWorldUpVectorZ".format(ik_spline_solver[0]), 1)
cmds.setAttr("{}.dWorldUpVectorEndZ".format(ik_spline_solver[0]), 1)

# clean scene
twsit_stretchy_system_grp = cmds.group(self.module_twist_objs, name="{}_{}_twistStretchy_grp".format(self.side, self.name))
# cmds.setAttr("{}.visibility".format(twsit_stretchy_system_grp), 0)
self.module_main_grp(twsit_stretchy_system_grp)
'''
