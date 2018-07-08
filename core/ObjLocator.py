import pymel.core as pm

class ObjLocator:

    def __init__(self, name, position=[], scale=[]):
        self.name = name
        self.position = position
        self.scale = scale
        pm.spaceLocator(n=name, p=(position[0], position[1]), position[2])

    def float[] getPosition():
        self.pos = pm.pointPosition(name, w=True)
        return pos

