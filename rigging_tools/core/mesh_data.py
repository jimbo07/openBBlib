'''
Created on 28 Sep 2018

@author: lasse-r
'''
import maya.cmds as cmds
import maya.OpenMaya as om

from ooutdmaya.rigging.core.util.IO import data
from ooutdmaya.rigging.core.util import easy

class MeshData( data.Data ):
    '''
    MeshData class object.
    Contains functions to save, load and rebuild maya mesh data.
    '''
    def __init__(self,mesh=''):
        '''
        MeshData class initializer.
        '''
        # Execute Super Class Initilizer
        super(MeshData, self).__init__()

        # Initialize Class Defaults
        self.maxDist = 9999999.9
        
        # Initialize Default Class Data Members
        self._data['name'] = ''
        self._data['vertexList'] = []
        self._data['polyCounts'] = []
        self._data['polyConnects'] = []
        
        self._data['uvCounts'] = []
        self._data['uvIds'] = []
        self._data['uArray'] = []
        self._data['vArray'] = []
        
        # Build Data
        if mesh: self.buildData(mesh)

    def buildData(self, mesh):
        ''' Build meshData class.
        :param mesh str: Mesh to initialize data for
        '''
        # Check Mesh
        if not easy.isMesh(mesh):
            raise Exception('Object {0} is not a vaild Mesh node!'.format(mesh))
        
        # Start timer
        timer = cmds.timerX()
        
        # Get basic mesh info
        self._data['name'] = mesh

        # Get Mesh Function Class
        meshFn = easy.getMeshFn(mesh)

        # Get Polygon Data
        polygonCounts = om.MIntArray()
        polygonConnects = om.MIntArray()
        meshFn.getVertices(polygonCounts,polygonConnects)
        self._data['polyCounts'] = list(polygonCounts)
        self._data['polyConnects'] = list(polygonConnects)

        # Get Vertex Data
        meshPts = meshFn.getRawPoints()
        numVerts = meshFn.numVertices()
        meshPtUtil = om.MScriptUtil()
        self._data['vertexList'] = [meshPtUtil.getFloatArrayItem(meshPts,i) for i in xrange(numVerts*3)]
        
        # UV Connect Data
        uvCounts = om.MIntArray()
        uvIds = om.MIntArray()
        meshFn.getAssignedUVs(uvCounts,uvIds)
        self._data['uvCounts'] = list(uvCounts)
        self._data['uvIds'] = list(uvIds)
        
        # Get UVs
        uArray = om.MFloatArray()
        vArray = om.MFloatArray()
        meshFn.getUVs(uArray,vArray)
        self._data['uArray'] = list(uArray)
        self._data['vArray'] = list(vArray)

        # Print timer result
        buildTime = cmds.timerX(st=timer)
        print("MeshData: Data build time for mesh {0}: {1}".format(mesh, str(buildTime)))
        
        return self._data['name']

    def rebuild(self):
        '''
        '''
        # Start timer
        timer = cmds.timerX()

        # Rebuild Mesh Data
        meshUtil = om.MScriptUtil()
        numVertices = len(self._data['vertexList'])/3
        numPolygons = len(self._data['polyCounts'])
        polygonCounts = om.MIntArray()
        polygonConnects = om.MIntArray()
        meshUtil.createIntArrayFromList(self._data['polyCounts'], polygonCounts)
        meshUtil.createIntArrayFromList(self._data['polyConnects'], polygonConnects)
        
        # Rebuild UV Data
        uvCounts = om.MIntArray()
        uvIds = om.MIntArray()
        meshUtil.createIntArrayFromList(self._data['uvCounts'], uvCounts)
        meshUtil.createIntArrayFromList(self._data['uvIds'], uvIds)
        uArray = om.MFloatArray()
        vArray = om.MFloatArray()
        meshUtil.createFloatArrayFromList(self._data['uArray'], uArray)
        meshUtil.createFloatArrayFromList(self._data['vArray'], vArray)

        # Rebuild Vertex Array
        vertexArray = om.MFloatPointArray(numVertices,om.MFloatPoint.origin)
        vertexList = [vertexArray.set(i, self._data['vertexList'][i*3], self._data['vertexList'][i*3+1], self._data['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]

        # Rebuild Mesh
        meshFn = om.MFnMesh()
        meshData = om.MFnMeshData().create()
        meshObj = meshFn.create(numVertices,
                                numPolygons,
                                vertexArray,
                                polygonCounts,
                                polygonConnects,
                                uArray,
                                vArray,
                                meshData)
        
        # Assign UVs
        meshFn.assignUVs(uvCounts,uvIds)
        
        meshObjHandle = om.MObjectHandle(meshObj)

        # Print Timed Result
        buildTime = cmds.timerX(st=timer)
        print("MeshIntersectData: Data rebuild time for mesh {0}: {1}".format(self._data['name'], str(buildTime)))
        
        return meshObjHandle

    def rebuildMesh(self):
        '''
        '''
        # Start timer
        timer = cmds.timerX()

        # Rebuild Mesh Data
        meshData = om.MObject()
        meshUtil = om.MScriptUtil()
        numVertices = len(self._data['vertexList'])/3
        numPolygons = len(self._data['polyCounts'])
        polygonCounts = om.MIntArray()
        polygonConnects = om.MIntArray()
        meshUtil.createIntArrayFromList(self._data['polyCounts'],polygonCounts)
        meshUtil.createIntArrayFromList(self._data['polyConnects'],polygonConnects)
        
        # Rebuild UV Data
        uArray = om.MFloatArray()
        vArray = om.MFloatArray()
        meshUtil.createFloatArrayFromList(self._data['uArray'],uArray)
        meshUtil.createFloatArrayFromList(self._data['vArray'],vArray)
        uvCounts = om.MIntArray()
        uvIds = om.MIntArray()
        meshUtil.createIntArrayFromList(self._data['uvCounts'],uvCounts)
        meshUtil.createIntArrayFromList(self._data['uvIds'],uvIds)

        # Rebuild Vertex Array
        vertexArray = om.MFloatPointArray(numVertices,om.MFloatPoint.origin)
        vertexList = [vertexArray.set(i,self._data['vertexList'][i*3],self._data['vertexList'][i*3+1],self._data['vertexList'][i*3+2],1.0) for i in xrange(numVertices)]

        # Rebuild Mesh
        meshFn = om.MFnMesh()
        meshObj = meshFn.create(    numVertices,
                                    numPolygons,
                                    vertexArray,
                                    polygonCounts,
                                    polygonConnects,
                                    uArray,
                                    vArray,
                                    meshData    )
        
        # Assign UVs
        meshFn.assignUVs(uvCounts,uvIds)

        # Rename Mesh
        mesh = om.MFnDependencyNode(meshObj).setName(self._data['name']+"WSMesh")
        meshShape = cmds.listRelatives(mesh, s=True, ni=True, pa=True)[0]

        # Assign Initial Shading Group
        cmds.sets(meshShape,fe='initialShadingGroup')

        # Print timer result
        buildTime = cmds.timerX(st=timer)
        print("MeshIntersectData: Geometry rebuild time for mesh {0}: {1}".format(mesh, str(buildTime)))
        
        return mesh
    
    
    
