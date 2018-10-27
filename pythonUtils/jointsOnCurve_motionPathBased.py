import pymel.core as pm

jointsNumber = 10
groupJnts = 'joint_GRP'
curve = 'curve2'
pm.rebuildCurve(curve, rt=0, s=5)
for i in range(0, 10):
    newJnt = pm.joint(n='twist_'+str(i+1)+'_JNT', radius=0.5)
    if pm.uniqueObjExists(groupJnts):
        pm.parent(newJnt, groupJnts)
    else:
        pm.group(newJnt, n=groupJnts)
    motionPath = pm.pathAnimation(newJnt, c=curve, fractionMode = 0, eu = 1)
    maxValueCurve = pm.getAttr(curve+'.maxValue')
    print maxValueCurve
    #pm.cutKey(motionPath+'.u')
    pm.setAttr(motionPath+'.u', i * (maxValueCurve / (jointsNumber - 1)))
    '''
    pm.disconnectAttr(motionPath+'.u')
    pm.disconnectAttr(newJnt+'.tx')
    pm.disconnectAttr(newJnt+'.ty')
    pm.disconnectAttr(newJnt+'.tz')
    pm.delete(motionPath)

list = pm.listRelatives(groupJnts, c=True)
print list
for i in range(0, len(list)):
    if i == 0:
        continue
    else:
        pm.parent(list[i], list[i-1])
'''