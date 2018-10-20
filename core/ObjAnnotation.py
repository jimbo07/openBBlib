import pymel.core as pm

class ObjAnnotation:

    def __init__(self, nameObj, nameAnnotation, textObj, pointObj, startObj, positionObj=[]):
        self.nameObj = nameObj
        self.nameAnnotation = nameAnnotation
        self.textObj = textObj
        self.pointObj = pointObj
        self.startObj = startObj
        self.positionObj = positionObj
        if (self.startObj == ''):
            pm.annotate(self.pointObj, tx=self.textObj, p=self.positionObj)
            pm.rename('annotation1', self.nameAnnotation)
            pm.setAttr(self.nameAnnotation+'.overrideEnabled', 1)
            pm.setAttr(self.nameAnnotation + '.overrideColor', 17)
            pm.setAttr(self.nameAnnotation + '.overrideDisplayType', 2)
        else:
            #pos = pm.xform(self.startObj, q=True, ws=True, t=True)
            pos = pm.pointPosition(self.startObj, w=True)
            pm.annotate(self.pointObj, tx=self.textObj, p=pos)
            pm.rename('annotation1', self.nameAnnotation)
            pm.setAttr(self.nameAnnotation+'.overrideEnabled', 1)
            pm.setAttr(self.nameAnnotation + '.overrideColor', 17)
            pm.setAttr(self.nameAnnotation + '.overrideDisplayType', 2)
            pm.parent(self.nameAnnotation, self.startObj)

    def getObjName(self):
        return self.nameObj

    def getObjText(self):
        return self.textObj

    def getStartingObj(self):
        return self.startObj

    def getPointingObj(self):
        return self.pointObj