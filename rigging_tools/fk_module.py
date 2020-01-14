
from ..utils import attributes_utils, joints_utils, dag_node, transforms_utils
from ..controls import controller

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


class FKModule():
    def __init__(
                    self, 
                    name, 
                    main_chain, 
                    side = "C", 
                    root_space = None,
                    num_fk_ctrls = -1, 
                ):
        """
        Class constructor

        Args:

        Returns:

        """
        self.name = name
        self.side = side
        
        self.main_chain = main_chain
        self.fk_chain = []
        
        self.num_fk_ctrls = num_fk_ctrls

        self.world_space_loc = None
        
        self.root_space = root_space 

        self.fk_controls = []

        self.fk_system_objs = []

        self.fk_ctrls_main_grp = "{}_{}_fkControls_GRP".format(self.side, self.name)

        self.main_grp = "{}_{}_simpleFkSystem_GRP".format(self.side, self.name)

        self.world_space_loc = None
        

    def create_driver_joint_chain(self):
        """
        building up the final driver chain which will drive the final skeleton one

        Args:

        Returns:

        """
        self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)
        self.fk_system_objs.append(self.fk_chain[0])
        return self.fk_chain

    def fk_system(self):
        """
        building up the fk system

        Args:

        Returns:

        """       
        # self.fk_chain = joints_utils.related_clean_joint_chain(self.main_chain, self.side, "fk", True)
        # self.fk_system_objs.append(self.fk_chain[0])

        if self.num_fk_ctrls == -1 or self.num_fk_ctrls == len(self.fk_chain):
            for i, jnt in enumerate(self.fk_chain):
                if i == 0:
                    ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 3.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
                    self.fk_controls.append(ctrl)
                    cmds.parentConstraint(self.fk_controls[i].get_control(), jnt, maintainOffset=True)
                elif i == len(self.fk_chain) - 1:
                    break
                else:
                    ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 3.0, 'circle', jnt, jnt, self.fk_controls[i-1].get_control(), ['s', 'v'], '', True, True, False)
                    self.fk_controls.append(ctrl)
                    cmds.parentConstraint(self.fk_controls[i].get_control(), jnt, maintainOffset=True)
        else:
            print ("WIP PART")
            '''
            joints_numb = len(self.fk_chain)
            ctrl_index_position = self.num_fk_ctrls / joints_numb
            for i, jnt in enumerate(slef.fk_chain):
                if i == 0:
                    ctrl = controller.Control("{}".format(jnt[:len(jnt)-4]), 3.0, 'circle', jnt, jnt, '', ['s', 'v'], '', True, True, False)
                    self.fk_controls.append(ctrl)
                    cmds.parentConstraint(self.fk_controls[i].get_control(), jnt, maintainOffset=True)
            '''

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


    def chains_connection(self):
        """
        create the connections between the two chains - fk and main

        Args:

        Returns:

        """
        grp_objs = []

        for i, jnt in enumerate(self.main_chain):
            main_pac = cmds.parentConstraint(self.fk_chain[i], jnt, maintainOffset=True)

        # clean up the scene
        self.module_main_grp(self.fk_chain[0])


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

        print("###--- Simple FK Module --- START ---###")

        # temporary
        self.world_space_loc = cmds.spaceLocator(name="{}_{}_worldSpace_LOC".format(self.side, self.name))
        world_space_loc_offset_grp = transforms_utils.offset_grps_hierarchy(self.world_space_loc[0])

        self.module_main_grp(world_space_loc_offset_grp[0])

        self.create_driver_joint_chain()

        self.fk_system()

        self.chains_connection()

        # Temporary stuff
        if cmds.objExists("rig_GRP"):
            cmds.parent(self.main_grp, "rig_GRP")
        
        if cmds.objExists("controls_GRP"):
            cmds.parent(self.fk_ctrls_main_grp, "controls_GRP")



