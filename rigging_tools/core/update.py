import maya.cmds as cmds


def extractCtlShapes(topnode):
    """Extract all ctl shapes
    """
    name = topnode
    allNodes = cmds.listRelatives(topnode, ad=True, f=True)
    ctlShapeList = []
    for node in allNodes:
        if cmds.objectType(node) == "nurbsCurve":
            ctlShapeList = ctlShapeList + [node]
        
    cmds.select(cl=True)
    ctlSet = cmds.sets(n="{0}CtlShapes_set".format(name))
    ctlGroup = cmds.group(n="{0}CtlShapes_grp".format(name), w=True, em=True)
    
    for ctlShape in ctlShapeList:
        if "ctl" in ctlShape.split("|")[-1]:
            shape = cmds.instance(ctlShape)
            dupe = cmds.duplicate(shape, n=ctlShape.split("|")[-1].replace("_ctl", "Extracted_ctl"))[0]
            cmds.delete(shape)
            cmds.parent(dupe, ctlGroup)
            cmds.sets(dupe, add=ctlSet)
            

def updateCtlShapes(topnode, filepath):
    """Update all ctl shapes
    """
    
