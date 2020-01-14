'''
Created on 1 Oct 2018

@author: lasse-r
'''
import maya.cmds as cmds

from ooutdmaya.rigging.core.util.IO import constraints, data
import types

class ConstraintData( data.Data ):
    ''' ConstraintData base class object.
        Contains functions to save, load and rebuild constraints.
    '''
    TYPE = 'constraint'
    
    ATTR_VAL = []
    ATTR_CON = []
    
    INTERP = [      'NoFlip',
                    'Average',
                    'Shortest',
                    'Longest',
                    'Cache'    ]
    
    WORLD_UP = [    'Scene Up',
                    'Object Up',
                    'Object Rotation Up',
                    'Vector',
                    'None'    ]
    
    TRANSLATE = {   'x':'translateX',
                    'y':'translateY',
                    'z':'translateZ'    }
    ROTATE =     {  'x':'rotateX',
                    'y':'rotateY',
                    'z':'rotateZ'    }
    
    def __init__(self, nodeList=None):
        ''' ConstraintData class initializer.
        '''
        # Execute Super Class Initilizer
        super(ConstraintData, self).__init__()
        
        # Build ChannelData
        if nodeList: self.buildData(nodeList)
        
    
    def name(self):
        ''' Return class name
        '''
        return self.__class__.__name__
    
    
    def verify(self):
        ''' Verify constraint data
        '''
        if not self._data:
            raise Exception(self.name()+' has not been initialized! No data...')
        
    
    def buildData(self, nodeList):
        ''' Build ConstraintData.
        :param nodeList list: List of constraint nodes to store data for.
        '''
        # Check Node List
        if not nodeList: return
        
        # ==============
        # - Build Data -
        # ==============
        
        # Start timer
        timer = cmds.timerX()
        
        # Reset Data
        self.reset()
        
        # Build Constraint Data
        for constraint in nodeList:
            
            # Check Constraint
            if not constraints.isConstraint(constraint):
                print("{0}: Object {1} is not a valid {2}! Skipping...".format(self.name(), constraint, self.TYPE))
                continue
            
            # Initialize Constraint Data
            self._data[constraint] = {}
            
            # Constraint Type
            self._data[constraint]['type'] = cmds.objectType(constraint)
            
            # Constraint Slave Transform
            slave = constraints.slave(constraint)
            self._data[constraint]['slave'] = slave
            
            # Target List
            targetList = constraints.targetList(constraint)
            self._data[constraint]['targetList'] = targetList
            self._data[constraint]['targetAliasList'] = [constraints.targetAlias(constraint,target) for target in targetList]
            self._data[constraint]['targetIndex'] = [constraints.targetIndex(constraint,target) for target in targetList]
            self._data[constraint]['targetWeight'] = [cmds.getAttr(constraint+'.'+target) for target in self._data[constraint]['targetAliasList']]
            
            # Constraint Slave Attributes
            constraintAttrs = [cmds.ls(i, o=True)[0] for i in cmds.listConnections(constraint,s=False,d=True,p=True,sh=True) or [] if i.startswith(slave+'.')]
            self._data[constraint]['skipTranslate'] = sorted([i for i in self.TRANSLATE.keys() if not self.TRANSLATE[i] in constraintAttrs])
            self._data[constraint]['skipRotate'] = sorted([i for i in self.ROTATE.keys() if not self.ROTATE[i] in constraintAttrs])
        
        # Print Timer Result
        buildTime = cmds.timerX(st=timer)
        print(self.name()+': Data build time for nodes "'+str(nodeList)+'": '+str(buildTime))
        
        # ========================
        # - Build Attribute Data -
        # ========================
        
        self.buildAttrValueData()
        self.buildAttrConnectionData()
        c = ParentConstraintData()
        c._data = self._data
        c.buildData(nodeList)
        
        # =================
        # - Return Result -
        # =================
        
        return self._data
    
    def buildAttrValueData(self):
        '''
        Build constraint attribute value data
        '''
        # Verify Data
        self.verify()
        
        # ==============================
        # - Build Attribute Value Data -
        # ==============================
        
        for constraint in self._data.iterkeys():
            
            # Check Constraint
            if not cmds.objExists(constraint):
                print(self.name()+': '+self.TYPE+' "'+constraint+'" does not exist! Skipping...')
            
            # Build Attribute Value Data
            for attr in self.ATTR_VAL:
                if cmds.attributeQuery(attr,n=constraint,ex=True):
                    attrVal = cmds.getAttr(constraint+'.'+attr)
                    if cmds.getAttr(constraint+'.'+attr,type=True) == 'double3':
                        self._data[constraint][attr] = attrVal[0]
                    else:
                        self._data[constraint][attr] = attrVal
                else:
                    print(self.name()+': '+self.TYPE+' "'+constraint+'" has no attribute "'+attr+'"! Skipping...')
    
    def buildAttrConnectionData(self):
        '''
        Build constraint attribute connection data
        '''
        # Verify Data
        self.verify()
        
        # ===================================
        # - Build Attribute Connection Data -
        # ===================================
        
        for constraint in self._data.iterkeys():
            
            # Check Constraint
            if not cmds.objExists(constraint):
                print(self.name()+': '+self.TYPE+' "'+constraint+'" does not exist! Skipping...')
            
            # Build Attribute Connection Data
            for attr in self.ATTR_CON:
                if cmds.attributeQuery(attr, n=constraint, ex=True):
                    attrCon = cmds.listConnections(constraint+'.'+attr,s=True,d=False,p=True)
                    if attrCon: self._data[constraint][attr] = attrCon[0]
                else:
                    print(self.name()+': '+self.TYPE+' "'+constraint+'" has no attribute "'+attr+'"! Skipping...')
    
    def restoreAttrValues(self):
        ''' Restore constraint attribute values.
        '''
        # Verify Data
        self.verify()
        
        # ============================
        # - Restore Attribute Values -
        # ============================
        
        for constraint in self._data.iterkeys():
            
            # Check Constraint
            if not cmds.objExists(constraint):
                print(self.name()+': '+self.TYPE+' "'+constraint+'" does not exist! Unable to restore attribute values...')
            
            # For Each Attribute Value
            for attr in self.ATTR_VAL:
                
                # Check Attribute Value Data
                if self._data[constraint].has_key(attr):
                    
                    # Restore Attribute Value
                    attrVal = self._data[constraint][attr]
                    try:
                        if isinstance(attrVal,types.ListType):
                            cmds.setAttr(constraint+'.'+attr,*attrVal)
                        else:
                            cmds.setAttr(constraint+'.'+attr,attrVal)
                    except Exception, e:
                        print(self.name()+': Unable to set constraint attribute value "'+constraint+'.'+attr+'"! Exception msg: '+str(e))
                else:
                    print(self.name()+': No attribute value data stored for "'+attr+'"! Skipping...')
    
    def restoreAttrConnections(self, force=False):
        ''' Restore constraint attribute connections.
        :param force bool: Force connection if target has existing incoming connection.
        '''
        # Verify Data
        self.verify()
        
        # =================================
        # - Restore Attribute Connections -
        # =================================
        
        for constraint in self._data.iterkeys():
            
            # Check Constraint
            if not cmds.objExists(constraint):
                print(self.name()+': '+self.TYPE+' "'+constraint+'" does not exist! Unable to restore attribute values...')
            
            # For Each Attribute Connection
            for attr in self.ATTR_CON:
                
                # Check Attribute Connection Data
                if self._data[constraint].has_key(attr):
                    
                    # Retore Attribute Connection
                    src = self._data[constraint][attr]
                    if cmds.objExists(src):
                        try: cmds.connectAttr(src,constraint+'.'+attr,f=force)
                        except Exception, e: print(self.name()+': Unable to connect "'+src+'" to "'+constraint+'.'+attr+'"! Exception msg:' +str(e))
                    else:
                        print(self.name()+': Attribute connection source "'+src+'" does not exist! Unable to restore attribute connection...')
                else:
                    print(self.name()+': No attribute connection data stored for "'+attr+'"! Skipping...')
    
    def rebuild(self,nodeList=None):
        ''' Rebuild constraint(s) from data
        @param nodeList: List of constraint nodes to rebuild. If None, rebuild all stored data.
        @type nodeList: list
        '''
        # ==========
        # - Checks -
        # ==========
        
        self.verify()
        
        # ===========================
        # - Rebuild Constraint Data -
        # ===========================
        
        # Start timer
        timer = cmds.timerX()
        
        # Get Node List
        if not nodeList: nodeList = self._data.keys()
        
        # =================================
        # - Rebuild Constraints from Data -
        # =================================
        
        print(self.name()+': Rebuilding Constraints...')
        
        constraintList = []
        for constraint in nodeList:
            
            # Check Constraint Key
            if not self._data.has_key(constraint):
                print('No constraint data for "{0}"!! Skipping...'.format(constraint))
                continue
            
            # Rebuild Constraint
            print('REBUILDING - "'+constraint+'"...')
            constraintNode = self.rebuildConstraint(constraint)
            constraintList.append(constraintNode)
            
        # Reconnect
        self.restoreAttrConnections()
        self.restoreAttrValues()
            
        # Print Timer Result
        buildTime = cmds.timerX(st=timer)
        print(self.name()+': Rebuild time "'+str(nodeList)+'": '+str(buildTime))
            
        # =================
        # - Return Result -
        # =================
        
        return constraintList

    
    def rebuildConstraint(self, constraint):
        ''' Rebuild single constraint using stored values.
            Implement per constraint type
        :param constraint str: Constraint to rebuild from data
        '''
        if self._data[constraint]['type'] == 'aimConstraint':
            c = AimConstraintData()
            c._data = self._data
            result = c.rebuildConstraint(constraint)
        elif self._data[constraint]['type'] == 'pointConstraint':
            c = PointConstraintData()
            c._data = self._data
            result = c.rebuildConstraint(constraint)
        elif self._data[constraint]['type'] == 'orientConstraint':
            c = OrientConstraintData()
            c._data = self._data
            result = c.rebuildConstraint(constraint)
        elif self._data[constraint]['type'] == 'parentConstraint':
            c = ParentConstraintData()
            c._data = self._data
            result = c.rebuildConstraint(constraint)
        else:
            print('Constraint type "{0}" is not valid for this method!'.format(self._data[constraint]['type']))
            
        return result
        
        
class AimConstraintData( ConstraintData ):
    '''
    '''
    TYPE = 'aimConstraint'
    
    ATTR_VAL = [    'lockOutput',
                    'offset',
                    'enableRestPosition',
                    'restRotate',
                    'aimVector',
                    'upVector',
                    'worldUpVector',
                    'worldUpType'    ]
    
    ATTR_CON = [    'worldUpMatrix'    ]
    
    def rebuildConstraint(self, constraint):
        '''
        Rebuild single constraint using stored values.
        @param constraint: Constraint to rebuild from data
        @type constraint: str
        '''
        # Rebuild Aim Constraint
        constraintNode = cmds.aimConstraint(self._data[constraint]['targetList'],
                                            self._data[constraint]['slave'],
                                            skip=self._data[constraint]['skipRotate'],
                                            weight=self._data[constraint]['targetWeight'][0],
                                            name=constraint )[0]
        
        # Return Result
        return constraintNode
    
class PointConstraintData( ConstraintData ):
    '''
    '''
    TYPE = 'pointConstraint'
    
    ATTR_VAL = [    'lockOutput',
                    'offset',
                    'enableRestPosition',
                    'restTranslate'    ]
    
    def rebuildConstraint(self, constraint):
        ''' Rebuild single constraint using stored values.
        @param constraint: Constraint to rebuild from data
        @type constraint: str
        '''
        print "\n TESTING: \n \n"
        print self._data[constraint]['targetList']
        print self._data[constraint]['slave']
        print self._data[constraint]['skipTranslate']
        print self._data[constraint]['targetWeight'][0]
        
        # Rebuild Point Constraint
        constraintNode = cmds.pointConstraint(  self._data[constraint]['targetList'],
                                                self._data[constraint]['slave'],
                                                skip=self._data[constraint]['skipTranslate'],
                                                weight=self._data[constraint]['targetWeight'][0],
                                                name=constraint )[0]
        
        # Return Result
        return constraintNode

class OrientConstraintData( ConstraintData ):
    '''
    '''
    TYPE = 'pointConstraint'
    
    ATTR_VAL = [    'lockOutput',
                    'offset',
                    'enableRestPosition',
                    'restRotate',
                    'interpType'    ]
    
    def rebuildConstraint(self,constraint):
        '''
        Rebuild single constraint using stored values.
        @param constraint: Constraint to rebuild from data
        @type constraint: str
        '''
        # Rebuild Orient Constraint
        constraintNode = cmds.orientConstraint(    self._data[constraint]['targetList'],
                                                self._data[constraint]['slave'],
                                                skip=self._data[constraint]['skipRotate'],
                                                weight=self._data[constraint]['targetWeight'][0],
                                                name=constraint )[0]
        
        # Return Result
        return constraintNode

class ParentConstraintData( ConstraintData ):
    '''
    '''
    TYPE = 'parentConstraint'
    
    ATTR_VAL = [    'lockOutput',
                    'offset',
                    'enableRestPosition',
                    'restTranslate',
                    'restRotate',
                    'interpType'    ]
    
    def buildData(self, nodeList=None):
        ''' Build ConstraintData.
        :param nodeList list: List of constraint nodes to store data for.
        '''
        # Check Node List
        if not nodeList: return
        
        print "ENTERING!!!"
        # Execute Super Class Build
        #----------------- super(ParentConstraintData, self).buildData(nodeList)
        
        # Target Offset Data
        for constraint in self._data.iterkeys():
            if not self._data[constraint]['type'] == "parentConstraint":
                continue
            # Initialize Offsets
            self._data[constraint]['targetOffsetTranslate'] = []
            self._data[constraint]['targetOffsetRotate'] = []
            
            # For Each Target
            targetList = self._data[constraint]['targetList']
            for t in range(len(targetList)):
                
                # Get Target Index
                targetIndex = self._data[constraint]['targetIndex'][t]
                
                # Get Target Offset Data from Constraint
                offsetT = cmds.getAttr(constraint+'.target['+str(targetIndex)+'].targetOffsetTranslate')[0]
                offsetR = cmds.getAttr(constraint+'.target['+str(targetIndex)+'].targetOffsetRotate')[0]
                
                # Append Target Offset Lists 
                self._data[constraint]['targetOffsetTranslate'].append(offsetT)
                self._data[constraint]['targetOffsetRotate'].append(offsetR)
        
    
    def rebuildConstraint(self, constraint):
        ''' Rebuild single constraint using stored values.
        :param constraint str: Constraint to rebuild from data
        '''
        # Rebuild Parent Constraint
        constraintNode = cmds.parentConstraint( self._data[constraint]['targetList'],
                                                self._data[constraint]['slave'],
                                                skipTranslate=self._data[constraint]['skipTranslate'],
                                                skipRotate=self._data[constraint]['skipRotate'],
                                                weight=self._data[constraint]['targetWeight'][0],
                                                name=constraint )[0]
            
        # Apply Target Offsets
        for target in range(len(self._data[constraint]['targetList'])):
            
            # Get Target Index
            targetIndex = self._data[constraint]['targetIndex'][target]
            
            # Get Target Offset Data from Constraint
            offsetT = self._data[constraint]['targetOffsetTranslate'][target]
            offsetR = self._data[constraint]['targetOffsetRotate'][target]
            cmds.setAttr(constraint+'.target['+str(targetIndex)+'].targetOffsetTranslate', offsetT[0], offsetT[1], offsetT[2],)
            cmds.setAttr(constraint+'.target['+str(targetIndex)+'].targetOffsetRotate', offsetR[0], offsetR[1], offsetR[2])
        
        # Return Result
        return constraintNode
    
    
