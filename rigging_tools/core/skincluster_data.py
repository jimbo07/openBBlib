'''
Created on 28 Sep 2018

@author: lasse-r
'''
import maya.cmds as cmds
import maya.OpenMaya as om

from ooutdmaya.rigging.core.util import easy
from ooutdmaya.rigging.core.util.IO import skinCluster, data, deformerData, meshData
from ooutdmaya.common.util import progressBar


class SkinClusterData( deformerData.MultiInfluenceDeformerData ):
    '''
    SkinCluster Data Class Object
    Contains functions to save, load and rebuild basic skinCluster data.
    '''
    def __init__(self,skc=''):
        '''
        SkinCluster Data Class Initializer
        '''
        print "Running SkinClusterData class!"
        # Execute Super Class Initilizer
        super(SkinClusterData, self).__init__()
        
        # SkinCluster Custom Attributes
        self._data['attrValueList'].append('skinningMethod')
        self._data['attrValueList'].append('useComponents')
        self._data['attrValueList'].append('normalizeWeights')
        self._data['attrValueList'].append('deformUserNormals')
        
        # Build SkinCluster Data
        if skc: self.buildData(skc)
    
    def verifySkinCluster(self, skc):
        '''
        '''
        # Check skinCluster
        if not skinCluster.isSkinCluster(skc):
            raise Exception('Object {0} is not a valid skinCluster!'.format(skc))
    
    def buildData(self, skc):
        ''' Build skinCluster data and store as class object dictionary entries
        :param skinCluster list: SkinCluster deformer to store data for.
        '''
        # Check skinCluster
        self.verifySkinCluster(skc)
        
        # Clear Data
        self.reset()
        
        # Start Timer
        timer = cmds.timerX()
        
        self._data['name'] = skc
        self._data['type'] = 'skinCluster'
        
        # Get affected geometry
        skinGeoShape = cmds.skinCluster(skc, q=True, g=True)
        if len(skinGeoShape) > 1: raise Exception('SkinCluster {0} output is connected to multiple shapes!'.format(skc))
        if not skinGeoShape: raise Exception('Unable to determine affected geometry for skinCluster {0}!'.format(skc))
        skinGeo = cmds.listRelatives(skinGeoShape[0], p=True, pa=True)
        if not skinGeo: raise Exception('Unable to determine geometry transform for object {0}!'.format(skinGeoShape))
        self._data['affectedGeometry'] = skinGeo
        skinGeo = skinGeo[0]
        
        skinClusterSet = easy.getDeformerSet(skc)
        
        self._data[skinGeo] = {}
        self._data[skinGeo]['index'] = 0
        self._data[skinGeo]['geometryType'] = str(cmds.objectType(skinGeoShape))
        self._data[skinGeo]['membership'] = easy.getDeformerSetMemberIndices(skc,skinGeo)
        self._data[skinGeo]['weights'] = []
        
        if self._data[skinGeo]['geometryType'] == 'mesh':
                self._data[skinGeo]['mesh'] = meshData.MeshData(skinGeo)
        
        # Get skinCluster influence list
        influenceList = cmds.skinCluster(skc,q=True,inf=True)
        if not influenceList: raise Exception('Unable to determine influence list for skinCluster {0}!'.format(skc))
        
        # Get Influence Wieghts
        weights = skinCluster.getInfluenceWeightsAll(skc)
        
        # For each influence
        for influence in influenceList:
            
            # Initialize influence data
            self._influenceData[influence] = {}
            
            # Get influence index
            infIndex = skinCluster.getInfluenceIndex(skc,influence)
            self._influenceData[influence]['index'] = infIndex
            
            # Get Influence BindPreMatrix
            bindPreMatrix = cmds.listConnections(skc+'.bindPreMatrix['+str(infIndex)+']',s=True,d=False,p=True)
            if bindPreMatrix: self._influenceData[influence]['bindPreMatrix'] = bindPreMatrix[0]
            else: self._influenceData[influence]['bindPreMatrix'] = ''
            
            # Get Influence Type (Transform/Geometry)
            infGeocmdsonn = cmds.listConnections(skc+'.driverPoints['+str(infIndex)+']')
            if infGeocmdsonn:
                self._influenceData[influence]['type'] = 1
                self._influenceData[influence]['polySmooth'] = cmds.skinCluster(skc,inf=influence,q=True,ps=True)
                self._influenceData[influence]['nurbsSamples'] = cmds.skinCluster(skc,inf=influence,q=True,ns=True)
            else:
                self._influenceData[influence]['type'] = 0
            
            # Get Influence Weights
            pInd = skinCluster.getInfluencePhysicalIndex(skc,influence)
            self._influenceData[influence]['wt'] = weights[pInd]
        
        # =========================
        # - Custom Attribute Data -
        # =========================
        
        # Add Pre-Defined Custom Attributes
        self.getDeformerAttrValues()
        self.getDeformerAttrConnections()
        
        # =================
        # - Return Result -
        # =================
        
        skinTime = cmds.timerX(st=timer)
        print('SkinClusterData: Data build time for "'+skc+'": '+str(skinTime))

    def rebuild(self):
        '''
        Rebuild the skinCluster using stored data
        '''
        # ==========
        # - Checks -
        # ==========
        
        # Check geometry
        skinGeo = self._data['affectedGeometry'][0]
        if not cmds.objExists(skinGeo):
            raise Exception('SkinCluster geometry "'+skinGeo+'" does not exist! Use remapGeometry() to load skinCluster data for a different geometry!')
        
        # =======================
        # - Rebuild SkinCluster -
        # =======================
        
        # Start timer
        timer = cmds.timerX()
        
        # Initialize Temp Joint
        tempJnt = ''
        
        # Unlock Influences
        influenceList = self._influenceData.keys()
        for influence in influenceList:
            if cmds.objExists(influence+'.liw'):
                if cmds.getAttr(influence+'.liw',l=True):
                    try: cmds.setAttr(influence+'.liw',l=False)
                    except: print('Error unlocking attribute "'+influence+'.liw"! This could problems when rebuilding the skinCluster...')
                if cmds.getAttr(influence+'.liw'):
                    try: cmds.setAttr(influence+'.liw',False)
                    except: print('Error setting attribute "'+influence+'.liw" to False! This could problems when rebuilding the skinCluster...')
        
        # Check SkinCluster
        skc = self._data['name']
        if not cmds.objExists(skc):
            
            # Get Transform Influences
            jointList = [inf for inf in influenceList if not self._influenceData[inf]['type']]
            
            # Check Transform Influences
            if not jointList:
                
                # Create Temporary Bind Joint
                cmds.select(cl=1)
                tempJnt = cmds.joint(n=skc+'_tempJoint')
                print('No transform influences specified for skinCluster "'+skc+'"! Creating temporary bind joint "'+tempJnt+'"!')
                jointList = [tempJnt]
            
            else:
                
                # Get Surface Influences
                influenceList = [inf for inf in influenceList if self._influenceData[inf]['type']]
            
            # Create skinCluster
            skc = cmds.skinCluster(jointList,skinGeo,tsb=True,n=skc)[0]
        
        else:
            
            # Check Existing SkinCluster
            affectedGeo = easy.getAffectedGeometry(skc)
            if affectedGeo.keys()[0] != skinGeo:
                raise Exception('SkinCluster "'+skc+'" already exists, but is not connected to the expeced geometry "'+skinGeo+'"!')
        
        # Add skinCluster influences
        for influence in influenceList:
            
            # Check influence
            if not cmds.objExists(influence):
                raise Exception('Influence "'+influence+'" does not exist! Use remapInfluence() to apply data to a different influence!')
            
            # Check existing influence connection
            if not cmds.skinCluster(skc,q=True,inf=True).count(influence):
            
                # Add influence
                if self._influenceData[influence]['type']:
                    # Geometry
                    polySmooth = self._influenceData[influence]['polySmooth']
                    nurbsSamples = self._influenceData[influence]['nurbsSamples']
                    cmds.skinCluster(skc,e=True,ai=influence,ug=True,ps=polySmooth,ns=nurbsSamples,wt=0.0,lockWeights=True)
                    
                else:
                    # Transform
                    cmds.skinCluster(skc,e=True,ai=influence,wt=0.0,lockWeights=True)
                
                # Bind Pre Matrix
                if self._influenceData[influence]['bindPreMatrix']:
                    infIndex = skinCluster.getInfluenceIndex(skc,influence)
                    cmds.connectAttr(self._influenceData[influence]['bindPreMatrix'],skc+'.bindPreMatrix['+str(infIndex)+']',f=True)
        
        # Load skinCluster weights
        cmds.setAttr(skc+'.normalizeWeights',0)
        skinCluster.clearWeights(skinGeo)
        self.loadWeights()
        cmds.setAttr(skc+'.normalizeWeights',1)
        
        # Restore Custom Attribute Values and Connections
        self.setDeformerAttrValues()
        self.setDeformerAttrConnections()
        
        # Clear Selection
        cmds.select(cl=True)
        
        # =================
        # - Return Result -
        # =================
        
        # Print Timed Result
        totalTime = cmds.timerX(st=timer)
        print('SkinClusterData: Rebuild time for skinCluster "'+skc+'": '+str(totalTime))
        
        return skc
    
    
    def loadWeights(    self,
                        skc        = None,
                        influenceList    = None,
                        componentList    = None,
                        normalize        = True ):
        ''' Apply the stored skinCluster weights.
        :param skc str: The list of components to apply skc weights to.
        :param influenceList list or None: The list of skc influences to apply weights for.
        :param componentList list or None: The list of components to apply skc weights to.
        :param normalize bool: Normalize influence weights.
        '''
        # ==========
        # - Checks -
        # ==========
        
        # Check SkinCluster
        if not skc: skc = self._data['name']
        self.verifySkinCluster(skc)
        
        # Check Geometry
        skinGeo = self._data['affectedGeometry'][0]
        if not cmds.objExists(skinGeo):
            raise Exception('SkinCluster geometry {0} does not exist! Use remapGeometry() to load skinCluster data to a different geometry!'.format(skinGeo))
        
        # Check Influence List
        if not influenceList: influenceList = self._influenceData.keys() or []
        for influence in influenceList:
            if not influence in cmds.skinCluster(skc,q=True,inf=True) or []:
                raise Exception('Object "'+influence+'" is not a valid influence of skinCluster "'+skc+'"! Unable to load influence weights...')
            if not self._influenceData.has_key(influence):
                raise Exception('No influence data stored for "'+influence+'"! Unable to load influence weights...')
        
        # Check Component List
        if not componentList:
            componentList = easy.getComponentStrList(skinGeo)
        componentSel = easy.getSelectionElement(componentList,0)
        
        # Get Component Index List
        componentIndexList = easy.getSingleIndexComponentList(componentList)
        componentIndexList = componentIndexList[componentIndexList.keys()[0]]
        
        # Get Influence Index
        infIndexArray = om.MIntArray()
        for influence in influenceList:
            infIndex = skinCluster.getInfluencePhysicalIndex(skc,influence)
            infIndexArray.append(infIndex)
        
        # Build Weight Array
        wtArray = om.MDoubleArray()
        oldWtArray = om.MDoubleArray()
        for c in componentIndexList:
            for i in range(len(influenceList)):
                if self._influenceData.has_key(influenceList[i]):
                    wtArray.append(self._influenceData[influenceList[i]]['wt'][c])
                else:
                    wtArray.append(0.0)
        
        # Get skinCluster function set
        skinFn = skinCluster.getSkinClusterFn(skc)
        
        # Set skinCluster weights
        skinFn.setWeights(componentSel[0], componentSel[1], infIndexArray, wtArray, normalize, oldWtArray)
        
        # =================
        # - Return Result -
        # =================
        
        return list(wtArray)
    
    
    def swapWeights(self, inf1, inf2):
        ''' Swap influence weight values between 2 skinCluster influeneces.
        :param inf1 str: First influence to swap weights for
        :param inf2 str: Second influence to swap weights for
        '''
        # Check Influences
        if not self._influenceData.has_key(inf1):
            raise Exception('No influence data for {0}! Unable to swap weights...'.format(inf1))
        if not self._influenceData.has_key(inf2):
            raise Exception('No influence data for {0}! Unable to swap weights...'.format(inf2))
        
        # Swap Weights
        self._influenceData[inf1]['wt'][:], self._influenceData[inf2]['wt'][:] = self._influenceData[inf2]['wt'][:], self._influenceData[inf1]['wt'][:]
        
        # Return Result
        print('SkinClusterData: Swap Weights Complete - {0} <> {1}'.format(inf1, inf2))
        
    
    def moveWeights(self,sourceInf, targetInf, mode='add'):
        ''' Move influence weight values from one skinCluster influenece to another.
        :param sourceInf str: First influence to swap weights for
        :param targetInf str: Second influence to swap weights for
        :param mode str: Move mode for the weights. Avaiable options are "add" and "replace".
        '''
        # Check Influences
        if not self._influenceData.has_key(sourceInf):
            raise Exception('No influence data for source influence {0}! Unable to move weights...'.format(sourceInf))
        if not self._influenceData.has_key(targetInf):
            raise Exception('No influence data for target influence {0}! Unable to move weights...'.format(targetInf))
        
        # Check Mode
        if not ['add','replace'].count(mode):
            raise Exception('Invalid mode value ("'+mode+'")!')
        
        # Move Weights
        sourceWt = self._influenceData[sourceInf]['wt']
        targetWt = self._influenceData[targetInf]['wt']
        if mode == 'add':
            self._influenceData[targetInf]['wt'] = [i[0]+i[1] for i in zip(sourceWt,targetWt)]
        elif mode == 'replace':
            self._influenceData[targetInf]['wt'] = [i for i in sourceWt]
        self._influenceData[sourceInf]['wt'] = [0.0 for i in sourceWt]
        
        # Return Result
        print('SkinClusterData: Move Weights Complete - "'+sourceInf+'" >> "'+targetInf+'"')
        
    
    def remapInfluence(self,oldInfluence, newInfluence):
        ''' Remap stored skinCluster influence data from one influence to another
        :param oldInfluence str: The influence to remap from. Source influence
        :param newInfluence str: The influence to remap to. Target influence
        '''
        # Check influence
        if not self._influenceData.has_key(oldInfluence):
            print('No data stored for influence {0} in skinCluster {1}! Skipping...'.format(oldInfluence, self._data['name']))
            return 
        
        # Update influence data
        self._influenceData[newInfluence] = self._influenceData[oldInfluence]
        self._influenceData.pop(oldInfluence)
        
        # Print message
        print('Remapped influence {0} to {1} for skinCluster {2}!'.format(oldInfluence, newInfluence, self._data['name']))
        
    
    def combineInfluence(self,sourceInfluenceList, targetInfluence, removeSource=False):
        ''' Combine stored skinCluster influence data from a list of source influences to a single target influence.
            Source influences data will be removed.
        :param sourceInfluenceList str: The list influence data to combine
        :param targetInfluence str: The target influence to remap the combined data to.
        '''
        # ===========================
        # - Check Source Influences -
        # ===========================
        
        skipSource = []
        for i in range(len(sourceInfluenceList)):
            
            # Check influence
            if not self._influenceData.has_key(sourceInfluenceList[i]):
                print('No data stored for influence "'+sourceInfluenceList[i]+'" in skinCluster "'+self._data['name']+'"! Skipping...')
                skipSource.append(sourceInfluenceList[i])
        
        # =============================
        # - Initialize Influence Data -
        # =============================
        
        if list(set(sourceInfluenceList)-set(skipSource)):
            if not self._influenceData.has_key(targetInfluence):
                self._influenceData[targetInfluence] = {'index':0,'type':0,'bindPreMatrix':''}
        else:
            return
        
        # ==========================
        # - Combine Influence Data -
        # ==========================
        
        wtList = []
        for i in range(len(sourceInfluenceList)):
            
            # Get Source Influence
            sourceInfluence = sourceInfluenceList[i]
            
            # Check Skip Source
            if skipSource.count(sourceInfluence): continue
            
            # Get Basic Influence Data from first source influence
            if not i:
                
                # Index
                self._influenceData[targetInfluence]['index'] = self._influenceData[sourceInfluence]['index']
                
                # Type
                self._influenceData[targetInfluence]['type'] = self._influenceData[sourceInfluence]['type']
                
                # Poly Smooth
                if self._influenceData[sourceInfluence].has_key('polySmooth'):
                    self._influenceData[targetInfluence]['polySmooth'] = self._influenceData[sourceInfluence]['polySmooth']
                else:
                    if self._influenceData[targetInfluence].has_key('polySmooth'):
                        self._influenceData[targetInfluence].pop('polySmooth')
                
                # Nurbs Samples
                if self._influenceData[sourceInfluence].has_key('nurbsSamples'):
                    self._influenceData[targetInfluence]['nurbsSamples'] = self._influenceData[sourceInfluence]['nurbsSamples']
                else:
                    if self._influenceData[targetInfluence].has_key('nurbsSamples'):
                        self._influenceData[targetInfluence].pop('nurbsSamples')
            
                # Get Source Influence Weights 
                wtList = self._influenceData[sourceInfluence]['wt']
            
            else:
                
                if wtList:
                
                    # Combine Source Influence Weights
                    wtList = [(x+y) for x,y in zip(wtList,self._influenceData[sourceInfluence]['wt'])]
                
                else:
                    
                    wtList = self._influenceData[sourceInfluence]['wt']
        
        # ==================================
        # - Assign Combined Source Weights -
        # ==================================
        self._influenceData[targetInfluence]['wt'] = wtList
        
        # =======================================
        # - Remove Unused Source Influence Data -
        # =======================================
        if removeSource:
        
            # For Each Source Influence
            for sourceInfluence in sourceInfluenceList:
                
                # Check Skip Source
                if skipSource.count(sourceInfluence): continue
                
                # Check Source/Target
                if sourceInfluence != targetInfluence:
                    
                    # Remove Unused Source Influence
                    self._influenceData.pop(sourceInfluence)
                    
    
    def remapGeometry(self,geometry):
        ''' Remap the skinCluster data for one geometry to another
        :param geometry str: The geometry to remap to the skinCluster
        '''
        # Checks
        oldGeometry = self._data['affectedGeometry'][0]
        if geometry == oldGeometry: return geometry
            
        # Check Skin Geo Data
        if not self._data.has_key(oldGeometry):
            raise Exception('SkinClusterData: No skin geometry data for affected geometry "'+oldGeometry+'"!')
        
        # Remap Geometry
        self._data['affectedGeometry'] = [geometry]
        
        # Update Skin Geo Data
        self._data[geometry] = self._data[oldGeometry]
        self._data.pop(oldGeometry)
        
        # Print Message
        print('Geometry for skinCluster "'+self._data['name']+'" remaped from "'+oldGeometry+'" to "'+geometry+'"')
        
        # Return result
        return self._data['affectedGeometry']
    
    
    def rebuildWorldSpaceData(self,targetGeo='', method='closestPoint'):
        ''' Rebuild the skinCluster deformer membership and weight arrays for the specified geometry using the stored world space geometry data.
        :param targetGeo str: Geometry to rebuild world space deformer data for. If empty, use sourceGeo.
        :param method str: Method for worldSpace transfer. Valid options are "closestPoint" and "normalProject".
        '''
        # Start timer
        timer = cmds.timerX()
        
        # Display Progress
        progressBar.init(status=('Rebuilding world space skinCluster data...'), maxValue=100)
        
        # Get Source Geometry
        sourceGeo = self._data['affectedGeometry'][0]
        
        # Target Geometry
        if not targetGeo: targetGeo = sourceGeo
        
        # Check Deformer Data
        if not self._data.has_key(sourceGeo):
            progressBar.end()
            raise Exception('No deformer data stored for geometry {0}!'.format(sourceGeo))
        
        # Check Geometry
        if not cmds.objExists(targetGeo):
            progressBar.end()
            raise Exception('Geometry {0} does not exist!'.format(targetGeo))
        if not easy.isMesh(targetGeo):
            progressBar.end()
            raise Exception('Geometry {0} is not a valid mesh!'.format(targetGeo))
        
        # Check Mesh Data
        if not self._data[sourceGeo].has_key('mesh'):
            progressBar.end()
            raise Exception('No world space mesh data stored for mesh geometry {0}!'.format(sourceGeo))
        
        meshData = self._data[sourceGeo]['mesh']._data
        
        meshUtil = om.MScriptUtil()
        numVertices = len(meshData['vertexList'])/3
        numPolygons = len(meshData['polyCounts'])
        polygonCounts = om.MIntArray()
        polygonConnects = om.MIntArray()
        meshUtil.createIntArrayFromList(meshData['polyCounts'], polygonCounts)
        meshUtil.createIntArrayFromList(meshData['polyConnects'], polygonConnects)
        
        # Rebuild Vertex Array
        vertexArray = om.MFloatPointArray(numVertices, om.MFloatPoint.origin)
        vertexList = [vertexArray.set(i, meshData['vertexList'][i*3], meshData['vertexList'][i*3+1], meshData['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]
        
        # Rebuild Mesh
        meshFn = om.MFnMesh()
        meshDataFn = om.MFnMeshData().create()
        meshObj = meshFn.create(numVertices, numPolygons, vertexArray, polygonCounts, polygonConnects, meshDataFn)
        
        # Create Mesh Intersector
        meshPt = om.MPointOnMesh()
        meshIntersector = om.MMeshIntersector()
        if method == 'closestPoint': meshIntersector.create(meshObj)
        
        # ========================================
        # - Rebuild Weights and Membership List -
        # ========================================
        
        # Initialize Influence Weights and Membership
        influenceList = self._influenceData.keys()
        influenceWt = [[] for inf in influenceList]
        membership = set([])
        
        # Get Target Mesh Data
        targetMeshFn = easy.getMeshFn(targetGeo)
        targetMeshPts = targetMeshFn.getRawPoints()
        numTargetVerts = targetMeshFn.numVertices()
        targetPtUtil = om.MScriptUtil()
        
        # Initialize Float Pointers for Barycentric Coords
        uUtil = om.MScriptUtil(0.0)
        vUtil = om.MScriptUtil(0.0)
        uPtr = uUtil.asFloatPtr()
        vPtr = vUtil.asFloatPtr()
        
        # Get Progress Step
        progressInd = int(numTargetVerts*0.01)
        if progressInd < 1: progressInd = 1 
        
        for i in range(numTargetVerts):
            
            # Get Target Point
            targetPt = om.MPoint(    targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+0),
                                        targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+1),
                                        targetPtUtil.getFloatArrayItem(targetMeshPts,(i*3)+2)    )
            
            # Get Closest Point Data
            meshIntersector.getClosestPoint(targetPt,meshPt)
            
            # Get Barycentric Coords
            meshPt.getBarycentricCoords(uPtr,vPtr)
            u = om.MScriptUtil(uPtr).asFloat()
            v = om.MScriptUtil(vPtr).asFloat()
            baryWt = [u,v,1.0-(u+v)]
            
            # Get Triangle Vertex IDs
            idUtil = om.MScriptUtil([0,1,2])
            idPtr = idUtil.asIntPtr()
            meshFn.getPolygonTriangleVertices(meshPt.faceIndex(),meshPt.triangleIndex(),idPtr)
            triId = [om.MScriptUtil().getIntArrayItem(idPtr,n) for n in range(3)]
            memId = [self._data[sourceGeo]['membership'].count(t) for t in triId]
            wtId = [self._data[sourceGeo]['membership'].index(t) for t in triId]
            
            # For Each Influence
            for inf in range(len(influenceList)):
                
                # Calculate Weight and Membership
                wt = 0.0
                isMember = False
                for n in range(3):
                    
                    # Check Against Source Membership
                    if memId[n]:
                        wt += self._influenceData[influenceList[inf]]['wt'][wtId[n]] * baryWt[n]
                        isMember = True
                
                # Check Member
                if isMember:
                    # Append Weight Value
                    influenceWt[inf].append(wt)
                    # Append Membership
                    membership.add(i)
            
            # Update Progress Bar
            if not i % progressInd: progressBar.update(step=1)
        
        # ========================
        # - Update Deformer Data -
        # ========================
        
        # Remap Geometry
        self.remapGeometry(targetGeo)
        
        # Rename SkinCluster
        targetSkinCluster = skinCluster.findRelatedSkinCluster(targetGeo)
        if targetSkinCluster:
            self._data['name'] = targetSkinCluster
        else:
            prefix = targetGeo.split(':')[-1]
            self._data['name'] = prefix+'_skinCluster'
        
        # Update Membership and Weights
        self._data[sourceGeo]['membership'] = list(membership)
        for inf in range(len(influenceList)):
            self._influenceData[influenceList[inf]]['wt'] = influenceWt[inf]
        
        # =================
        # - Return Result -
        # =================
        
        # End Progress
        progressBar.end()    
        
        # Print Timed Result
        buildTime = cmds.timerX(st=timer)
        print('SkinClusterData: Rebuild world space data for skinCluster {0}: {1}'.format(self._data['name'], str(buildTime)))
        
        # Return Weights
        return
    
    
    def mirror(self,search='l_',replace='r_'):
        ''' Mirror SkinCluster Data using search and replace for naming.
            This method doesn't perform closest point on surface mirroring.
        :param search str: Search for this string in skinCluster, geometry and influence naming and replace with the "replace" string.
        :param replace str: The string to replace all instances of the "search" string for skinCluster, geometry and influence naming.
        '''
        
        if self._data['name'].count(search):
            self._data['name'] = self._data['name'].replace(search,replace)
        
        for i in range(len(self._data['affectedGeometry'])):
            
            if self._data['affectedGeometry'][i].count(search):
                # Get 'mirror' geometry
                mirrorGeo = self._data['affectedGeometry'][i].replace(search,replace)
                # Check 'mirror' geometry
                if not cmds.objExists(mirrorGeo):
                    print ('WARNING: Mirror geoemtry {0} does not exist!'.format(mirrorGeo))
                # Assign 'mirror' geometry
                self.remapGeometry(mirrorGeo)
                #self._data['affectedGeometry'][i] = mirrorGeo
        
        # Search and Replace Inlfuences
        influenceList = self._influenceData.keys()
        for i in range(len(influenceList)):
            
            if influenceList[i].count(search):
                # Get 'mirror' influence
                mirrorInfluence = influenceList[i].replace(search, replace)
                # Check 'mirror' influence
                if not cmds.objExists(mirrorInfluence):
                    print ('WARNING: Mirror influence {0} does not exist!'.format(mirrorInfluence))
                # Assign 'mirror' influence
                self.remapInfluence(influenceList[i], mirrorInfluence)
                

class SkinClusterListData( data.Data ):
    ''' SkinCluster List Data Class Object
        Contains functions to save, load and rebuild multiple skinCluster data.
    '''
    def __init__(self):
        '''
        SkinClusterListData class initializer.
        '''
        # Execute Super Class Initilizer
        super(SkinClusterListData, self).__init__()
    
    def buildData(self, skinClusterList):
        ''' Build SkinClusterList data.
        :param skinClusterList list: List of skinClusters to build data for
        '''
        # For Each SkinCluster
        for skc in skinClusterList:
            
            # Check skinCluster
            if not cmds.objExists(skc):
                raise Exception('SkinCluster {0} does not exist!'.format(skc))
            if not skinCluster.isSkinCluster(skc):
                raise Exception('{0} is not a valid skinCluster!'.format(skc))
            
            # Build SkinCLuster Data
            self._data[skc] = SkinClusterData()
            self._data[skc].buildData(skc)
            
    
    def rebuild(self,skinClusterList):
        ''' Rebuild a list of skinClusters from the stored SkinClusterListData
        :param skinClusterList dict: List of skinClusters to rebuild
        '''
        # Start timer
        timer = cmds.timerX()
        
        # For Each SkinCluster
        for skc in skinClusterList:
            
            # Check skinClusterData
            if not self._data.has_key(skc):
                print('No data stored for skinCluster {0}! Skipping...'.format(skc))
            
            # Rebuild SkinCluster
            self._data[skc].rebuild()
        
        # Print timed result
        totalTime = cmds.timerX(st=timer)
        print('SkinClusterListData: Total build time for skinCluster list: {0}'.format(str(totalTime)))
        
    
        
        
