try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

class DagNode():
    def __init__(self, node):
        """
        """
        self.m_obj = OM.MObject()
        self.dag_path = OM.MDagPath()

        selection_list = newOM.MSelectionList()
        selection_list.add( node )

        self.m_obj = selection_list.getDependNode(0)
        self.dag_path = selection_list.getDagPath(0)

    def get_dag_path(self):
        """
        """
        return self.dag_path

    def get_m_obj(self):
        """
        """
        return self.self.m_obj

    def set_dag_path(self, new_dag_path):
        """
        """
        self.dag_path = new_dag_path
        return self.dag_path

    def set_m_obj(self, new_m_obj):
        """
        """
        self.m_obj = new_m_obj
        return self.self.m_obj

    def name( self ):
        """
        """
        nodeFn = OM.MFnDagNode( self.m_obj )
        node_name = nodeFn.fullPathName()

        return node_name

    def parent( self ):
        """
        """
        node_parent = cmds.listRelatives( self.name(), parent = True, f = True )

        if node_parent:
            return DAG_Node( node_parent[0] )

        else:
            return None

    def set_parent( self, parent ):
        cmds.parent( self.name(), parent.name() )
