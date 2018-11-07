import pymel.core as pm

class TwistJointCreator(ModuleSkeleton):

    def __init__(self, objName, jointsNumber, groupJnts, curve, startJoint):

        self.objName = objName
        self.jointsNumber = jointsNumber
        self.groupJnts = groupJnts
        self.curve = curve
        self.startJoint = startJoint

        motionPathList = []
        #curveSpans = pm.getAttr(self.curve + 'Shape.spans')
        if (self.curve == '') or (pm.objExists(self.curve) == False):
            childStartJoint = pm.listRelatives(self.startJoint)
            posStart = pm.xform(self.startJoint, q=True, t=True, ws=True)
            posEnd = pm.xform(childStartJoint, q=True, t=True, ws=True)
            autoGenCv = pm.curve( n=self.startJoint+'_twistJointsChain_CRV', d=1, p=[posStart, posEnd] )
            self.curve = autoGenCv
            pm.rebuildCurve(self.curve, ch=True, rt=0, rpo=True, end=1, kr=0, kep=True, kt=0, d=3, s=4)
        else:
            pm.rebuildCurve(self.curve, ch=True, rt=0, rpo=True, end=1, kr=0, kep=True, kt=0, d=3, s=4)
        
        pm.skinCluster(self.startJoint, childStartJoint, self.curve)
        pm.select(cl=True)
        
        groupTwistJoints = pm.group(n=self.groupJnts)
        
        nameTwistJoint = self.startJoint[0:len(self.startJoint)-4]
        
        for i in range(0, self.jointsNumber):
            newJnt = pm.joint(n=nameTwistJoint+'_twist_' + str(i + 1) + '_JNT', radius=0.25)
            pm.setAttr(newJnt + '.overrideEnabled', 1)
            pm.setAttr(newJnt + '.overrideColor', 13)

            pm.parent(newJnt, groupTwistJoints)

            # motionPath = pm.pathAnimation(newJnt, c=self.curve, fractionMode = 0, eu = 1)
            motionPath = pm.createNode('motionPath')
            motionPathList.append(motionPath)
            pm.connectAttr(self.curve + 'Shape.worldSpace[0]', motionPath + '.geometryPath')
            pm.connectAttr(motionPath + '.xCoordinate', newJnt + '.tx', f=True)
            pm.connectAttr(motionPath + '.yCoordinate', newJnt + '.ty', f=True)
            pm.connectAttr(motionPath + '.zCoordinate', newJnt + '.tz', f=True)
            pm.connectAttr(motionPath + '.message', newJnt + '.specifiedManipLocation', f=True)
            maxValueCurve = pm.getAttr(self.curve + '.maxValue')
            print maxValueCurve
            # pm.cutKey(motionPath+'.u')
            pm.setAttr(motionPath + '.u', i * (maxValueCurve / (self.jointsNumber - 1)))
            pm.disconnectAttr(newJnt + '.tx')
            pm.disconnectAttr(newJnt + '.ty')
            pm.disconnectAttr(newJnt + '.tz')

        jointlist = pm.listRelatives(self.groupJnts, c=True)
        #print list
        for i in range(0, len(jointlist)):
            if i == 0:
                continue
            else:
                pm.parent(jointlist[i], jointlist[i - 1])

        pm.joint(jointlist[0], e=True, oj='yxz', secondaryAxisOrient='zup', ch=True, zso=True);
        pm.joint(jointlist[len(jointlist) - 1], e=True, oj='none', ch=True, zso=True)

        for i in range(1, len(jointlist)):
            pm.parent(jointlist[i], groupTwistJoints)

        for i in range(0, len(motionPathList)):
            pm.connectAttr(motionPathList[i] + '.xCoordinate', jointlist[i] + '.tx', f=True)
            pm.connectAttr(motionPathList[i] + '.yCoordinate', jointlist[i] + '.ty', f=True)
            pm.connectAttr(motionPathList[i] + '.zCoordinate', jointlist[i] + '.tz', f=True)

        #pcGrpJnts = pm.parentConstraint(self.startJoint, groupTwistJoints, mo=False)
        #pm.delete(pcGrpJnts)
        #pm.parent(newJnt, self.groupJnts)

    def getObjName(self):
        return self.objName