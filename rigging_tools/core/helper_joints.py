import maya.cmds as cmds
from ooutdmaya.common.util import names


class HelperJoints():
    """
    Create helper joints that'll support better deformation on the rigBound through skinning.
    """
    
    def __init__(self):
        """
        Variables that'll be useful for all the procs are declared here
        """
        
        self.target = ""
        self.jntLen = 0
        self.parentTarget = ""
        self.childTarget = ""
        self.val = 1
        self.aimAxis = "x"
        self.parent = ""
        
    def buildTwist(self, reverse=0, noflip=0, stretch=0):
        """Builds a twist joint setup.
        
        Note:
            Requires at least 3 joints to build (ie. shoulder - elbow - wrist).
        
        Example:
            test = HelperJoints()
            test.target = "joint2"
            test._buildTwist(noflip=1)
        
        Args:
            reverse (bool): Defines whether we're extracting the twist down the chain or up the chain. 
                In a general sense, for a shoulder, reverse should be 0, for an ankle, reverse should be 1.
            noflip (bool): Sets the constraints to noflip mode, allowing 360 degree rotation
            stretch (bool): Toggles whether or not the joint length should be continuesly sampled to "stretch" 
                twist joints along with it whatever it's build inbetween.
            
        """
        # Default args
        if self.target == "": raise ValueError("Tried building twist joint setup without a target (self.target).")
        if self.val == 0: raise ValueError("Tried building twist joint with specified amount (self.val) being 0 (no twist joints)")
        self.side = names.getSide(self.target)
        self.descriptor = names.getDescriptor(self.target)
        if self.side: self.basename = "{0}_{1}_{2}".format(self.side, self.descriptor, "twist")
        else: self.basename = "{0}_{1}".format(self.descriptor, "twist")
        
        # Setup twist grp
        if not cmds.objExists("rigTwist_grp"):
            rigTwistGrp = cmds.group(n="rigTwist_grp", em=1, w=1)
            if self.parent: 
                cmds.parent(rigTwistGrp, self.parent)
            elif cmds.objExists("misc_grp"): 
                    cmds.parent(rigTwistGrp, "misc_grp")
            
        # Check if matrix nodes are loaded
        if not cmds.pluginInfo('matrixNodes', q=1, l=1):
            try: cmds.loadPlugin('matrixNodes')
            except: raise RuntimeError('Unable to load the matrixNodes plugin!')
        
        # Could potentially remove type limitation from this section if needed in the future.
        if self.childTarget == "": self.childTarget = cmds.listRelatives(self.target, c=1, typ="joint")[0]
        if self.parentTarget == "": self.parentTarget = cmds.listRelatives(self.target, p=1, typ="joint")[0]
        if self.jntLen == 0:
            lenFound = 0
            for i in ["x", "y", "z"]:
                if self.aimAxis == i:
                    self.jntLen = cmds.getAttr("{0}.t{1}".format(self.target, i))
                    lenFound = 1
            if not lenFound and not self.jntLen: raise ValueError("Joint length was not specified and the length could not be retrieved automatically")
        
        masterGrp = cmds.group(n=names.addModifier(self.basename, 'grp', addSuffix='Master'), em=1, p="rigTwist_grp")
        cmds.setAttr("{0}.inheritsTransform".format(masterGrp), 0)
        
        # Create dummy setup
        dummyTarget = cmds.duplicate(self.target, po=1, n=names.addModifier(self.basename, 'joint', addSuffix='DummyTarget'))[0]
        dummyParent = cmds.duplicate(self.parentTarget, po=1, n=names.addModifier(self.basename, 'joint', addSuffix='DummyParent'))[0]
        dummyChild = cmds.duplicate(self.childTarget, po=1, n=names.addModifier(self.basename, 'joint', addSuffix='DummyChild'))[0]
        
        cmds.parent(dummyChild, dummyTarget)
        cmds.parent(dummyTarget, dummyParent)
        cmds.parent(dummyParent, masterGrp)

        matchList = [self.target, self.parentTarget, self.childTarget]
        
        for z, i in enumerate([dummyTarget, dummyParent, dummyChild]):
            cmds.parentConstraint(matchList[z], i, n=names.addModifier(i, 'parentConstraint'), mo=0)

        # Create slave joints
        slaveA = cmds.duplicate(dummyTarget, po=1, n=names.addModifier(self.basename, 'joint', addSuffix='SlaveA'))[0]
        if reverse: slaveB = cmds.duplicate(dummyParent, po=1, n=names.addModifier(self.basename, 'joint', addSuffix='SlaveB'))[0]
        else: slaveB = cmds.duplicate(dummyChild, po=1, n=names.addModifier(self.basename, 'joint', addSuffix='SlaveB'))[0]
        cmds.parent(slaveB, slaveA)
        
        # Redundant parenting, just to be sure
        if not cmds.listRelatives(slaveA, p=1, typ="joint")[0] == dummyParent: cmds.parent(slaveA, dummyParent)

        # Create IK to remove the main axis
        rpIK, rpEE = cmds.ikHandle(n=names.addModifier(self.basename, 'ikHandle', addSuffix='Ext'), sj=slaveA, ee=slaveB)
        rpEE = cmds.rename(rpEE, names.addModifier(self.basename, 'endEffector', addSuffix='Ext'))
        cmds.parent(rpIK, dummyTarget)
        cmds.setAttr("{0}.poleVectorX".format(rpIK), 0)
        cmds.setAttr("{0}.poleVectorY".format(rpIK), 0)
        cmds.setAttr("{0}.poleVectorZ".format(rpIK), 0)
        
        # Create space locators that'll help store the current twist value (and visualize for debugging)
        twistValA = cmds.spaceLocator(n=names.addModifier(self.basename, 'locator', addSuffix='A'))[0]
        twistValB = cmds.spaceLocator(n=names.addModifier(self.basename, 'locator', addSuffix='B'))[0]
        cmds.parent(twistValA, twistValB, dummyTarget)
        attrList = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz"]
        for attr in attrList:
            cmds.setAttr(twistValA + attr, 0)
            cmds.setAttr(twistValB + attr, 0)
        
        valAOri = cmds.orientConstraint(slaveA, twistValA, n=names.addModifier(self.basename, 'orientConstraint', addSuffix='A'))[0]
        valBOri = cmds.orientConstraint(slaveA, dummyTarget, twistValB, n=names.addModifier(self.basename, 'orientConstraint', addSuffix='B'))[0]
        
        if noflip: 
            cmds.setAttr("{0}.interpType".format(valAOri), 0)
            cmds.setAttr("{0}.interpType".format(valBOri), 0)
            
        # Create transform for easy attribute access and prep
        twistGrp = cmds.group(n=names.addModifier(self.basename, 'grp', addSuffix='Ext'), em=1, w=1)
        cmds.parent(twistGrp, masterGrp)
        attrList = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz", ".v"]
        for attr in attrList:
            cmds.setAttr(twistGrp + attr, l=1, k=0)
        
        cmds.addAttr(twistGrp, ln="twistValA", k=1)
        cmds.addAttr(twistGrp, ln="twistValB", k=1)
        
        cmds.connectAttr("{0}.rx".format(twistValA), "{0}.twistValA".format(twistGrp))
        
        valBmdl = cmds.createNode("multDoubleLinear", n=names.addModifier(self.basename, 'multDoubleLinear', addSuffix='ValueB'))
        cmds.setAttr("{0}.input2".format(valBmdl), 2)
        cmds.connectAttr("{0}.rx".format(twistValB), "{0}.input1".format(valBmdl))
        cmds.connectAttr("{0}.output".format(valBmdl), "{0}.twistValB".format(twistGrp))
        
        # Create a group for the twist joints to get a better ui result
        jntGrp = cmds.group(n=names.addModifier(self.basename, 'grp', addSuffix='Joints'), em=1, p=masterGrp)
        cmds.parentConstraint(dummyParent, jntGrp, mo=0, n=names.addModifier(self.basename, 'parentConstraint', addSuffix='Joints'))
        
        # Get the placement values for the twist joints
        val = self.val + 1
        jntPlacement = []

        if self.aimAxis.lower() == "y":
            tr = "ty"
        elif self.aimAxis.lower() == "z":
            tr = "tz"
        else:
            tr = "tx"
        self.twistJoints = list()
        for i in range(val):
            i += 1
            if not i == val:
                div = float(i) / float(val)
                jntPlacement = float("{0:.2f}".format(self.jntLen * div))
                curJoint = str(i)
                
                # Create, place and connect twist joints based on extracted information
                jnt = cmds.duplicate(dummyParent, po=1, n=names.addModifier(self.basename, 'joint', addSuffix=curJoint))[0]
                cmds.parent(jnt, jntGrp)
                
                for i in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
                    cmds.setAttr("{0}.{1}".format(jnt, i), 0)
                
                if stretch:
                    stretchMdl = cmds.createNode("multDoubleLinear", n=names.addModifier(self.basename, 'multDoubleLinear', addSuffix=curJoint + "Stretch"))
                    cmds.setAttr("{0}.input2".format(stretchMdl), div)
                    cmds.connectAttr("{0}.{1}".format(dummyTarget, tr), "{0}.input1".format(stretchMdl))
                    cmds.connectAttr("{0}.output".format(stretchMdl), "{0}.{1}".format(jnt, tr))
                        
                else: cmds.setAttr("{0}.{1}".format(jnt, tr), jntPlacement)
                
                twistValmdl = cmds.createNode("multDoubleLinear", n=names.addModifier(self.basename, 'multDoubleLinear', addSuffix=curJoint))
                cmds.setAttr("{0}.input2".format(twistValmdl), (div * -1))
                if noflip: cmds.connectAttr("{0}.twistValB".format(twistGrp), "{0}.input1".format(twistValmdl))
                else: cmds.connectAttr("{0}.twistValA".format(twistGrp), "{0}.input1".format(twistValmdl))
                cmds.connectAttr("{0}.output".format(twistValmdl), "{0}.rx".format(jnt))
                
                # Pretty it up a bit
                cmds.setAttr("{0}.overrideEnabled".format(jnt), 1)
                cmds.setAttr("{0}.radius".format(jnt), 0.5)
                cmds.setAttr("{0}.overrideColor".format(jnt), 12)
                
                # Lock values
                attrList = ["tx", "ty", "tz", "rx", "ry", "rz"]
                for attr in attrList:
                    cmds.setAttr("{0}.{1}".format(jnt, attr), l=1)
                    
                # Assign joints to variable
                self.twistJoints = self.twistJoints + [jnt]
                        
        # Clean up
        cmds.setAttr("{0}.v".format(dummyParent), 0)

    def buildInterp(self, bias=0.0):
        """Build interpolation joint
        
        Note:
            Uses MayaMuscle cSmartConstraint to reliably interpolate a joints rotation between two other joints. Useful
            for skinning tweaks in areas where you need a softer bend, or maintain volume. Changing bias defines how the rotation
            is interpolated between the parent and target joint.
            
            Aim can be x, y, z, -x, -y, -z
        
        Args:
            bias (float): -1 follows parent, 1 follows target
            
        """
        
        # Prep variables and check for prerequisites
        self.side = names.getSide(self.target)
        self.descriptor = names.getDescriptor(self.target)
        self.basename = "{0}_{1}_{2}".format(self.side, self.descriptor, "interp")
        if self.target == "": raise ValueError("Tried building interpolation joint setup without a target.")
        
        if not cmds.pluginInfo('MayaMuscle', q=1, l=1):
            try: cmds.loadPlugin('MayaMuscle')
            except: raise RuntimeError('Unable to load the MayaMuscle plugin!')

        # Setup interp grp
        if not cmds.objExists("rigInterp_grp"):
            rigInterpGrp = cmds.group(n="rigInterp_grp", em=1, w=1)
            if self.parent: 
                cmds.parent(rigInterpGrp, self.parent)
            elif cmds.objExists("misc_grp"): 
                    cmds.parent(rigInterpGrp, "misc_grp")
            
        
        # Create hierarchy
        masterGrp = cmds.group(em=1, n=names.addModifier(self.basename, 'grp'), p="rigInterp_grp")
        cmds.delete(cmds.parentConstraint(self.target, masterGrp, mo=0))
        
        # Create driver joints
        cmds.select(d=1)
        cDrv = cmds.joint(n=names.addModifier(self.basename, 'joint', addSuffix='child'))      
        cmds.select(d=1)
        pDrv = cmds.joint(n=names.addModifier(self.basename, 'joint', addSuffix='parent'))
        cmds.parent(cDrv, pDrv, masterGrp)
        
        # Identify parent joint
        pJnt = cmds.listRelatives(self.target, p=1, typ="joint")[0]
        
        # Match dummy joint placements and move rotation to jointOrientation
        cmds.delete(cmds.parentConstraint(pJnt, pDrv, mo=0))
        cmds.delete(cmds.parentConstraint(self.target, cDrv, mo=0))
        cmds.makeIdentity(pDrv, r=1, a=1)
        cmds.makeIdentity(cDrv, r=1, a=1)
        
        # Create parent constraints
        pParCon = cmds.parentConstraint(pJnt, pDrv, mo=0, n=names.addModifier(pDrv, 'parentConstraint'))
        cParCon = cmds.parentConstraint(self.target, cDrv, mo=0, n=names.addModifier(cDrv, 'parentConstraint'))
        
        # Create the interpolation joint, add helper group structure.
        cmds.select(d=1)
        self.intJnt = cmds.joint(n=names.addModifier(self.basename, 'joint'))
        intOffGrp = cmds.group(em=1, w=1, n=names.addModifier(self.intJnt, 'grp', addSuffix="offset"))
        intConGrp = cmds.group(intOffGrp, w=1, n=names.addModifier(self.intJnt, 'grp', addSuffix="constraint"))
        cmds.delete(cmds.parentConstraint(self.intJnt, intConGrp, mo=0))
        cmds.xform(intOffGrp, ro=(0, 0, 0), t=(0, 0, 0), a=1, ws=1)
        cmds.parent(self.intJnt, intOffGrp)
        
        # Pretty it up a bit
        cmds.setAttr("{0}.overrideEnabled".format(self.intJnt), 1)
        cmds.setAttr("{0}.radius".format(self.intJnt), 1.5)
        cmds.setAttr("{0}.overrideColor".format(self.intJnt), 17)
        
        # Create muscle smart constraint and connect it up
        # Note on the cMuscleSmartConstraint:
        # It has a build in trigger with the ability to adjust the bias. So, say you want it to follow the shoulder more 
        # at values above 90 degrees, but want it to interpolate 50/50 for all rotation values under that, you can do it 
        # by setting a trigger rotation value of 90, and once it hits 90 degrees of rotation, it'll smoothly move bias more 
        # towards the shoulder rather than the elbow.
        
        smartCon = cmds.createNode("cMuscleSmartConstraint", n=names.addModifier(self.basename, 'cMuscleSmartConstraint', addSuffix='constraint'))
        cmds.connectAttr("{0}.worldMatrix".format(pDrv), "{0}.worldMatrixA".format(smartCon))
        cmds.connectAttr("{0}.worldMatrix".format(cDrv), "{0}.worldMatrixB".format(smartCon))
        cmds.connectAttr("{0}.outTranslate".format(smartCon), "{0}.translate".format(self.intJnt))
        cmds.connectAttr("{0}.outRotate".format(smartCon), "{0}.rotate".format(self.intJnt))
        
        # Set axis based on the aim attribute
        axisList = ["x", "y", "z", "-x", "-y", "-z"]
        axisSet = 0
        for z, i in enumerate(axisList):
            if self.aimAxis == i:
                cmds.setAttr("{0}.axis".format(smartCon), z)
                axisSet = 1
        
        if not axisSet:
            cmds.setAttr("{0}.axis".format(smartCon), 0)
        
        # Promote bias attributes etc. to master node for manual adjustments
        cmds.addAttr(masterGrp, ln="customAttributes", nn="__Custom Attributes__", k=1)
        cmds.setAttr("{0}.customAttributes".format(masterGrp), l=1)
        cmds.addAttr(masterGrp, ln="axis",)
        cmds.addAttr(masterGrp, ln="trigger", k=1, min=0, max=180)
        cmds.addAttr(masterGrp, ln="bias", k=1, min=-1, max=1)
        cmds.addAttr(masterGrp, ln="biasAdjust", k=1, min=-2, max=2)
        
        cmds.connectAttr("{0}.trigger".format(masterGrp), "{0}.triggerMin".format(smartCon))
        cmds.connectAttr("{0}.bias".format(masterGrp), "{0}.bias".format(smartCon))
        cmds.connectAttr("{0}.biasAdjust".format(masterGrp), "{0}.biasAdjust".format(smartCon))
        
        # Clean up
        cmds.parent(intConGrp, masterGrp)
        cmds.setAttr("{0}.bias".format(masterGrp), bias)
        cmds.setAttr("{0}.inheritsTransform".format(masterGrp), 0)
        
        for i in [cDrv, pDrv]:
            cmds.setAttr("{0}.v".format(i), 0)
            
        attrList = ["sx", "sy", "sz"]
        for attr in attrList:
            cmds.setAttr("{0}.{1}".format(self.intJnt, attr), l=1)

    def _buildHierarchy(self, target, zeroOff=0):
        """Builds a hierarchy of groups
        
        Note:
            Builds hierarchy like so:
            constraint_grp
                          -> offset_grp
                                       -> target
                                       
        Args:
            target (str): Target which will be put into hierarchy
            zeroOff (bool): Zeros the offset group (to reverse effects of local space)
            
        """
        if not target: raise ValueError("Tried creating offset/constraint group hiearchies without a target")
        
        removeThis = target.split("_")[-1]
        conGrpName = target.replace("_" + removeThis, "") + "Constraint_grp"
        offGrpName = target.replace("_" + removeThis, "") + "Offset_grp"
        
        offGrp = cmds.group(n=offGrpName, em=1, w=1)
        conGrp = cmds.group(offGrp, n=conGrpName, w=1)
        
        cmds.delete(cmds.parentConstraint(target, conGrp, mo=0))
        if zeroOff:
            cmds.xform(offGrp, ro=(0, 0, 0), t=(0, 0, 0), a=1, ws=1)
        cmds.parent(target, offGrp)
        
        return offGrp, conGrp
        
    def prepStretch(self, useTarget=0):
        """Builds placement setup for stretch joints
        
        """
        self.basename = self.side + self.name + "StretchPrep"
        
        sLoc = cmds.spaceLocator(n=self.basename + "Start_loc")
        eLoc = cmds.spaceLocator(n=self.basename + "End_loc")
        uLoc = cmds.spaceLocator(n=self.basename + "Up_loc")
        
        for i in [sLoc, eLoc, uLoc]:
            offGrp, conGrp = self._buildHierarchy(i)
        
    def buildStretch(self):
        """Builds stretch joint setup
        
        Note:
            Builds a joint chain with a stationary joint and a movable joint that'll stretch (if enabled) between
            two locators. Can be used to emulate muscles like the traps, pecs or lats. Don't skin too much to these.
            
        """
        self.basename = self.side + self.name + "Stretch"
    
