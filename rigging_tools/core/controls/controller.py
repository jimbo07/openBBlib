try:
    from maya import cmds, mel
    from maya.api import OpenMaya as OM
except ImportError:
    import traceback
    traceback.print_exc()

from ..utils import transforms_utils

reload(transforms_utils)

class Control():

    def __init__(
                    self,
                    prefix="new",
                    scaleValue=1.0,
                    shape="circle",
                    translateTo="",
                    rotateTo="",
                    parent="",
                    lockChannels=["s", "v"],
                    newController = "",
                    doModify=False,
                    doOffset=True,
                    doDynamicPivot=False,
                ):
        
        """
        class for building rig control
        :param prefix: str, prefix to name new objects
        :param scaleValue: float, scaleValue value for size of control shapes
        :param translateTo: str, reference object for control position
        :param rotateTo: str, reference object for control orientation
        :param parent: str, object to be parent of new control
        :param shape: str, control shape type (normal direction)
        :param lockChannels: list( str ), list of channels on control to be locked and non-keyable
        :param objBBox: str, object to calculate ctrl scaleValue
        :param autoBBox: bool, auto find scaleValue value from Proxy Geo if exist
        :param newController : str, class attrib to get controllerName 
        :return: None
        """

        ctrlObject = None
        circleNormal = [1, 0, 0]        

            
        # default ctrl
        if not ctrlObject:
            ctrlObject = ""
            if shape == "circle":
                ctrlObject = cmds.circle(n=prefix + "_CTRL", ch=False, normal=circleNormal, radius=scaleValue)[0]
            elif shape == "circleFourArrows":
                ctrlObject = self.createCurve_circleFourArrows(prefix + "_CTRL")
            elif shape == "cube":
                ctrlObject = self.createCurve_cube(prefix + "_CTRL")
            elif shape == "sphere":
                ctrlObject = self.createCurve_sphere(prefix + "_CTRL")
            elif shape == "locator":
                ctrlObject = self.createCurve_locator(prefix + "_CTRL")
            elif shape == "square":
                ctrlObject = self.createCurve_square(prefix + "_CTRL")
            elif shape == "triangle":
                ctrlObject = self.createCurve_triangle(prefix + "_CTRL")
            elif shape == "s":
                ctrlObject = self.createCurve_s(prefix + "_CTRL")
            elif shape == "pin":
                ctrlObject = self.createCurve_pin(prefix + "_CTRL")
            elif shape == "cross":
                ctrlObject = self.createCurve_cross(prefix + "_CTRL")

        if doModify:
            ctrlModify = cmds.group(n=prefix + "_modify_GRP", em=1)
            cmds.parent(ctrlObject, ctrlModify)

        if doOffset:
            ctrlOffset = cmds.group(n=prefix + "_offset_GRP", em=1)
            if doModify:
                cmds.parent(ctrlModify, ctrlOffset)
            else:
                cmds.parent(ctrlObject, ctrlOffset)
                

        self.newController = ctrlObject


        
        
        # color control
        ctrlShapes = cmds.listRelatives(ctrlObject, shapes=True)
        for ctrl_shape in ctrlShapes:
            #ctrl_shape.ove.set(1)
            cmds.setAttr("{}.overrideEnabled".format(ctrl_shape),1)
            if prefix.startswith("L_"):
                #ctrl_shape.ovc.set(6)
                cmds.setAttr("{}.overrideColor".format(ctrl_shape),6)

            elif prefix.startswith("R_"):
                #ctrl_shape.ovc.set(13)
                cmds.setAttr("{}.overrideColor".format(ctrl_shape),13)

            else:
                #ctrl_shape.ovc.set(22)
                cmds.setAttr("{}.overrideColor".format(ctrl_shape),22)

        # translate control
        if translateTo != None and translateTo != "":
            if cmds.objExists(translateTo):
                transforms_utils.align_objs(translateTo, ctrlOffset, True, False)

        # rotate control
        if rotateTo != None and rotateTo != "":
            if cmds.objExists(rotateTo):
                transforms_utils.align_objs(translateTo, ctrlOffset, False, True)

        # lock control channels
        singleAttributeLockList = []

        for lockChannel in lockChannels:

            if lockChannel in ["t", "r", "s"]:

                for axis in ["x", "y", "z"]:
                    at = lockChannel + axis
                    singleAttributeLockList.append(at)

            else:
                singleAttributeLockList.append(lockChannel)

        for at in singleAttributeLockList:
            cmds.setAttr(ctrlObject + "." + at, l=1, k=0)
        # add public members
        self.scaleValue = scaleValue
        self.C = ctrlObject
        self.Modify = None
        self.Off = None

        if doOffset:
            self.Off = ctrlOffset
        if doModify:
            self.Modify = ctrlModify

        # parent control
        if parent != None and parent != "":
            if cmds.objExists(parent):
                cmds.parent(self.get_top(), parent)

        self.dynamicPivot = None
        if doDynamicPivot:
            self.dynamicPivot = self.make_dynamic_pivot(prefix, scaleValue, translateTo, rotateTo)  

            
            
    def make_dynamic_pivot(self, prefix, scaleValue, translateTo, rotateTo):        
        pivotCtrl = Control(prefix=prefix+"Pivot", scaleValue=scaleValue, translateTo=translateTo, rotateTo=rotateTo, parent=self.C,
                           shape="sphere", doOffset=True, doDynamicPivot=False)
        pivot_Name = str(pivotCtrl.get_control())
        
        cmds.connectAttr("{}.translateX".format(pivotCtrl.get_control()), "{}.rotatePivotX".format(self.newController), f=True)
        cmds.connectAttr("{}.translateY".format(pivotCtrl.get_control()), "{}.rotatePivotY".format(self.newController), f=True)
        cmds.connectAttr("{}.translateZ".format(pivotCtrl.get_control()), "{}.rotatePivotZ".format(self.newController), f=True)

        # add visibility Attribute on CTRL
        cmds.addAttr(self.newController, ln="PivotVisibility", at="enum", enumName="off:on", k=1, dv=0)        
        pivotOff_Name = pivotCtrl.get_offset_grp()
        cmds.connectAttr("{}.PivotVisibility".format(self.newController), "{}.visibility".format(pivotOff_Name))

            
            
    def get_control(self):
        return self.C

    def get_offset_grp(self):
        """
        Return Offset Grp if exist or NonecreateCurve_circleFourArrows
        :return:
        """
        if self.Off:
            return self.Off
        return None

    def get_modify_grp(self):
        """
        Return Modify Grp if exist or None
        :return:
        """
        if self.Modify:
            return self.Modify
        return None

    def get_top(self):
        """
        Return control's top Grp or Control
        :return:
        """
        if self.Off:
            return self.Off
        elif self.Modify:
            return self.Modify
        else:
            return self.C                       
   


    def createCurve_circleFourArrows(self, name=""):
        """
        Creates a nurbs curve in the shape of a circle with four arrows 
        """
        startCurve1 = cmds.curve(d=3, p=[ (-0.448148, 0, -0.137417), (-0.425577, 0, -0.210319), (-0.345762, 0, -0.345408), (-0.210765, 0, -0.425313), (-0.138183, 0, -0.447335) ], k=[0, 0, 0, 1, 2, 2, 2])
        startCurve2 = cmds.curve(d=1, p=[(-0.138183, 0, -0.447335), (-0.138183, 0, -0.552734), (-0.276367, 0, -0.552734), (0, 0, -0.829101), (0.276367, 0, -0.552734), (0.138183, 0, -0.552734), (0.138183, 0, -0.447335) ], k=[0, 1, 2, 3, 4, 5, 6])
        curve1 = cmds.attachCurve(startCurve1, startCurve2, replaceOriginal=0, kmk=1, ch=0)
        cmds.delete(startCurve1, startCurve2)
        curve2 = cmds.duplicate(curve1)
        cmds.rotate(0, 90, 0, curve1)
        curve3 = cmds.duplicate(curve1)
        cmds.rotate(0, 180, 0, curve3)
        curve4 = cmds.duplicate(curve1)
        cmds.rotate(0, 270, 0, curve4)
        attachCurve1 = cmds.attachCurve(curve1, curve2, replaceOriginal=0, kmk=1, ch=0)
        attachCurve2 = cmds.attachCurve(curve3, curve4, replaceOriginal=0, kmk=1, ch=0)
        cmds.delete(curve1, curve2, curve3, curve4)
        attachCurve2 = cmds.reverseCurve(attachCurve2[0], ch=0, rpo=1)
        newCurve = cmds.attachCurve(attachCurve1[0], attachCurve2[0], replaceOriginal=0, kmk=1, ch=0)
        cmds.delete(attachCurve1[0], attachCurve2[0])
        cmds.makeIdentity(newCurve, apply=1, t=1, r=1, s=1, n=0)
        ret = cmds.rename(newCurve, name)
        return ret


    def createCurve_cube(self, name="cube_ctl"):
        """
        Creates a nurbs curve in the shape of a cube
        """
        return(cmds.curve(name=name, d=1, p=[(-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1), (1, 1, 1), (1, -1, 1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
        

    
    def createCurve_sphere(self, name="sphere_CTL"):
        """
        Creates a nurbs curve in the shape of a sphere
        """
        circle1 = cmds.circle(nr=(1, 0, 0), n=name, ch=False)[0]
        circle2 = cmds.circle(nr=(0, 1, 0), n=name+"1", ch=False)[0]
        circle3 = cmds.circle(nr=(0, 0, 1), n=name+"2", ch=False)[0]
        circle2Shape = cmds.listRelatives(circle2, type="nurbsCurve", children=True)
        circle3Shape = cmds.listRelatives(circle3, type="nurbsCurve", children=True)
        cmds.parent(circle2Shape, circle1, shape=True, relative=True)
        cmds.parent(circle3Shape, circle1, shape=True, relative=True)
        cmds.delete(circle2, circle3)
        #setAttr([circle1], ["v"])
        return circle1


    def createCurve_locator(self, name="locator_ctl"):
        """
        Creates a nurbs curve in the shape of a locator
        """
        return(cmds.curve(name=name, d=1, p=[(0, 1, 0), (0, -1, 0), (0, 0, 0), (-1, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0, 1), (0, 0, -1)], k=[0, 1, 2, 3, 4, 5, 6, 7]))


    def createCurve_circle(self, name="circle_ctl"):
        """
        Creates a nurbs curve in the shape of a circle
        """
        return cmds.circle(n=name, nr=[1, 0, 0], ch=False)[0]


    def createCurve_square(self, name="square_ctl"):
        """
        Creates a nurbs curve in the shape of a square
        """
        return(cmds.curve(n=name, d=1, p=[(1, 0, 1), (-1, 0, 1), (-1, 0, -1), (1, 0, -1), (1, 0, 1)]))


    def createCurve_triangle(self, name="triangle_ctl"):
        """
        Creates a nurbs curve in the shape of a triangle
        """
        return(cmds.curve(n=name, d=1, p=[(0, 0, 0), (2, 0, 0), (0, 1, 0), (0, 0, 0)]))


    def createCurve_s(self, name="s_ctl"):
        """
        Creates a nurbs curve in the shape of a S
        """
        return(cmds.curve(n=name, d=True, p=[(-1, 0, -1), (-1.5, 0, -1), (-2, 0, -.5), (-2, 0, 0), (-2, 0, .5), (-1.5, 0, 1), (-1, 0, 1), (-.5, 0, 1), (0, 0, .5), (0, 0, 0), (0, 0, -.5), (.5, 0, -1), (1, 0, -1), (1.5, 0, -1), (2, 0, -.5), (2, 0, 0), (2, 0, .5), (1.5, 0, 1), (1, 0, 1)]))


    def createCurve_pin(self, name="pin_ctl"):
        """
        Creates a nurbs curve in the shape of a pin
        """
        return(cmds.curve(n=name, d=True, p=[(0, 0, 0), (0, 0.8, 0), (0, 1, 0.2), (0, 1.2, 0), (0, 1, -0.2), (0, 0.8, 0), (-0.2, 1, 0), (0, 1.2, 0), (0.2, 1, 0), (0, 0.8, 0)]))         
        
    def createCurve_cross(self, name="cross"):
        """
        Creates a nurbs curve in the shape of a pin
        """
        return(cmds.curve(n=name, d=True, p=[(1, 0, 1),(3, 0, 1), (3, 0, -1), (1, 0, -1), (1, 0, -3), (-1, 0, -3), (-1, 0, -1), (-3, 0, -1), (-3, 0, 1), (-1, 0, 1), (-1, 0, 3), (1, 0, 3), (1, 0, 1)]))                 

    def add_attrib(self, ctrlName, longname = "", type = "", dv = 0, keyable=True):
        cmds.addAttr(ctrlName, ln=longname, at=type, dv=dv)
        cmds.setAttr("{}.{}".format(ctrlName, longname), keyable=keyable)
