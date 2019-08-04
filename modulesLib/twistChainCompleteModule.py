from pymel.core import *

#clearCache(all=True)

class twistChainCompleteModule():
    
    def __init__(self, shoulderJoint, elbowJoint, wristJoint):
        self.shoulderJoint = shoulderJoint
        self.elbowJoint = elbowJoint
        self.wristJoint = wristJoint

        side = shoulderJoint[0:1]

        relativeParent = listRelatives(shoulderJoint, p=True)
        fatherJoint = relativeParent[0]
        upperArmGroup = group(empty=True, name=side+"_upperArmTwistChain_GRP")
        transformUpperArmGroup = duplicate(upperArmGroup, name=side+"_transform_upperArmTwistChain_GRP")
        parent(transformUpperArmGroup[0], upperArmGroup)
        transformUpperArmGroupPC = parentConstraint(shoulderJoint, transformUpperArmGroup[0], maintainOffset=True)
        
        if(fatherJoint == 0):
            print("\nfather of joint "+shoulderJoint+" doesn't exist! The module will be parented under kWorld space!!!")
            pcAlign = parentConstraint(shoulderJoint, upperArmGroup, maintainOffset=False)
            delete(pcAlign)
        else:
            pcAlign = parentConstraint(shoulderJoint, upperArmGroup, maintainOffset=False)
            delete(pcAlign)
            parent(upperArmGroup, fatherJoint.name())
            
        shoulderDriverIK = duplicate(shoulderJoint, name=side+"_upperArmTwistChainDriver_start_JNT")
        allDescendentsShoulder = listRelatives(shoulderDriverIK[0], allDescendents=True)
        delete(allDescendentsShoulder[0].name())
        elbowDriverIK = rename(allDescendentsShoulder[1], side+"_upperArmTwistChainDriver_end_JNT")
        
        ikSCDriverSolver = ikHandle(startJoint=shoulderDriverIK[0], endEffector=allDescendentsShoulder[1].shortName(), solver="ikSCsolver", name=side+"_upperArmTwistChainDriver_ikSCHandle")
        ikSCDriverSolverPointC = pointConstraint(elbowJoint, ikSCDriverSolver[0], maintainOffset=True)
        elbowDriverIKOC = orientConstraint(elbowJoint, elbowDriverIK, maintainOffset=True)
        
        parent(shoulderDriverIK[0], upperArmGroup)
        parent(ikSCDriverSolver[0], upperArmGroup)