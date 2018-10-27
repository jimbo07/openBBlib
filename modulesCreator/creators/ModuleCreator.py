import pymel.core as pm


class ModuleCreator(JsonUtils, ObjAnnotation, ObjLocator):

    def __init__(self, objName, jsonFile, side, mirror):
        self.objName = objName
        self.jsonFile = jsonFile
        self.side = side
        self.mirror = mirror

        data = self.jsonFile.readingDataFromJson()
        lenght = len(data)
        nameDataJson = self.jsonFile.getJsonName()

        if self.side != '':
            # building locators
            for i in data[nameDataJson]:
                nameObj = ('locObj_' + self.side + '_' + i['nodeName'])
                nameLoc = (self.side + '_' + i['nodeName'])
                position = [i['nodePosX'], i['nodePosY'], i['nodePosZ']]
                scale = [i['nodeSclX'], i['nodeSclY'], i['nodeSclZ']]

                loc = ObjLocator(nameObj, nameLoc, position, scale)
                loc.addStringAttribute('locFather', 'locFather', self.side + i['nodeFather'])
                loc.addStringAttribute('locChild', 'locChild', self.side + i['nodeChild'])

            # building annotations
            for i in data[nameDataJson]:
                if (i['nodeChild'] != 'self'):
                    nameObj = ('antObj_' + self.side + '_' + i['nodeChild'])
                    nameAnn = (self.side + '_' + i['nodeName'] + '_ANT')
                    textAnn = self.side + '_' + i['nodeName']
                    annotation = ObjAnnotation(nameObj, nameAnn, textAnn, self.side + '_' + i['nodeChild'],
                                               self.side + '_' + i['nodeName'], [])
                else:
                    nameObj = ('antObj_' + self.side + '_' + i['nodeChild'])
                    nameAnn = (self.side + '_' + i['nodeName'] + '_ANT')
                    textAnn = self.side + '_' + i['nodeName']
                    annotation = ObjAnnotation(nameObj, nameAnn, textAnn, self.side + '_' + i['nodeName'],
                                               self.side + '_' + i['nodeName'], [])
        else:
            # building locators
            for i in data[nameDataJson]:
                nameObj = ('locObj_' + i['nodeName'])
                nameLoc = (i['nodeName'])
                position = [i['nodePosX'], i['nodePosY'], i['nodePosZ']]
                scale = [i['nodeSclX'], i['nodeSclY'], i['nodeSclZ']]

                loc = ObjLocator(nameObj, nameLoc, position, scale)
                loc.addStringAttribute('locFather', 'locFather', i['nodeFather'])
                loc.addStringAttribute('locChild', 'locChild', i['nodeChild'])

            # building annotations
            for i in data[nameDataJson]:
                if (i['nodeChild'] != 'self'):
                    nameObj = ('antObj_' + i['nodeChild'])
                    nameAnn = (i['nodeName'] + '_ANT')
                    textAnn = i['nodeName']
                    annotation = ObjAnnotation(nameObj, nameAnn, textAnn, i['nodeChild'], i['nodeName'], [])
                else:
                    nameObj = ('antObj_' + i['nodeChild'])
                    nameAnn = (i['nodeName'] + '_ANT')
                    textAnn = i['nodeName']
                    annotation = ObjAnnotation(nameObj, nameAnn, textAnn, i['nodeName'], i['nodeName'], [])

        mainGrpModuleCreator = nameDataJson+'_GRP'

        for i in data[nameDataJson]:
            if pm.uniqueObjExists(mainGrpModuleCreator):
                pm.parent(i['nodeName'], mainGrpModuleCreator)
            else:
                pm.group(i['nodeName'], n=mainGrpModuleCreator)

    def getListLocs(self):
        data = self.jsonFile.readingDataFromJson()
        lenght = len(data)
        nameDataJson = self.jsonFile.getJsonName()

        listLocs = []
        if self.side != '':
            for i in data[nameDataJson]:
                listLocs.insert(len(listLocs), self.side + '_' + i['nodeName'])
        else:
            for i in data[nameDataJson]:
                listLocs.insert(len(listLocs), i['nodeName'])

        return listLocs

        # ------- test for sorting all locs ------ #
        """
        for i in data[nameDataJson]:

            if i['nodeFather'] == 'self' and i['nodeChild'] != 'self':
                listLocs.insert(0, i['nodeName'])
            else if i['nodeFather'] != 'self' and i['nodeChild'] == 'self':
                listLocs.insert(len(listLocs), i['nodeName'])
         """