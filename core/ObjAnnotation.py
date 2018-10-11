class ObjAnnotation:

    def ___init_(self, nameObj, textObj, pointingObj, startObj, positionObj=[]):
        self.nameObj = nameObj
        self.textObj = textObj
        self.pointingObj = pointingObj
        self.startObj = startObj
        self.positionObj = positionObj
        if (self.startObj == ''):
            pm.annotate(pointingObj, tx=text, p=position)
        else:
            pos = pm.xform(startObj, q=True, t=True)
            pm.annotate(pointingObj, tx=text, p=pos)
            pm.parent(text, startObj)

    def getObjName(self):
        return self.nameObj

    def getObjText(self):
        return self.textObj