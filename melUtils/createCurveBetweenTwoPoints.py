import pymel.core as pm
import maya.cmds as cmds

locators = pm.ls(sl=True)

print locators[0].name()
print locators[1].name()

positionLocFirst = pm.pointPosition(locators[0], w=True)
positionLocSecond = pm.pointPosition(locators[1], w=True)

curve = pm.curve(d=1, p=(positionLocFirst, positionLocSecond), n='junction__'+locators[0]+'__'+locators[1]+'__CV')

curveCVs = pm.ls('{0}.cv[:]'.format(curve), fl = True)
count = 0
if curveCVs: # Check if we found any cvs
    for cv in curveCVs:
        print 'Creating {0}'.format(cv)
        cluster = pm.cluster(cv) # Create cluster on a cv
        pm.hide(cluster)
        pm.parent(cluster, locators[count])
        count = count + 1
else:
    cmds.warning('Found no cvs!')
