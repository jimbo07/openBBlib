'''
Created on 22 Aug 2018

@author: lasse-r
'''

from maya import cmds
from ooutdmaya.rigging.core.util import easy
from ooutdmaya.rigging.core.puppet import base
from ooutdmaya.common.util import names
from ooutdmaya.rigging.core.util import lib

defaultSDK = {
    'protraction':{
        'locValue':0.25,
        'posTx':0.0171,
        'posTz':0.0114},
    'retraction':{
        'locValue':-0.25,
        'posTx':-0.0167,
        'posTz':-0.0116},
    'sideLeft':{
        'locValue':0.25,
        'rotRz':-4.836},
    'sideRight':{
        'locValue':-0.25,
        'rotRz':4.836},
    'open':{
        'locValue':-1,
        'rotRy':26.5,
        'rotTx':-0.001,
        'rotTz':-0.001},
    'close':{
        'locValue':0.125,
        'rotRy':-3.3125,
        'rotTx':0.001,
        'rotTz':0.002},
    'limits':{
        'tx':[-0.25, 0.25],
        'ty':[-1, 0.25],
        'tz':[-0.25, 0.25]}
    }

class Jaw(base.Base):

    def __init__(self, name, side='', workDir=None, go=False):
        ''' Builds a jaw
        '''
        base.Base.__init__(self, name, workDir=workDir, side=side)
        
        # init param attrs
        self.chain = None
        self.side = side
        
        # default params
        self.sdkDict = defaultSDK
        
        # ctl creation
        self.createCtls = False     
        
        # upVector
        self.jawBaseUpVector = [0, -1, 0]
        
        self.prefix = ""
        
        if go: self.go()
        
    # ====================
    # Jaw control
    # ====================
    @property
    def createCtls(self):
        """The internal state property."""
        self._initCreateCtls()
        return self._createCtls
        
    @createCtls.setter
    def createCtls(self, val):
        """Sets all "ctls" dictionary keys to the specified value"""
        self._initCreateCtls()
        self._createCtls = val
        for key in self.ctls:
            self.ctls[key]['createCtl'] = self._createCtls
        
        self.createJawCtl = val
 
    
    def _initJawCtl(self):
        if not 'jaw' in self.ctls:
            self.declareCtl(key='jaw', name='jaw')
            self.ctls['jaw']['ctlShape'] = 'cube'
            self.ctls['jaw']['ctlShape'] = 'sphere'

    @property
    def createJawCtl(self):
        """The internal state property."""
        self._initJawCtl()
        return self.ctls['jaw']['createCtl']
    
    @createJawCtl.setter
    def createJawCtl(self, val):
        self._initJawCtl()
        self.ctls['jaw']['createCtl'] = val
        
    
    # ====================
    # GO 
    # ====================
    def go(self):
        """
        """
        self.prep()
        self.run()
        self.complete()
        

    # ====================
    # PREP 
    # ====================
    def prep(self):
        # Run inherited functionality
        base.Base.prep(self)
                
                
    # ====================
    # BUILD 
    # ====================
    def run(self):
        """
        """
        
        # Run inherited functionality
        base.Base.run(self)
        
        # Create groups      
        self.driverChain = self.chain
        #=======================================================================
        # self.driverChain = joint.duplicateSegment(self.chain, suffix='DRV',
        #                                       searchReplaceSetList=[(names.getNS(self.chain[0]), '')])
        #=======================================================================
        
        self.jawOffset = cmds.createNode('transform', n=names.nodeName('transform', '{0}{1}Offset'.format(self.prefix, self.name), self.side))
        chainParent = cmds.listRelatives(self.chain[0], p=1)[0]
        if chainParent:
            easy.snapAlignScaleTo(chainParent, self.jawOffset)
        
        cmds.parent(self.jawOffset, self.grpSkeleton)
        cmds.parent(self.driverChain[0], self.jawOffset)
        
        key = 'jaw'
        self.buildCtl(key, lockAttrList=['scale'], movablePivot=False, keyAttrList=['rotateOrder'])
        ctlDict = self.ctls[key]
        easy.snapAlignTo(self.chain[-1], ctlDict['input'])
        
        self.sdkZeroGrp = cmds.createNode('transform', n=names.nodeName('transform', '{0}{1}SDKZero'.format(self.prefix, self.name), self.side))
        if chainParent:
            cmds.parent(self.sdkZeroGrp, chainParent)
            cmds.parentConstraint(chainParent, self.ctls['jaw']['input'], mo=1,
                                  n=names.addModifier(self.ctls['jaw']['input'], 'parentConstraint'))
        
        cmds.delete(cmds.parentConstraint(self.chain[0], self.sdkZeroGrp))
        cmds.delete(cmds.scaleConstraint(self.chain[0], self.sdkZeroGrp))
        
        cmds.delete(cmds.aimConstraint(self.chain[-1], self.sdkZeroGrp, aimVector=[1, 0, 0],
            upVector=[0, 0, 1], worldUpType='objectrotation', worldUpVector=self.jawBaseUpVector,
            worldUpObject=chainParent))
        
        # Create a rotation set driven key transform
        self.sdkRotGrp = cmds.duplicate(self.sdkZeroGrp, n=names.addModifier(self.sdkZeroGrp, 'transform', addSuffix="SetDrivenRot"))[0]
        
        # Create a position set driven key transform
        self.sdkPosGrp = cmds.duplicate(self.sdkZeroGrp, n=names.addModifier(self.sdkZeroGrp, 'transform', addSuffix="SetDrivenPos"))[0]
        
        # Parent all groups together
        cmds.parent(self.sdkRotGrp, self.sdkZeroGrp)
        cmds.parent(self.sdkPosGrp, self.sdkRotGrp)
        cmds.parent(self.jawOffset, self.sdkPosGrp)     
        
        # Create a transform to drive our jaw transformations
        self.sdkDriverLoc = cmds.spaceLocator(n=names.nodeName('locator', "{0}{1}SdkDriver".format(self.prefix, self.name), ))[0]
        cmds.delete(cmds.pointConstraint(self.chain[-1], self.sdkDriverLoc))
        cmds.hide(self.sdkDriverLoc)
        self.sdkDriverLocGrp = lib.createNode('transform', names.getDescriptor(self.sdkDriverLoc))
        cmds.delete(cmds.pointConstraint(self.chain[-1], self.sdkDriverLocGrp))
        cmds.parent(self.sdkDriverLoc, self.sdkDriverLocGrp)
        cmds.parent(self.sdkDriverLocGrp, self.grpMisc)
        
        # Set driven keys
        posTxAttrPlug = '{0}.translateZ'.format(self.sdkPosGrp)
        posTzAttrPlug = '{0}.translateX'.format(self.sdkPosGrp)
        rotTxAttrPlug = '{0}.translateZ'.format(self.sdkRotGrp)
        rotTzAttrPlug = '{0}.translateX'.format(self.sdkRotGrp)
        rotRyAttrPlug = '{0}.rotateY'.format(self.sdkRotGrp)
        rotRzAttrPlug = '{0}.rotateZ'.format(self.sdkRotGrp)
        
        # Protraction/Retraction driven keys
        cmds.setDrivenKeyframe(posTxAttrPlug,
            currentDriver='{0}.translateX'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(posTzAttrPlug,
            currentDriver='{0}.translateX'.format(self.sdkDriverLoc))
        # rename sdk nodes
        posTxSdk = cmds.listConnections(posTxAttrPlug, s=1, d=0, type='animCurve')[0]
        posTxSdk = cmds.rename(posTxSdk, '{0}PosTx_SDK'.format(self.prefix))
        posTzSdk = cmds.listConnections(posTzAttrPlug, s=1, d=0, type='animCurve')[0]
        posTzSdk = cmds.rename(posTzSdk, '{0}PosTz_SDK'.format(self.prefix))
        
        # Protraction driven key
        cmds.setAttr('{0}.translateX'.format(self.sdkDriverLoc), self.sdkDict['protraction']['locValue'])
        cmds.setAttr(posTxAttrPlug, self.sdkDict['protraction']['posTx'])
        cmds.setAttr(posTzAttrPlug, self.sdkDict['protraction']['posTz'])
        cmds.setDrivenKeyframe(posTxAttrPlug,
            currentDriver='{0}.translateX'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(posTzAttrPlug,
            currentDriver='{0}.translateX'.format(self.sdkDriverLoc))
        
        # Retraction driven key
        cmds.setAttr('{0}.translateX'.format(self.sdkDriverLoc), self.sdkDict['retraction']['locValue'])
        cmds.setAttr(posTxAttrPlug, self.sdkDict['retraction']['posTx'])
        cmds.setAttr(posTzAttrPlug, self.sdkDict['retraction']['posTz'])
        cmds.setDrivenKeyframe(posTxAttrPlug,
            currentDriver='{0}.translateX'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(posTzAttrPlug,
            currentDriver='{0}.translateX'.format(self.sdkDriverLoc))
        cmds.setAttr('{0}.translateX'.format(self.sdkDriverLoc), 0)
        
        # Sideways driven keys
        cmds.setDrivenKeyframe(rotRzAttrPlug,
            currentDriver='{0}.translateZ'.format(self.sdkDriverLoc))
        # rename sdk node
        rotRzSdk = cmds.listConnections(rotRzAttrPlug, s=1, d=0, type='animCurve')[0]
        rotRzSdk = cmds.rename(rotRzSdk, '{0}RotRz_SDK'.format(self.prefix))
        
        # Sideways left driven key
        cmds.setAttr('{0}.translateZ'.format(self.sdkDriverLoc), self.sdkDict['sideLeft']['locValue'])
        cmds.setAttr(rotRzAttrPlug, self.sdkDict['sideLeft']['rotRz'])
        cmds.setDrivenKeyframe(rotRzAttrPlug,
            currentDriver='{0}.translateZ'.format(self.sdkDriverLoc))
            
        # Sideways right driven key
        cmds.setAttr('{0}.translateZ'.format(self.sdkDriverLoc), self.sdkDict['sideRight']['locValue'])
        cmds.setAttr(rotRzAttrPlug, self.sdkDict['sideRight']['rotRz'])
        cmds.setDrivenKeyframe(rotRzAttrPlug,
            currentDriver='{0}.translateZ'.format(self.sdkDriverLoc))
        cmds.setAttr('{0}.translateZ'.format(self.sdkDriverLoc), 0)
        
        # Open/Close driven keys
        cmds.setDrivenKeyframe(rotRyAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(rotTxAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(rotTzAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        
        # rename sdk node
        rotRySdk = cmds.listConnections(rotRyAttrPlug, s=1, d=0, type='animCurve')[0]
        rotRySdk = cmds.rename(rotRySdk, '{0}RotRy_SDK'.format(self.prefix))
        rotTxSdk = cmds.listConnections(rotTxAttrPlug, s=1, d=0, type='animCurve')[0]
        rotTxSdk = cmds.rename(rotTxSdk, '{0}RotTx_SDK'.format(self.prefix))
        rotTzSdk = cmds.listConnections(rotTzAttrPlug, s=1, d=0, type='animCurve')[0]
        rotTzSdk = cmds.rename(rotTzSdk, '{0}RotTz_SDK'.format(self.prefix))
            
        # Open driven key
        cmds.setAttr('{0}.translateY'.format(self.sdkDriverLoc), self.sdkDict['open']['locValue'])
        cmds.setAttr(rotRyAttrPlug, self.sdkDict['open']['rotRy'])
        cmds.setAttr(rotTxAttrPlug, self.sdkDict['open']['rotTx'])
        cmds.setAttr(rotTzAttrPlug, self.sdkDict['open']['rotTz'])
        cmds.setDrivenKeyframe(rotRyAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(rotTxAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(rotTzAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
            
        # Close driven key
        cmds.setAttr('{0}.translateY'.format(self.sdkDriverLoc), self.sdkDict['close']['locValue'])
        cmds.setAttr(rotRyAttrPlug, self.sdkDict['close']['rotRy'])
        cmds.setAttr(rotTxAttrPlug, self.sdkDict['close']['rotTx'])
        cmds.setAttr(rotTzAttrPlug, self.sdkDict['close']['rotTz'])
        cmds.setDrivenKeyframe(rotRyAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(rotTxAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setDrivenKeyframe(rotTzAttrPlug,
            currentDriver='{0}.translateY'.format(self.sdkDriverLoc))
        cmds.setAttr('{0}.translateY'.format(self.sdkDriverLoc), 0)
        
        # Set tangents to linear
        cmds.keyTangent(posTxSdk, itt='linear', ott='linear', e=1)
        cmds.keyTangent(posTzSdk, itt='linear', ott='linear', e=1)
        cmds.keyTangent(rotRzSdk, itt='linear', ott='linear', e=1)
        cmds.keyTangent(rotRySdk, itt='linear', ott='linear', e=1)
        cmds.keyTangent(rotTxSdk, itt='linear', ott='linear', e=1)
        cmds.keyTangent(rotTzSdk, itt='linear', ott='linear', e=1)
        
        cmds.connectAttr("{0}.{1}".format(ctlDict['ctl'][0], "translate"), "{0}.{1}".format(self.sdkDriverLoc, "translate"))
        
        # Set transform limits
        cmds.transformLimits(ctlDict['ctl'][0], tx=self.sdkDict['limits']['tx'], etx=[1, 1])
        cmds.transformLimits(ctlDict['ctl'][0], ty=self.sdkDict['limits']['ty'], ety=[1, 1])
        cmds.transformLimits(ctlDict['ctl'][0], tz=self.sdkDict['limits']['tz'], etz=[1, 1])
        
        # ====================
        # Curve shape data
        # ====================
        if self.createCurveShapeDataSet:
            for k in self.ctls:
                if 'ctl' in self.ctls[k]:
                    cmds.sets(self.ctls[k]['ctl'], add=self.curveShapeDataSet)
            self.importCurveShapeData()

        
    # ====================
    # COMPLETE 
    # ====================
    def complete(self):
        base.Base.complete(self)

