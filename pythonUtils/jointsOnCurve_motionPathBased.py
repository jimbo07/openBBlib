import pymel.core as pm

jointsNumber = 40
groupJnts = 'joint_GRP'
curve = 'curveMP'
motionPathList = []
curveSpans = pm.getAttr(curve + 'Shape.spans')
pm.rebuildCurve(curve, ch=True, rt=0, rpo=True, end=1, kr=0, kep=True, kt=0, d=3, s=curveSpans)
for i in range(0, jointsNumber):
    newJnt = pm.joint(n='twist_' + str(i + 1) + '_JNT', radius=0.5)
    pm.setAttr(newJnt + '.overrideEnabled', 1)
    pm.setAttr(newJnt + '.overrideColor', 13)
    if pm.uniqueObjExists(groupJnts):
        pm.parent(newJnt, groupJnts)
    else:
        pm.group(newJnt, n=groupJnts)
        # motionPath = pm.pathAnimation(newJnt, c=curve, fractionMode = 0, eu = 1)
    motionPath = pm.createNode('motionPath')
    motionPathList.append(motionPath)
    pm.connectAttr(curve + 'Shape.worldSpace[0]', motionPath + '.geometryPath')
    pm.connectAttr(motionPath + '.xCoordinate', newJnt + '.tx', f=True)
    pm.connectAttr(motionPath + '.yCoordinate', newJnt + '.ty', f=True)
    pm.connectAttr(motionPath + '.zCoordinate', newJnt + '.tz', f=True)
    pm.connectAttr(motionPath + '.message', newJnt + '.specifiedManipLocation', f=True)
    maxValueCurve = pm.getAttr(curve + '.maxValue')
    print maxValueCurve
    # pm.cutKey(motionPath+'.u')
    pm.setAttr(motionPath + '.u', i * (maxValueCurve / (jointsNumber - 1)))
    pm.disconnectAttr(newJnt + '.tx')
    pm.disconnectAttr(newJnt + '.ty')
    pm.disconnectAttr(newJnt + '.tz')

jointlist = pm.listRelatives(groupJnts, c=True)
print list
for i in range(0, len(jointlist)):
    if i == 0:
        continue
    else:
        pm.parent(jointlist[i], jointlist[i - 1])

pm.joint(jointlist[0], e=True, oj='yxz', secondaryAxisOrient='zup', ch=True, zso=True);

for i in range(1, len(jointlist)):
    pm.parent(jointlist[i], groupJnts)

for i in range(0, len(motionPathList)):
    pm.connectAttr(motionPathList[i] + '.xCoordinate', jointlist[i] + '.tx', f=True)
    pm.connectAttr(motionPathList[i] + '.yCoordinate', jointlist[i] + '.ty', f=True)
    pm.connectAttr(motionPathList[i] + '.zCoordinate', jointlist[i] + '.tz', f=True)
