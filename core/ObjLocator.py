import pymel.core as pm

class ObjLocator:

    def __init__(self, nameObj, textObj, positionObj=[], scaleObj=[]):
        self.nameObj = nameObj
        self.textObj = textObj
        self.positionObj = positionObj
        self.scaleObj = scaleObj
        pm.spaceLocator(n= self.textObj)
        #pm.xform( self.textObj, cp=True)
        pm.xform(self.textObj, r=True, t=(self.positionObj[0], self.positionObj[1], self.positionObj[2]))

    def getPosition():
        self.pos = pm.pointPosition(textObj, w=True)
        return self.pos

    def getObjName(self):
        return self.nameObj

    def getObjText(self):
        return self.textObj

    def addStringAttribute(self, shortName, longName, text):
        pm.addAttr(self.textObj, sn=shortName, ln=longName, dt='string')
        pm.setAttr(self.textObj+'.'+longName, text)

    def addFloatAttribute(self, shortName, longName, minValue, maxValue, defaultValue):
        pm.addAttr(self.textObj, sn=shortName, ln=longName, at='float', dt='double', min=minValue, max=maxValue, dv=defaultValue)
        pm.setAttr(self.textObj+'.'+longName, l=False, k=True)