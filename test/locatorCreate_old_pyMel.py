import maya.cmds as cmds
import pymel.core as pm
import maya.api.OpenMaya as newOM
import maya.OpenMaya as oldOM


class locatorCreate:

    def __init__(self, nameLocator, position=[], scale=[]):
        self.nl = nameLocator
        self.pos = position
        self.scl = scale

    def createLoc(self):
        self.loc = pm.spaceLocator(n=self.nl, p=(self.pos[0], self.pos[1], self.pos[2]))
        print self.loc

    def float[] getPositionInWorld(self):
        self.locPositionWorld = pm.pointPosition(self.nl, w = True)
        print 'the world positions of '+self.nl+' are: x='+str(self.locPositionWorld[0])+', y='+str(self.locPositionWorld[1])+', z='+str(self.locPositionWorld[2])
        return self.locPositionWorld

    def float[] getPositionInLocal(self):
        self.locPositionLocal = pm.pointPosition(self.nl, l = True)
        print 'the local positions of '+self.nl+' are: x='+str(self.locPositionWorld[0])+', y='+str(self.locPositionWorld[1])+', z='+str(self.locPositionWorld[2])
        return self.locPositionLocal
