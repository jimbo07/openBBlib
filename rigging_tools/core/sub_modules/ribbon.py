class Ribbon():
    
    def __init__(self ,numJoint,prefix, scaleGrp, defFlag, endC, topC, locatorRotation):
        print locatorRotation
        #self.width     = 0
        self.numJoints = numJoint
        self.prefix    = prefix
        self.scaleGrp  = scaleGrp
        self.defFlag = defFlag
        self.endC = endC
        self.topC = topC
        self.locatorRotation = locatorRotation
        #self.locatorRotation = 90
        
        widthDistance = cmds.distanceDimension('endL','topL')
        cmds.spaceLocator(n='midL')
        cmds.parentConstraint('endL','topL',midLocator)
        self.width = cmds.getAttr('{}.distance'.format(widthDistance))
        self.topPoint  = (self.width/2)
        self.endPoint  = (self.width/2*-1)        
        self.main_grp = "{}_RibbonSystem_GRP".format(self.prefix)


    # GENERAL FUNCTION: ADD ATTRIBUTE(S) ON MULTIPLE OBJECTS
    def addAttribute(self, objects=[], longName='', niceName='', lock=False, **kwargs):
        #For each object
        for obj in objects:
            #For each attribute
            for x in range(0, len(longName)):
                #See if a niceName was defined
                attrNice = '' if not niceName else niceName[x]
                #If the attribute does not exists
                if not cmds.attributeQuery(longName[x], node=obj, exists=True):
                    #Add the attribute
                    cmds.addAttr(obj, longName=longName[x], niceName=attrNice, **kwargs)
                    #If lock was set to True
                    cmds.setAttr((obj + '.' + longName[x]), lock=1) if lock else cmds.setAttr((obj + '.' + longName[x]), lock=0)        
                    
                    
    # GENERAL FUNCTION: CREATE A CONTROL MADE OUT OF A CURVE
    def createCurveCtrl(self, pos=(0,0,0), name='curveCtrl', scale=1, color=6, freezeTransforms=0):
        #Create the controller
        crvCtrl = cmds.curve(p=[(0,1,0),(0,-1,0),(0,0,0),(0,0,1),(0,0,-1),(0,0,0),(1,0,0),(-1,0,0)], d=1)
        crvCtrl = cmds.rename(crvCtrl, name)
        #Set the scale
        cmds.setAttr((crvCtrl + '.scale'), scale, scale, scale)
        cmds.makeIdentity(crvCtrl, apply=True, translate=False, rotate=False, scale=True)
        #Set the color for the curve
        cmds.setAttr((cmds.listRelatives(crvCtrl, shapes=True)[0] + '.overrideEnabled'), 1)
        cmds.setAttr((cmds.listRelatives(crvCtrl, shapes=True)[0] + '.overrideColor'), color)
        #If a position was defined
        if len(pos) == 3:
            #Position the locator
            cmds.setAttr((crvCtrl + '.translate'), pos[0], pos[1], pos[2])
            #If freeze transforms was set to true
            if freezeTransforms:
                cmds.makeIdentity(crvCtrl, apply=True, translate=True)
        #Return the locator
        return crvCtrl  
        

    # GENERAL FUNCTION: CREATE A FOLLICLE AND ATTACH IT TO A SURFACE
    def createFollicle(self, inputSurface=[], scaleGrp='', uVal=0.5, vVal=0.5, hide=1, name='follicle'):
        #Create a follicle
        follicleShape = cmds.createNode('follicle')
        #Get the transform of the follicle
        follicleTrans = cmds.listRelatives(follicleShape, parent=True)[0]
        #Rename the follicle
        follicleTrans = cmds.rename(follicleTrans, name)
        follicleShape = cmds.rename(cmds.listRelatives(follicleTrans, c=True)[0], (name + 'Shape'))
        #If the inputSurface is of type 'nurbsSurface', connect the surface to the follicle
        if cmds.objectType(inputSurface[0]) == 'nurbsSurface':
            cmds.connectAttr((inputSurface[0] + '.local'), (follicleShape + '.inputSurface'))
        #If the inputSurface is of type 'mesh', connect the surface to the follicle
        if cmds.objectType(inputSurface[0]) == 'mesh':
            cmds.connectAttr((inputSurface[0] + '.outMesh'), (follicleShape + '.inputMesh'))
        #Connect the worldMatrix of the surface into the follicleShape
        cmds.connectAttr((inputSurface[0] + '.worldMatrix[0]'), (follicleShape + '.inputWorldMatrix'))
        #Connect the follicleShape to it's transform
        cmds.connectAttr((follicleShape + '.outRotate'), (follicleTrans + '.rotate'))
        cmds.connectAttr((follicleShape + '.outTranslate'), (follicleTrans + '.translate'))
        #Set the uValue and vValue for the current follicle
        cmds.setAttr((follicleShape + '.parameterU'), uVal)
        cmds.setAttr((follicleShape + '.parameterV'), vVal)
        #Lock the translate/rotate of the follicle
        cmds.setAttr((follicleTrans + '.translate'), lock=True)
        cmds.setAttr((follicleTrans + '.rotate'), lock=True)
        #If it was set to be hidden, hide the follicle
        if hide:
            cmds.setAttr((follicleShape + '.visibility'), 0)
        #If a scale-group was defined and exists
        if scaleGrp and cmds.objExists(scaleGrp):
            #Connect the scale-group to the follicle
            cmds.connectAttr((scaleGrp + '.scale'), (follicleTrans + '.scale'))
            #Lock the scale of the follicle
            cmds.setAttr((follicleTrans + '.scale'), lock=True)
        #Return the follicle and it's shape
        return follicleTrans, follicleShape
        
        
    # GENERAL FUNCTION: GROUP MULTIPLE OBJECTS
    def grpObject(self, objects=[], snapTrans=1, snapRot=1, keepHi=1, keepTransforms=1, empty=False, name='', suffix='_grp'):
        #Create a variable to store the groups in
        groups = []
        #For each object passed in
        for obj in objects:
            #Create an empty group for the current object
            newGrp = cmds.group(empty=True, name=(obj + suffix))
            #If a name was specified, rename the group
            if name:
                cmds.rename(newGrp, name)
            #Set the rotateOrder of the current group to the same order as the current object
            cmds.setAttr((newGrp + '.rotateOrder'), cmds.getAttr(obj + '.rotateOrder'))
            #If snapTrans was set to true, PointConstraint the group to the current object
            if snapTrans:
                cmds.delete(cmds.pointConstraint(obj, newGrp))
            #If snapRot was set to true, OrientConstraint the group to the current object
            if snapRot:
                cmds.delete(cmds.orientConstraint(obj, newGrp))
            #If keepHi was set to true
            if keepHi:
                #Get the first parent of the current object
                currParent = cmds.listRelatives(obj, parent=True)
                #If a parent was found, parent the group in the first parent of the current object
                if currParent:
                    cmds.parent(newGrp, currParent[0])
            #If keepTransforms was set to false, Freeze the transformations of the group
            if not keepTransforms:
                cmds.makeIdentity(newGrp, apply=True, translate=True, rotate=True)
            #If empty was set to false, parent the current object into the group
            if not empty:
                cmds.parent(obj, newGrp)
            #Append the current group into the result
            groups.append(newGrp)
        #Return the groups
        return groups
        

    # GENERAL FUNCTION: CREATE A NONLINEAR DEFORMER
    def nonlinearDeformer(self, objects=[], defType=None, lowBound=-1, highBound=1, translate=None, rotate=None, name='nonLinear'):
        #If something went wrong or the type is not valid, raise exception
        if not objects or defType not in ['bend','flare','sine','squash','twist','wave']:
            raise Exception, "function: 'nonlinearDeformer' - Make sure you specified a mesh and a valid deformer"
        #Create and rename the deformer        
        nonLinDef = cmds.nonLinear(objects[0], type=defType, lowBound=lowBound, highBound=highBound)
        nonLinDef[0] = cmds.rename(nonLinDef[0], (name + '_' + defType + '_def'))
        nonLinDef[1] = cmds.rename(nonLinDef[1], (name + '_' + defType + 'Handle'))        
        #If translate was specified, set the translate
        if translate:
            cmds.setAttr((nonLinDef[1] + '.translate'), translate[0], translate[1], translate[2])
        #If rotate was specified, set the rotate
        if rotate:
            cmds.setAttr((nonLinDef[1] + '.rotate'), rotate[0], rotate[1], rotate[2])
        #Return the deformer
        return nonLinDef
            
    # GENERAL FUNCTION: SET PIVOT OF OBJECT(S)
    def setPivot(self, objects=[], rotatePivot=1, scalePivot=1, pivot=(0,0,0)):
        #Make sure the input is passed on as a list
        objects = [objects] if isinstance(objects, (str, unicode)) else objects
        #For each object
        for obj in objects:
            #If rotatePivot was set to True, set the rotatePivot
            if rotatePivot:
                cmds.xform(obj, worldSpace=True, rotatePivot=pivot)
            #If scalePivot was set to True, set the scalePivot
            if scalePivot:
                cmds.xform(obj, worldSpace=True, scalePivot=pivot)
                
    # SCRIPT FUNCTION: LOAD THE SCALE GROUP
    def loadScaleGrp(*args):
        #Get the selected object
        scaleGrp = cmds.ls(selection=True, type="transform")
        #Update the scaleGrpField
        if scaleGrp:
            cmds.textField('scaleGrpField', edit=True, text=scaleGrp[0])                

    def cleanScene(self):
        
        q=cmds.parentConstraint('midL','{}_transform_GRP'.format(self.prefix))
        cmds.delete(q)
        tmp1 = cmds.parentConstraint('endL','{}_end_CTRL'.format(self.prefix))
        tmp2 = cmds.parentConstraint('topL','{}_top_CTRL'.format(self.prefix))
        cmds.delete(tmp1, tmp2,'endL','topL', 'midL', widthDistance,'distanceDimension1')            

    def module_main_grp(self):
        """
        building up the main group for the sub-module which will contain all the parts built before

        Args:

        Returns:
        
        """
        if cmds.objExists(self.main_grp):
            cmds.parent('{}_transform_GRP'.format(self.prefix), self.main_grp)
            cmds.parent('{}_noTransform_GRP'.format(self.prefix), self.main_grp)
        else:
            newG = cmds.group(name=self.main_grp, em=True)
            cmds.parent('{}_transform_GRP'.format(self.prefix),newG)
            cmds.parent('{}_noTransform_GRP'.format(self.prefix),newG)

        #cmds.setAttr("{}.visibility".format(self.main_grp), 0)
        
        #return self.main_grp 

    def createRibbon(self):
        cmds.setAttr("endL.rotateY", self.locatorRotation)        
        cmds.setAttr("topL.rotateY", self.locatorRotation)
        '''#Gather information
        width     = width
        numJoints = numJoint
        prefix    = prefix
        scaleGrp  = scaleGrp
        topPoint  = (width/2)
        endPoint  = (width/2*-1)'''


    	#Create the main groups
    	grpNoTransform = cmds.group(empty=True, name=(self.prefix + '_noTransform_GRP'))
    	grpTransform   = cmds.group(empty=True, name=(self.prefix + '_transform_GRP'))
    	grpCtrl        = cmds.group(empty=True, name=(self.prefix + '_ctrl_GRP'), parent=grpTransform)
    	grpSurface     = cmds.group(empty=True, name=(self.prefix + '_surface_GRP'), parent=grpTransform)
    	grpSurfaces    = cmds.group(empty=True, name=(self.prefix + '_surfaces_GRP'), parent=grpNoTransform)
    	grpDeformers   = cmds.group(empty=True, name=(self.prefix + '_deformer_GRP'), parent=grpNoTransform)
    	grpFollMain    = cmds.group(empty=True, name=(self.prefix + '_follicles_skin_GRP'), parent=grpNoTransform)
    	grpFollVolume  = cmds.group(empty=True, name=(self.prefix + '_follicles_volume_GRP'), parent=grpNoTransform)
    	grpCluster     = cmds.group(empty=True, name=(self.prefix + '_cluster_GRP'), parent=grpNoTransform)
    	grpMisc        = cmds.group(empty=True, name=(self.prefix + '_misc_GRP'), parent=grpNoTransform)


    	#Create a NURBS-plane to use as a base
    	tmpPlane = cmds.nurbsPlane(axis=(0,1,0), width=self.width, lengthRatio=(1.0 / self.width), u=self.numJoints, v=1, degree=3, ch=0)[0]
    	#Create the NURBS-planes to use in the setup
    	geoPlane       = cmds.duplicate(tmpPlane, name=(self.prefix + 'GEO'))
    	geoPlaneWire   = cmds.duplicate(tmpPlane, name=(self.prefix + 'wire_blnd_GEO'))
        if (self.defFlag == True):
            geoPlaneTwist  = cmds.duplicate(tmpPlane, name=(self.prefix + 'twist_blnd_GEO'))
            geoPlaneSine   = cmds.duplicate(tmpPlane, name=(self.prefix + 'sine_blnd_GEO'))
            geoPlaneVolume = cmds.duplicate(tmpPlane, name=(self.prefix + 'volume_GEO'))
            #Offset the volume-plane
            cmds.setAttr((geoPlaneVolume[0] + '.translateZ'), -0.5)

    	'''geoPlane       = cmds.duplicate(tmpPlane, name=(self.prefix + 'GEO'))
    	geoPlaneTwist  = cmds.duplicate(tmpPlane, name=(self.prefix + 'twist_blnd_GEO'))
    	geoPlaneSine   = cmds.duplicate(tmpPlane, name=(self.prefix + 'sine_blnd_GEO'))
    	geoPlaneWire   = cmds.duplicate(tmpPlane, name=(self.prefix + 'wire_blnd_GEO'))
    	geoPlaneVolume = cmds.duplicate(tmpPlane, name=(self.prefix + 'volume_GEO'))'''
    	

    	#Delete the base surface
    	cmds.delete(tmpPlane)


    	#Create the controllers
    	ctrlTop = self.createCurveCtrl(name=(self.prefix + '_top_CTRL'), freezeTransforms=1, color=9, pos=(self.topPoint,0,0))
    	ctrlMid = self.createCurveCtrl(name=(self.prefix + '_mid_CTRL'), freezeTransforms=1, color=9, pos=(0,0,0))
    	ctrlEnd = self.createCurveCtrl(name=(self.prefix + '_end_CTRL'), freezeTransforms=1, color=9, pos=(self.endPoint,0,0))
    	#Group the controllers
    	grpTop = self.grpObject(objects=[ctrlTop], snapTrans=1, keepTransforms=0, keepHi=1, empty=0, suffix='_GRP')[0]
    	grpMid = self.grpObject(objects=[ctrlMid], snapTrans=1, keepTransforms=0, keepHi=1, empty=0, suffix='_GRP')[0]
    	grpEnd = self.grpObject(objects=[ctrlEnd], snapTrans=1, keepTransforms=0, keepHi=1, empty=0, suffix='_GRP')[0]
    	#PointConstraint the midCtrl between the top/end
    	midConst = cmds.pointConstraint(ctrlTop, ctrlEnd, grpMid)
    	#Create deformers: Wire deformer
        deformCrv = cmds.curve(p=[(self.topPoint,0,0),(0,0,0),(self.endPoint,0,0)], degree=2)
    	deformCrv = cmds.rename(deformCrv, (self.prefix + 'ribbon_wire_CRV'))
    	wireDef = cmds.wire(geoPlaneWire, dds=(0,15), wire=deformCrv)
    	wireDef[0] = cmds.rename(wireDef[0], (geoPlaneWire[0] + '_WIRE'))
    	#Create deformers: Clusters
    	clsTop = cmds.cluster((deformCrv + '.cv[0:1]'), relative=1)
    	clsMid = cmds.cluster((deformCrv + '.cv[1]'), relative=1)
    	clsEnd = cmds.cluster((deformCrv + '.cv[1:2]'), relative=1)
    	clsTop[0] = cmds.rename(clsTop[0], (ctrlTop + '_top_cluster'))
    	clsTop[1] = cmds.rename(clsTop[1], (ctrlTop + '_top_clusterHandle'))
    	clsMid[0] = cmds.rename(clsMid[0], (ctrlMid + '_mid_cluster'))
    	clsMid[1] = cmds.rename(clsMid[1], (ctrlMid + '_mid_clusterHandle'))
    	clsEnd[0] = cmds.rename(clsEnd[0], (ctrlEnd + '_end_cluster'))
    	clsEnd[1] = cmds.rename(clsEnd[1], (ctrlEnd + '_end_clusterHandle'))
    	cmds.setAttr((cmds.listRelatives(clsTop[1], type="shape")[0] + '.originX'), self.topPoint)
    	cmds.setAttr((cmds.listRelatives(clsEnd[1], type="shape")[0] + '.originX'), self.endPoint)
    	self.setPivot(objects=[clsTop[1]], rotatePivot=1, scalePivot=1, pivot=(self.topPoint,0,0))
    	self.setPivot(objects=[clsEnd[1]], rotatePivot=1, scalePivot=1, pivot=(self.endPoint,0,0))
        cmds.percent(clsTop[0], (deformCrv + '.cv[1]'), v=0.5)
    	cmds.percent(clsEnd[0], (deformCrv + '.cv[1]'), v=0.5)
    	posTopPma = cmds.shadingNode('plusMinusAverage', asUtility=1, name = (self.prefix + 'top_ctrl_pos_pma'))
    	cmds.connectAttr((ctrlTop + '.translate'), (posTopPma + '.input3D[0]'))
    	cmds.connectAttr((grpTop + '.translate'), (posTopPma + '.input3D[1]'))
    	posEndPma = cmds.shadingNode('plusMinusAverage', asUtility=1, name = (self.prefix + 'end_ctrl_pos_pma'))
    	cmds.connectAttr((ctrlEnd + '.translate'), (posEndPma + '.input3D[0]'))
    	cmds.connectAttr((grpEnd + '.translate'), (posEndPma + '.input3D[1]'))
    	cmds.connectAttr((posTopPma + '.output3D'), (clsTop[1] + '.translate'))
    	cmds.connectAttr((ctrlMid + '.translate'), (clsMid[1] + '.translate'))
    	cmds.connectAttr((posEndPma + '.output3D'), (clsEnd[1] + '.translate'))
    	#Create deformers: Blendshape
    	
    	

        if (self.defFlag == True):
            blndDef = cmds.blendShape(geoPlaneWire[0], geoPlaneTwist[0], geoPlaneSine[0], geoPlane[0], name=(self.prefix + 'blendShape'),weight=[(0,1),(1,1),(2,1)])
            #Add attributes: Twist/Roll attributes
    	    self.addAttribute(objects=[ctrlTop,ctrlMid,ctrlEnd],longName=['twistSep'],niceName=['---------------'],at="enum",en='Twist',lock=1,k=True)
    	    self.addAttribute(objects=[ctrlTop,ctrlEnd],longName=['twist'],at="float",k=True)
    	    self.addAttribute(objects=[ctrlTop,ctrlEnd],longName=['twistOffset'],at="float",k=True)
    	    self.addAttribute(objects=[ctrlTop,ctrlEnd],longName=['affectToMid'],at="float",min=0, max=10,dv=10,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['roll'],at="float",k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['rollOffset'],at="float",k=True)
    	    #Add attributes: Volume attributes
    	    self.addAttribute(objects=[ctrlMid],longName=['volumeSep'],niceName=['---------------'],at="enum",en='Volume',lock=1,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['volume'],at="float",min=-1,max=1,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['volumeMultiplier'],at="float",min=1,dv=3,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['startDropoff'],at="float",min=0, max=1, dv=1,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['endDropoff'],at="float",min=0, max=1, dv=1, k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['volumeScale'],at="float",min=self.endPoint*0.9, max=self.topPoint*2,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['volumePosition'],min=self.endPoint,max=self.topPoint,at="float",k=True)
    	    #Add attributes: Sine attributes
    	    self.addAttribute(objects=[ctrlMid], longName=['sineSep'], niceName=['---------------'], attributeType='enum', en="Sine:", keyable=True, lock=1)
    	    self.addAttribute(objects=[ctrlMid], longName=['amplitude'], attributeType="float", keyable=True)
    	    self.addAttribute(objects=[ctrlMid], longName=['offset'], attributeType="float", keyable=True)
    	    self.addAttribute(objects=[ctrlMid], longName=['twist'], attributeType="float", keyable=True)
    	    self.addAttribute(objects=[ctrlMid], longName=['sineLength'], min=0.1, dv=2, attributeType="float", keyable=True)
    	    #Add attributes: Extra attributes
    	    self.addAttribute(objects=[ctrlMid],longName=['extraSep'],niceName=['---------------'],at="enum",en='Extra',lock=1,k=True)
    	    self.addAttribute(objects=[ctrlMid],longName=['showExtraCtrl'],at="enum",en='Hide:Show:',k=True)
    	    cmds.setAttr((ctrlMid + '.showExtraCtrl'), 1)


    	    #Create deformers: Twist deformer, Sine deformer, Squash deformer
    	    twistDef  = self.nonlinearDeformer(objects=[geoPlaneTwist[0]],  defType='twist',  name=geoPlaneTwist[0],  lowBound=-1, highBound=1, rotate=(0,0,90))
    	    sineDef   = self.nonlinearDeformer(objects=[geoPlaneSine[0]],   defType='sine',   name=geoPlaneSine[0],   lowBound=-1, highBound=1, rotate=(0,0,90))
    	    squashDef = self.nonlinearDeformer(objects=[geoPlaneVolume[0]], defType='squash', name=geoPlaneVolume[0], lowBound=-1, highBound=1, rotate=(0,0,90))
    	    cmds.setAttr((sineDef[0] + '.dropoff'), 1)
    	    

            #Twist deformer: Sum the twist and the roll
            sumTopPma = cmds.shadingNode('plusMinusAverage', asUtility=1, name = (self.prefix + 'twist_top_sum_pma'))
            cmds.connectAttr((ctrlTop + '.twist'), (sumTopPma + '.input1D[0]'))
            cmds.connectAttr((ctrlTop + '.twistOffset'), (sumTopPma + '.input1D[1]'))
            cmds.connectAttr((ctrlMid + '.roll'), (sumTopPma + '.input1D[2]'))
            cmds.connectAttr((ctrlMid + '.rollOffset'), (sumTopPma + '.input1D[3]'))
            cmds.connectAttr((sumTopPma + '.output1D'), (twistDef[0] + '.startAngle'))
            sumEndPma = cmds.shadingNode('plusMinusAverage', asUtility=1, name = (self.prefix + 'twist_low_sum_pma'))
            cmds.connectAttr((ctrlEnd + '.twist'), (sumEndPma + '.input1D[0]'))
            cmds.connectAttr((ctrlEnd + '.twistOffset'), (sumEndPma + '.input1D[1]'))
            cmds.connectAttr((ctrlMid + '.roll'), (sumEndPma + '.input1D[2]'))
            cmds.connectAttr((ctrlMid + '.rollOffset'), (sumEndPma + '.input1D[3]'))
            cmds.connectAttr((sumEndPma + '.output1D'), (twistDef[0] + '.endAngle'))
            #Twist deformer: Set up the affect of the deformer
            topAffMdl = cmds.shadingNode('multDoubleLinear', asUtility=1, name = (self.prefix + 'twist_top_affect_mdl'))
            cmds.setAttr((topAffMdl + '.input1'), -0.1)
            cmds.connectAttr((ctrlTop + '.affectToMid'), (topAffMdl + '.input2'))
            cmds.connectAttr((topAffMdl + '.output'), (twistDef[0] + '.lowBound'))
            endAffMdl = cmds.shadingNode('multDoubleLinear', asUtility=1, name = (self.prefix + 'twist_end_affect_mdl'))
            cmds.setAttr((endAffMdl + '.input1'), 0.1)
            cmds.connectAttr((ctrlEnd + '.affectToMid'), (endAffMdl + '.input2'))
            cmds.connectAttr((endAffMdl + '.output'), (twistDef[0] + '.highBound'))

            #Squash deformer: Set up the connections for the volume control
            volumeRevfMdl = cmds.shadingNode('multDoubleLinear', asUtility=1, name = (self.prefix + 'volume_reverse_mdl'))
            cmds.setAttr((volumeRevfMdl + '.input1'), -1)
            cmds.connectAttr((ctrlMid + '.volume'), (volumeRevfMdl + '.input2'))
            cmds.connectAttr((volumeRevfMdl + '.output'), (squashDef[0] + '.factor'))
            cmds.connectAttr((ctrlMid + '.startDropoff'), (squashDef[0] + '.startSmoothness'))
            cmds.connectAttr((ctrlMid + '.endDropoff'), (squashDef[0] + '.endSmoothness'))
            cmds.connectAttr((ctrlMid + '.volumePosition'), (squashDef[1] + '.translateX'))
            #Squash deformer: Set up the volume scaling
            sumScalePma = cmds.shadingNode('plusMinusAverage', asUtility=1, name = (self.prefix + 'volume_scale_sum_pma'))
            cmds.setAttr((sumScalePma + '.input1D[0]'), self.topPoint)
            cmds.connectAttr((ctrlMid + '.volumeScale'), (sumScalePma + '.input1D[1]'))
            cmds.connectAttr((sumScalePma + '.output1D'), (squashDef[1] + '.scaleY'))

            #Sine deformer: Set up the connections for the sine
            cmds.connectAttr((ctrlMid + '.amplitude'), (sineDef[0] + '.amplitude'))
            cmds.connectAttr((ctrlMid + '.offset'), (sineDef[0] + '.offset'))
            cmds.connectAttr((ctrlMid + '.twist'), (sineDef[1] + '.rotateY'))
            cmds.connectAttr((ctrlMid + '.sineLength'), (sineDef[0] + '.wavelength'))

            
            #Cleanup: Hierarchy
            cmds.parent(geoPlaneWire[0], geoPlaneTwist[0], geoPlaneSine[0], geoPlaneVolume[0], grpSurfaces)
            cmds.parent(twistDef[1], sineDef[1], squashDef[1], grpDeformers)
            cmds.parent(clsTop[1], clsMid[1], clsEnd[1], grpCluster)
            cmds.parent(grpTop, grpMid, grpEnd, grpCtrl)
            cmds.parent(geoPlane[0], grpSurface)
            cmds.parent(deformCrv, (cmds.listConnections(wireDef[0] + '.baseWire[0]')[0]), grpMisc)
            #Cleanup: Visibility
            cmds.hide(grpSurfaces, grpDeformers, grpCluster, grpMisc)
            for x in cmds.listConnections(ctrlMid):
                cmds.setAttr((x + '.isHistoricallyInteresting'), 0)
                for y in cmds.listConnections(x):
                    cmds.setAttr((y + '.isHistoricallyInteresting'), 0)
        else:
            blndDef = cmds.blendShape(geoPlaneWire[0], geoPlane[0], name=(self.prefix + 'blendShape'),weight=[(0,1),(1,1),(2,1)])
            #Cleanup: Hierarchy
            cmds.parent(geoPlaneWire[0], grpSurfaces)
            #cmds.parent(twistDef[1], sineDef[1], squashDef[1], grpDeformers)
            cmds.parent(clsTop[1], clsMid[1], clsEnd[1], grpCluster)
            cmds.parent(grpTop, grpMid, grpEnd, grpCtrl)
            cmds.parent(geoPlane[0], grpSurface)
            cmds.parent(deformCrv, (cmds.listConnections(wireDef[0] + '.baseWire[0]')[0]), grpMisc)
            #Cleanup: Visibility
            cmds.hide(grpSurfaces, grpDeformers, grpCluster, grpMisc)
            for x in cmds.listConnections(ctrlMid):
                cmds.setAttr((x + '.isHistoricallyInteresting'), 0)
                for y in cmds.listConnections(x):
                    cmds.setAttr((y + '.isHistoricallyInteresting'), 0)                
            print 'No deformer created'        

        #Update the scale-group
        scaleGrp = self.scaleGrp if self.scaleGrp else grpTransform
        #Create follicles: The main-surface and the volume-surface
        for x in range(0, self.numJoints):
            #Declare a variable for the current index
            num = str(x + 1)
            #Get the normalized position of where to place the current follicle
            uVal = ((0.5 / self.numJoints) * (x + 1) * 2) - ((0.5 / (self.numJoints * 2)) * 2)
            #Create a follicle for the bind-plane and the volume-plane
            follicleS = self.createFollicle(scaleGrp=scaleGrp, inputSurface=cmds.listRelatives(geoPlane[0], type="shape"), uVal=uVal, name=(self.prefix + num + '_follicle'))
            if (self.defFlag == True):
                follicleV = self.createFollicle(scaleGrp=None, inputSurface=cmds.listRelatives(geoPlaneVolume[0], type="shape"), uVal=uVal, vVal=0, name=(self.prefix + num + '_volume_follicle'))
                cmds.parent(follicleV[0], grpFollVolume)                
            cmds.parent(follicleS[0], grpFollMain)

            #Create a joint, controller and a group for the current skin-follicle
            cmds.select(clear=True)
            follicleJoint = cmds.joint(name=(self.prefix + num + '_JNT'), radius=0.1)
            follicleCtrl = cmds.circle(name=(self.prefix + num + '_CTRL'), c=(0,0,0), nr=(1,0,0), sw=360, r=0.5, d=3, s=8, ch=0)[0]
            follicleXform = cmds.group(name=(self.prefix + num + '_xform_GRP'), empty=True)
            cmds.parent(follicleXform, follicleS[0])
            cmds.parent(follicleCtrl, follicleXform)
            cmds.parent(follicleJoint, follicleCtrl)
            cmds.delete(cmds.parentConstraint(follicleS[0], follicleXform))
            #Set the color and connect the visibility-switch for the controller
            cmds.setAttr((cmds.listRelatives(follicleCtrl, shapes=True)[0] + '.overrideEnabled'), 1)
            cmds.setAttr((cmds.listRelatives(follicleCtrl, shapes=True)[0] + '.overrideColor'), 12)
            if (self.defFlag == True):
                cmds.connectAttr((ctrlMid + '.showExtraCtrl'), (cmds.listRelatives(follicleCtrl, shapes=True)[0] + '.visibility'))
            #Make the connections for the volume
            multMpd = cmds.shadingNode('multiplyDivide', asUtility=1, name = (self.prefix + num + '_multiplier_mpd'))
            if (self.defFlag == True):
                cmds.connectAttr((ctrlMid + '.volumeMultiplier'), (multMpd + '.input1Z'))                
                cmds.connectAttr((follicleV[0] + '.translate'), (multMpd + '.input2'))
            sumPma = cmds.shadingNode('plusMinusAverage', asUtility=1, name = (self.prefix + num + '_volume_sum_pma'))
            cmds.connectAttr((multMpd + '.outputZ'), (sumPma + '.input1D[0]'))
            cmds.setAttr((sumPma + '.input1D[1]'), 1)
            cmds.connectAttr((sumPma + '.output1D'), (follicleXform + '.scaleY'))
            cmds.connectAttr((sumPma + '.output1D'), (follicleXform + '.scaleZ'))                        
        
        self.cleanScene()       
        
        for elem in self.endC:
            endTmpC = cmds.parentConstraint(self.endC,'{}_end_CTRL'.format(self.prefix), mo=True)
            if len(self.endC) > 1:
                cmds.setAttr('{}.interpType'.format(endTmpC[0]), 2)
        for elem in self.topC:
            cmds.parentConstraint(self.topC,'{}_top_CTRL'.format(self.prefix), mo=True)
            if len(self.topC) > 1:
                cmds.setAttr('{}.interpType'.format(topTmpC[0]), 2)                                
            

            
    def run(self):            
        self.createRibbon()      
        self.module_main_grp()
        
        
'''
rib = Ribbon(5, 'L_armRibbon', 'scaleGrp', True, endC=['body:C_jaw_JNT'], topC=['body:C_spine4_JNT'], locatorRotation = 90)                          
rib.run()
'''


