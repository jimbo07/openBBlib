import pymel.core as pm
#from modulesLib import ModuleCreator

class ModuleSkeleton(ModuleCreator):

    def __init__(self, objName, nameModuleCreator, listLocs):
        self.objName = objName
        self.nameModuleCreator = nameModuleCreator
        self.listLocs = listLocs
        # pm.select("*_LOC")
        # listLocs = pm.ls(sl=True)

        # print listLocs
        listJoints = []
        if self.listLocs == '':
            list = self.nameModuleCreator.getListLocs()
        else:
            list = listLocs

        print list

        jointList = []
        chainFather = ''

        for i in range(0, len(list)):
            positionLocs = pm.pointPosition(list[i], w=True)
            nameLoc = list[i]
            subName = nameLoc[0: len(list[i]) - 3]
            nameJnt = subName + 'JNT'
            pm.joint(p=(positionLocs[0], positionLocs[1], positionLocs[2]), n=nameJnt)
            jointList.append(nameJnt)
            pm.parent(nameJnt, w=True)
            pm.setAttr(nameJnt+'.radius', 0.5)

        for i in range(0, len(list)):
            obj = pm.getAttr(list[i]+'.locFather')
            print '\n\r Loc Father: '+obj+'\n\r'
            if obj != 'self':
                subName = obj[0: len(obj) - 3]
                print '\n\r SubName: ' + subName + '\n\r'
                jointFather = subName + 'JNT'
                pm.parent(jointList[i], jointFather)
            else:
                chainFather = jointList[i]

        pm.joint(chainFather, e=True, oj='yxz', secondaryAxisOrient='zup', ch=True, zso=True);
