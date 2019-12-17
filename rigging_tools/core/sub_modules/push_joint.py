from ..utils import attributes_utils, joints_utils, dag_node, transforms_utils

reload(attributes_utils)
reload(joints_utils)
reload(dag_node)
reload(transforms_utils)

try:
    from maya import cmds, mel
    from maya.api import OpenMaya as newOM
    from maya import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

DEBUG_MODE = True

class PushJoint():
    def __init__(
                    self,
                    name,
                    driver_trasform,
                    root_transform,
                    side = "C",
                    x_axis = False,
                    x_axis_inn_off = 0.15,
                    x_axis_out_off = 0.15,
                    x_axis_inn_mul = 2.0,
                    x_axis_out_mul = 1.0,
                    y_axis = True,
                    y_axis_inn_off = 0.15,
                    y_axis_out_off = 0.15,
                    y_axis_inn_mul = 2.0,
                    y_axis_out_mul = 1.0,
                    z_axis = True,
                    z_axis_inn_off = 0.15,
                    z_axis_out_off = 0.15,
                    z_axis_inn_mul = 2.0,
                    z_axis_out_mul = 1.0
                ):
        """
        Constructor class

        Args:

        Returns:
      
        """
        self.name = name
        self.driver_trasform = driver_trasform
        self.root_transform = root_transform
        self.side = side
        self.x_axis = x_axis
        self.x_axis_inn_off = x_axis_inn_off
        self.x_axis_out_off = x_axis_out_off
        self.x_axis_inn_mul = x_axis_inn_mul
        self.x_axis_out_mul = x_axis_out_mul
        self.y_axis = y_axis
        self.y_axis_inn_off = y_axis_inn_off
        self.y_axis_out_off = y_axis_out_off
        self.y_axis_inn_mul = y_axis_inn_mul
        self.y_axis_out_mul = y_axis_out_mul
        self.z_axis = z_axis
        self.z_axis_inn_off = z_axis_inn_off
        self.z_axis_out_off = z_axis_out_off
        self.z_axis_inn_mul = z_axis_inn_mul
        self.z_axis_out_mul = z_axis_out_mul

        self.axis_dict = {
            "X":{
                "axisCheck":self.x_axis,
                "axisInnOff":self.x_axis_inn_off,
                "axisOutOff":self.x_axis_out_off,
                "axisInnMul":self.x_axis_inn_mul,
                "axisOutMul":self.x_axis_out_mul
            },
            "Y":{
                "axisCheck":self.y_axis,
                "axisInnOff":self.y_axis_inn_off,
                "axisOutOff":self.y_axis_out_off,
                "axisInnMul":self.y_axis_inn_mul,
                "axisOutMul":self.y_axis_out_mul
            },
            "Z":{
                "axisCheck":self.z_axis,
                "axisInnOff":self.z_axis_inn_off,
                "axisOutOff":self.z_axis_out_off,
                "axisInnMul":self.z_axis_inn_mul,
                "axisOutMul":self.z_axis_out_mul
            },
        }

        self.main_grp = "{}_{}_pushSystem_GRP".format(self.side, self.name)
        
        self.master_grp = "pushSystem_GRP"


    def push_system(self):
        """
        building up the stretchy system

        Args:

        Returns:
      
        """

        system_objects = []
        for key in self.axis_dict:
            if self.axis_dict[key]["axisCheck"]:
                attributes_utils.add_separator(self.driver_trasform, name_sep="{}axisMultiplierAttrs".format(key))
                for position in ["inner", "outer"]:
                    # creating offset grp
                    offset_grp = cmds.group(empty=True, name="{}_{}_{}axis_{}Offset_GRP".format(self.side, self.name, key, position))
                    transforms_utils.align_objs(self.driver_trasform, offset_grp)
                    cmds.parentConstraint(self.root_transform, offset_grp, maintainOffset=True)

                    # creating push grp
                    push_grp = cmds.group(empty=True, name="{}_{}_{}axis_{}Push_GRP".format(self.side, self.name, key, position))
                    transforms_utils.align_objs(self.driver_trasform, push_grp)
                    cmds.pointConstraint(self.driver_trasform, push_grp, maintainOffset=True)
                    orient_cons_push_grp = cmds.orientConstraint([self.root_transform, self.driver_trasform], push_grp, maintainOffset=True)
                    cmds.setAttr("{}.interpType".format(orient_cons_push_grp[0]), 2)
                    cmds.parent(push_grp, offset_grp)

                    #creating push joints
                    push_jnt = cmds.createNode("joint", name="{}_{}_{}axis_{}Push_JNT".format(self.side, self.name, key, position))
                    transforms_utils.align_objs(self.driver_trasform, push_jnt)
                    cmds.parent(push_jnt, push_grp)
                    cmds.makeIdentity(push_jnt, apply=True, translate=True, rotate=True, scale=True, normal=False, preserveNormals=True)
                    
                    # print self.axis_dict[key]["axisInnOff"]
                    #  cmds.error()

                    if position == "inner":
                        if self.side == "R":
                            cmds.setAttr("{}.translate{}".format(push_jnt, key), self.axis_dict[key]["axisInnOff"] * (-1.0))
                        else:
                            cmds.setAttr("{}.translate{}".format(push_jnt, key), self.axis_dict[key]["axisInnOff"])
                    else:
                        if self.side == "R":
                            cmds.setAttr("{}.translate{}".format(push_jnt, key), self.axis_dict[key]["axisOutOff"])
                        else:
                            cmds.setAttr("{}.translate{}".format(push_jnt, key), self.axis_dict[key]["axisOutOff"] * (-1.0))
                            
                    # start to clean the scene
                    system_objects.append(offset_grp)

                    # creating attribute to drive the quantity of push we want to apply to the final joints
                    mult_attr = "{}axis_{}Multiplier".format(key, position)
                    attributes_utils.add_float_attr(self.driver_trasform, mult_attr, 0)

                    # creating multiplayer nodes and all connections for the final operations
                    divide_degree_mdl = cmds.createNode("multDoubleLinear", name="{}_{}_{}axis_{}DivideDegree_MDL".format(self.side, self.name, key, position))
                    multiplier_mdl = cmds.createNode("multDoubleLinear", name="{}_{}_{}axis_{}Multiplier_MDL".format(self.side, self.name, key, position))
                    inverse_value_mdl = cmds.createNode("multDoubleLinear", name="{}_{}_{}axis_{}InverseValue_MDL".format(self.side, self.name, key, position))
                    condition = cmds.createNode("condition", name="{}_{}_{}axis_{}_CND".format(self.side, self.name, key, position))
                    if position == "inner":
                        if self.side == "R": 
                            cmds.setAttr("{}.operation".format(condition), 2)
                        else:
                            cmds.setAttr("{}.operation".format(condition), 4)
                    else:
                        if self.side == "R":
                            cmds.setAttr("{}.operation".format(condition), 4)
                        else:
                            cmds.setAttr("{}.operation".format(condition), 2)
                    
                    driver_adl = cmds.createNode("addDoubleLinear", name="{}_{}_{}axis_{}{}_ADL".format(self.side, self.name, key, position, self.driver_trasform))
                    
                    if position == "inner":
                        if self.side == "R":
                            cmds.setAttr("{}.input2".format(driver_adl), self.axis_dict[key]["axisInnOff"] * (-1.0))
                        else:
                            cmds.setAttr("{}.input2".format(driver_adl), self.axis_dict[key]["axisInnOff"])
                    else:
                        if self.side == "R":
                            cmds.setAttr("{}.input2".format(driver_adl), self.axis_dict[key]["axisOutOff"])
                        else:
                            cmds.setAttr("{}.input2".format(driver_adl), self.axis_dict[key]["axisOutOff"] * (-1.0))

                    cmds.setAttr("{}.input2".format(divide_degree_mdl), 1.0/360.0)
                    cmds.connectAttr("{}.{}".format(self.driver_trasform, mult_attr), "{}.input1".format(divide_degree_mdl), force=True)
                    cmds.connectAttr("{}.output".format(divide_degree_mdl), "{}.input2".format(multiplier_mdl), force=True)
                    if key == "X":
                        cmds.connectAttr("{}.rotateX".format(self.driver_trasform), "{}.input1".format(multiplier_mdl), force=True)
                    elif key == "Y":
                        cmds.connectAttr("{}.rotateZ".format(self.driver_trasform), "{}.input1".format(multiplier_mdl), force=True)
                    else:
                        cmds.connectAttr("{}.rotateY".format(self.driver_trasform), "{}.input1".format(multiplier_mdl), force=True)
                    
                    if position == "inner":
                        if self.side == "R":
                            cmds.setAttr("{}.input2".format(inverse_value_mdl), -1.0)
                        else:
                            cmds.setAttr("{}.input2".format(inverse_value_mdl), 1.0)
                    else:
                        if self.side == "R":
                            cmds.setAttr("{}.input2".format(inverse_value_mdl), 1.0)
                        else:
                            cmds.setAttr("{}.input2".format(inverse_value_mdl), -1.0)


                    cmds.connectAttr("{}.output".format(multiplier_mdl), "{}.input1".format(inverse_value_mdl), force=True)
                    cmds.connectAttr("{}.output".format(multiplier_mdl), "{}.firstTerm".format(condition), force=True)
                    cmds.connectAttr("{}.output".format(multiplier_mdl), "{}.colorIfFalseR".format(condition), force=True)
                    cmds.connectAttr("{}.output".format(inverse_value_mdl), "{}.colorIfTrueR".format(condition), force=True)
                    cmds.connectAttr("{}.outColorR".format(condition), "{}.input1".format(driver_adl), force=True)

                    cmds.connectAttr("{}.output".format(driver_adl), "{}.translate{}".format(push_jnt, key), force=True)
                    
                    # default values to multiplier attributes
                    if position == "inner":
                        cmds.setAttr("{}.{}".format(self.driver_trasform, mult_attr), self.axis_dict[key]["axisInnMul"])
                    else:
                        cmds.setAttr("{}.{}".format(self.driver_trasform, mult_attr), self.axis_dict[key]["axisOutMul"])

        # cleaning the scene
        self.module_main_grp(system_objects)

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

        self.push_system()

        
        # Temporary stuff
        if not cmds.objExists(self.master_grp):
            cmds.group(empty=True, name=self.master_grp)
            cmds.parent(self.main_grp, self.master_grp)
        else:
            cmds.parent(self.main_grp, self.master_grp)

        if cmds.objExists("rig_GRP"):
            try:
                cmds.parent(self.master_grp, "rig_GRP")
            except:
                print "{} already parented underneath rig_GRP".format(self.master_grp)
        

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
