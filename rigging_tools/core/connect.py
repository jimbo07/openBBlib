import maya.cmds as cmds
from ooutdmaya.rigging.core.util import tag, transform, names
from ooutdmaya.rigging.core.util.transform import matrixConstraint

DEFCON = {
    'joint':'attributeConnection',
    'transform':'matrixConstraint'
    }


class Connect():
    """This class interacts with the tags metadata to connect rigs
    
    Example:
        from jm_maya.rig.util import connect
        test = connect.Connect("topNodeA", "topNodeB")
    
    Attributes:
        target (str, optional): Specify the target for the connection if selective connecting is needed.
        topNode (str): Everything below this topNode will be looped through for connect tags and connected
            or disconnected accordingly.
        tagName (str): Everything that should be connected should have this attribute.
        
    """

    def __init__(self, topNodeA, topNodeB, tagName="connectID", target=""):
        """Initialize
        
        """
        self.target = target
        self.topNodeA = topNodeA
        self.topNodeB = topNodeB
        self.tagName = tagName
    
    def add(self):
        """Connect things
        """
        # TODO
        # Connect based off tags rather than tags -> then matching names
        if self.topNodeA and self.topNodeB:
            getTag = tag.Tag()
            getTag.tagName = self.tagName
              
            d1 = getTag._returnDict(self.tagName, "", self.topNodeA)[self.topNodeA]
            d2 = getTag._returnDict(self.tagName, "", self.topNodeB)[self.topNodeB]
                        
            d1ns = names.getNS(self.topNodeA)
            d2ns = names.getNS(self.topNodeB)
            
            added, removed, modified, same = tag.compareDict(d1, d2, ns=1, d1ns=d1ns, d2ns=d2ns)
            
            # TODO
            # Add in different kinds of connections options
            for i in list(same):
                a = d1ns + i
                b = d2ns + i
                if d2[b][self.tagName][0] == "joint":
                    attrList = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
                    for attr in attrList:
                        if not cmds.isConnected("{0}.{1}".format(a, attr), "{0}.{1}".format(b, attr)):
                            cmds.connectAttr("{0}.{1}".format(a, attr), "{0}.{1}".format(b, attr))
                if d2[b][self.tagName][0] == "transform":
                    matrixConstraint(a, b)
            if list(modified):
                print "Did not create any connections for the following:\n {0}\n The connection types did not match!".format(list(modified))
    
    def remove(self):
        """Disconnect things
        """
        if self.topNodeA and self.topNodeB:
            getTag = tag.Tag()
            getTag.tagName = self.tagName
              
            d1 = getTag._returnDict(self.tagName, "", self.topNodeA)[self.topNodeA]
            d2 = getTag._returnDict(self.tagName, "", self.topNodeB)[self.topNodeB]
                        
            d1ns = names.getNS(self.topNodeA)
            d2ns = names.getNS(self.topNodeB)
            
            added, removed, modified, same = tag.compareDict(d1, d2, ns=1, d1ns=d1ns, d2ns=d2ns)
            
            combinedList = list(same) + list(modified)
            for i in combinedList:
                a = d1ns + i
                b = d2ns + i
                if d2[b][self.tagName][0] == "joint":
                    attrList = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
                    for attr in attrList:
                        if cmds.isConnected("{0}.{1}".format(a, attr), "{0}.{1}".format(b, attr)):
                            cmds.disconnectAttr("{0}.{1}".format(a, attr), "{0}.{1}".format(b, attr))
    
    def _getType(self, override=""):
        """Returns the type of connection to be made or removed based type or override.
        
        Args:
            override (str, optional): If this argument is specified, node type will be ignored
                in favor of whatever is specified in the argument.
            
        """
