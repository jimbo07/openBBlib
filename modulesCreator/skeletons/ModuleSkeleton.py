import pymel.core as pm


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

        for i in range(0, len(list)):
            positionLocs = pm.pointPosition(list[i], w=True)
            nameLoc = list[i]
            subName = nameLoc[0: len(list[i]) - 3]
            nameJnt = subName + 'JNT'
            pm.joint(p=(positionLocs[0], positionLocs[1], positionLocs[2]), n=nameJnt)

            pm.parent(nameJnt, w=True)