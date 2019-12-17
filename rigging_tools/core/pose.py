import maya.cmds as cmds
import json
import os

#from collections import OrderedDict
from ooutdmaya.common.util import names
from ooutdmaya.rigging.core import util


basePoseSet = 'pose_set'

def createPoses(node, nameList=[], extra=[], ns=""):
    """ Creates poses specified in the nameList on specified node.
    :param node str: node to add poses to
    :param nameList list: list of pose names
    :param extra list: appends the attributes specified in this list to the default list of attrs
    
    Example:
        from ooutdmaya.rigging.core.util import pose
        reload(pose)
        
        if not cmds.objExists('pose_set'): cmds.sets('pose_set')
        
        mySphere = cmds.polySphere(n="test1_geo", ch=0)[0]
        cmds.addAttr(mySphere, ln="testAttr", at="float", k=True, dv=10)
        pose.createPoses(mySphere, ['default', 'test'], ['testAttr])
    """
    if not node: return
    if not cmds.objExists(ns+node): return
    
    attrList = ['tx', 'ty', 'tz', 
                'rx', 'ry', 'rz', 
                'sx', 'sy', 'sz', 
                'v','rotateOrder']
    
    if extra: attrList = attrList+extra
    
    data = {}
    
    for attr in attrList:
        val = cmds.getAttr("{0}.{1}".format(ns+node, attr))
        data[attr] = val
    
    prettyData = json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))
    
    for name in nameList:
        cmds.addAttr(ns+node, ln=name, dt="string", h=False)
        cmds.setAttr("{0}.{1}".format(ns+node, name), prettyData, type="string")
        
        setName = ns+names.nodeName('set', names.getDescriptor(name), side=names.getSide(name))

        if cmds.objExists(setName):
            cmds.sets(ns+node, add=setName)
        else:
            newSet = util.lib.createNode('objectSet', name=ns+setName)
            cmds.sets(newSet, add=ns+basePoseSet)
            cmds.sets(ns+node, add=newSet)
            
            
def setPose(name, node=None, ns=""):
    """ Reads the attributes off all objects in the specified set (name) and sets those as the set values
    :param name str: name of the pose to set
    :param node str: if specified, only applies the pose on the specified node
    """
    if name == 'default': raise NameError("Can't override the default pose!")
    setName = ns + names.nodeName('set', names.getDescriptor(name), side=names.getSide(name))
    if node: 
        node = node.replace(names.getNS(node), "")
        nodes = [ns+node]
    else: nodes = util.objectSet.getSetContents(setName)
    
    for node in nodes:
        if not cmds.objExists("{0}.{1}".format(node, name)): cmds.error("{0} is not part of the pose {1}".format(node, name))
        data = json.loads(cmds.getAttr("{0}.{1}".format(node, name)))
        
        for attr in data:
            val = cmds.getAttr("{0}.{1}".format(node, attr))
            data[attr] = val
        
        prettyData = json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))
        
        cmds.setAttr("{0}.{1}".format(node, name), prettyData, type="string")
        
        
def applyPose(name, node=None, ns=""):
    """ Applies the pose specified (name) to all objects in the relevant pose set
    :param name str: name of the pose to apply
    """
    setName = ns+names.nodeName('set', names.getDescriptor(ns+name), side=names.getSide(ns+name))
    print setName
    if node: 
        node = node.replace(names.getNS(node), "")
        nodes = [ns+node]
    else: nodes = util.objectSet.getSetContents(setName)
    
    for node in nodes:
        if not cmds.objExists("{0}.{1}".format(node, name)): cmds.error("{0} is not part of the pose {1}".format(node, name))
        data = json.loads(cmds.getAttr("{0}.{1}".format(node, name)))
        
        for attr in data:
            try: cmds.setAttr("{0}.{1}".format(node, attr), data[attr])
            except: continue
            
            
def savePoses(nameList, path, ns=""):
    """ Saves out all poses in nameList to specified path. Creates a new file per pose
    :param nameList list: list of pose names to save out
    :param path str: path to save to, should be in the style "/test/path" and cannot be a file
    """
    if not os.path.exists(path): raise NameError("The path '{0}' does not exist!".format(path))
    for name in nameList:
        setName = names.nodeName('set', names.getDescriptor(name), side=names.getSide(name))
        nodes = util.objectSet.getSetContents(setName)
        data = {}
        for node in nodes:
            data[node] = {}
            if not cmds.objExists("{0}.{1}".format(node, name)): cmds.error("{0} is not part of the pose {1}".format(node, name))
            poseData = json.loads(cmds.getAttr("{0}.{1}".format(node, name)))
            
            for attr in poseData:
                val = cmds.getAttr("{0}.{1}".format(node, attr))
                poseData[attr] = val
            
            data[node] = poseData
            
        prettyData = json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))
        
        # Create a file name
        dataPath = os.path.join(path, name + "Pose.json")
        if os.path.exists(dataPath):
            # os.rename and shutil.move both throws errors, doing it the manual way...
            old = json.loads(open(dataPath).read())
            f = open(dataPath+"OLD", 'w')                    
            prettyData = json.dumps(old, sort_keys=True, indent=3, separators=(',', ': '))
            print >> f, prettyData
            f.close()                  
            os.remove(dataPath)
            
        # Save the data to disc. Running json.dumps and printing line by line returns an easily readable json
        f = open(dataPath, 'w')                    
        prettyData = json.dumps(data, sort_keys=True, indent=3, separators=(',', ': '))
        print >> f, prettyData
        f.close()
    
            
def loadPoses(nameList, path, ns=""):
    """ Tries to load all poses in specified location with specfied names
    :param nameList list : list of pose names to look for
    :param path str: folder to look in
    """
    if not os.path.exists(path): raise NameError("The path '{0}' does not exist!".format(path))
    if not cmds.objExists(ns+basePoseSet): raise ValueError("This scene does not have a base pose set!")
    
    for name in nameList:
        setName = ns + names.nodeName('set', names.getDescriptor(name), side=names.getSide(name))
        if not cmds.objExists(setName): cmds.sets(setName, add=ns+basePoseSet)
        dataPath = os.path.join(path, name + "Pose.json")
        
        data = json.loads(open(dataPath).read())
        
        for node in data:
            if not cmds.objExists("{0}.{1}".format(ns+node, name)): continue            
            newData = {}
            for attr in data[node]:
                val = data[node][attr]
                newData[attr] = val
            
            prettyData = json.dumps(newData, sort_keys=True, indent=3, separators=(',', ': '))
            
            cmds.setAttr("{0}.{1}".format(ns+node, name), prettyData, type="string")
#===============================================================================
# '''
# class Pose():
#     """Class for storing and reading poses on joints
#     
#     Example:
#         from jm_maya.rig.util import pose
#         # TopNodeA is just a random name, change it to match your skeleton grp
#         p = pose.Pose("topNodeA", mode="store", type="A", run=True)
#     
#     Note:
#         As a general rule of thumb, only use this on base skeletons as it can have unpredictable results
#         on helperjoints etc. 
#     
#     Attributes:
#         topnode (str, required): The target from which every joint underneath will be affected
#         mode (str, *optional): Define whether or not we're going to a stored pose or storing a new pose. *Default is store.
#         type (str, required): Can be A, T or P
#             A = A-pose
#             T = T-pose
#             P = Projection-pose
#     
#     """
#     
#     def __init__(self, topnode="", mode="store", run=False, type=""):
#         """Initialize
#         
#         Args:
#             run (bool, optional): If we just want to run immediately, set this to True. Default is false.
# 
#         """
#         self.target = topnode
#         self.mode = mode
#         self.type = type.upper()
#         
#         if run:
#             self.run()
#             
#     def run(self):
#         """Run
#         """
#         # Check if everything has been set correctly
#         if not self.target or not self.mode or not self.type:
#             raise ValueError("Information:\nTarget: {0}\nMode:{1}\nType:{2}\n".format(self.target, self.mode, self.type) + 
#                              "If one of the fields is empty, set it correctly and run again.")
#         
#         # Create list of joints
#         if cmds.objectType(self.target) == "joint":
#             jointList = [self.target] + cmds.listRelatives(self.target, ad=1, c=1, typ="joint")
#         else:
#             jointList = cmds.listRelatives(self.target, ad=1, c=1, typ="joint")        
#         
#         print jointList
#         # If we found joints underneath the target, proceed, else raise error
#         if jointList:
#             # Check the specified mode and proceed accordingly
#             if self.mode == "store":
#                 # Generate name for the pose attribute
#                 poseAttr = self.type + "pose"
#                 
#                 # Loop through the joints and store values one by one
#                 for jnt in jointList:
#                     # Check if the pose already exists
#                     poseExists = cmds.attributeQuery(poseAttr, node=jnt, ex=1)
#                     
#                     # TODO
#                     # Crude approach, change to loops
#                     tx = cmds.getAttr("{0}.{1}".format(jnt, "tx"))
#                     ty = cmds.getAttr("{0}.{1}".format(jnt, "ty"))
#                     tz = cmds.getAttr("{0}.{1}".format(jnt, "tz"))
#                     rx = cmds.getAttr("{0}.{1}".format(jnt, "rx"))
#                     ry = cmds.getAttr("{0}.{1}".format(jnt, "ry"))
#                     rz = cmds.getAttr("{0}.{1}".format(jnt, "rz"))
#                     sx = cmds.getAttr("{0}.{1}".format(jnt, "sx"))
#                     sy = cmds.getAttr("{0}.{1}".format(jnt, "sy"))
#                     sz = cmds.getAttr("{0}.{1}".format(jnt, "sz"))
#                     jox = cmds.getAttr("{0}.{1}".format(jnt, "jointOrientX"))
#                     joy = cmds.getAttr("{0}.{1}".format(jnt, "jointOrientY"))
#                     joz = cmds.getAttr("{0}.{1}".format(jnt, "jointOrientZ"))
#                     
#                     # Create a dictionary with all the attribute values we're interested in
#                     transformDict = {
#                         poseAttr + "Translate":{
#                             poseAttr + "Tx":tx,
#                             poseAttr + "Ty":ty,
#                             poseAttr + "Tz":tz
#                         },
#                         poseAttr + "Rotate":{
#                             poseAttr + "Rx":rx,
#                             poseAttr + "Ry":ry,
#                             poseAttr + "Rz":rz
#                         },
#                         poseAttr + "Scale":{
#                             poseAttr + "Sx":sx,
#                             poseAttr + "Sy":sy,
#                             poseAttr + "Sz":sz
#                         },
#                         poseAttr + "JointOrient":{
#                             poseAttr + "JOx":jox,
#                             poseAttr + "JOy":joy,
#                             poseAttr + "JOz":joz
#                         }
#                     }
#                     
#                     if poseExists:
#                         # Create attribute per transform
#                         for keyAttr in transformDict:
#                             for attr in transformDict[keyAttr]:
#                                 cmds.setAttr("{0}.{1}".format(jnt, attr), l=0)
#                                 cmds.setAttr("{0}.{1}".format(jnt, attr), transformDict[keyAttr][attr], l=1)
#                     
#                     # If pose doesn't already exists, we'll have to create the attributes
#                     else:
#                         # Separator
#                         cmds.addAttr(jnt, ln=poseAttr, niceName=poseAttr, at='enum', en='________', k=0)
#                         
#                         # Add the attributes to a double3 too keep the extra attributes tab relatively clean
#                         for keyAttr in transformDict:
#                             cmds.addAttr(jnt, ln=keyAttr, niceName=keyAttr, at="double3")
#                             for attr in transformDict[keyAttr]:
#                                 cmds.addAttr(jnt, ln=attr, niceName=attr, at="double", p=keyAttr)
#                         
#                         # To make sure the attributes gets created, split loop up into to two to force a refresh
#                         for keyAttr in transformDict:
#                             for attr in transformDict[keyAttr]:
#                                 cmds.setAttr("{0}.{1}".format(jnt, attr), transformDict[keyAttr][attr], l=1)
#                                                         
#             if self.mode == "read":
#                 for jnt in jointList:
#                     poseAttr = self.type + "pose"
#                     
#                     # Test whether or not pose exists, if it doesn't stop the execution
#                     poseExists = poseExists = cmds.attributeQuery(poseAttr, node=jnt, ex=1)
#                     if not poseExists:
#                         raise ValueError("Tried setting a pose ({0}) that doesn't exist".format(self.type))
# 
#                     # TODO
#                     # Crude approach, change to loops
#                     tx = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Tx"))
#                     ty = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Ty"))
#                     tz = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Tz"))
#                     rx = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Rx"))
#                     ry = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Ry"))
#                     rz = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Rz"))
#                     sx = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Sx"))
#                     sy = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Sy"))
#                     sz = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "Sz"))
#                     jox = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "JOx"))
#                     joy = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "JOy"))
#                     joz = cmds.getAttr("{0}.{1}".format(jnt, poseAttr + "JOz"))
#                     
#                     # Define information we're interested in and set them accordingly
#                     attrList = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "jointOrientX", "jointOrientY", "jointOrientZ"]
#                     for z, i in enumerate([tx, ty, tz, rx, ry, rz, sx, sy, sz, jox, joy, joz]):
#                         cmds.setAttr("{0}.{1}".format(jnt, attrList[z]), l=0)
#                         cmds.setAttr("{0}.{1}".format(jnt, attrList[z]), i)
#                 
#         else:
#             raise ValueError("No joints found under {0}, aborting...".format(self.target))
#         
#             
#===============================================================================
