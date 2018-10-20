class ModuleCreator(JsonUtils, ObjAnnotation, ObjLocator):

    def __init__(self, objName, jsonFile, side, mirror):
        self.objName = objName
        self.jsonFile = jsonFile
        self.side = side
        self.mirror = mirror

        data = self.jsonFile.readingDataFromJson()
        nameDataJson = self.jsonFile.getJsonName()

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
                textAnn = side + '_' + i['nodeName']
                annotation = ObjAnnotation(nameObj, nameAnn, textAnn, side + '_' + i['nodeChild'],
                                           side + '_' + i['nodeName'], [])
            else:
                nameObj = ('antObj_' + self.side + '_' + i['nodeChild'])
                nameAnn = (self.side + '_' + i['nodeName'] + '_ANT')
                textAnn = side + '_' + i['nodeName']
                annotation = ObjAnnotation(nameObj, nameAnn, textAnn, side + '_' + i['nodeName'], side + '_' + i['nodeName'], [])