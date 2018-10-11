import pymel.core as pm


class ObjLocator:

    def __init__(self, nameObj, textObj, positionObj=[], scaleObj=[]):
        self.nameObj = nameObj
        self.textObj = textObj
        self.positionObj = positionObj
        self.scaleObj = scaleObj
        pm.spaceLocator(n=textObj, p=(positionObj[0], positionObj[1], positionObj[2]))

    def getPosition():
        self.pos = pm.pointPosition(textObj, w=True)
        return self.pos

    def getObjName(self):
        return self.nameObj

    def getObjText(self):
        return self.textObj