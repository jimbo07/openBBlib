import pymel.core as pm

class ObjAnnotation:

    def __init__(self, nameObj, textObj, pointObj, startObj, positionObj=[]):
        self.nameObj = nameObj
        self.textObj = textObj
        self.pointObj = pointObj
        self.startObj = startObj
        self.positionObj = positionObj
        if (self.startObj == ''):
            pm.annotate(pointObj, tx=textObj, p=positionObj)
        else:
            pos = pm.xform(startObj, q=True, ws=True, t=True)
            pm.annotate(pointObj, tx=textObj, p=pos)
            pm.parent(textObj, startObj)

    def getObjName(self):
        return self.nameObj

    def getObjText(self):
        return self.textObj

    def getStartingObj(self):
        return self.startObj

    def getPointingObj(self):
        return self.pointObj