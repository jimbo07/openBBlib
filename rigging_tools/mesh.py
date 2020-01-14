from ooutdmaya.common import transform
from ooutdmaya.common.util import maths

reload(transform)
reload(maths)

from maya import cmds
import maya.api.OpenMaya as om


def get_face_type(obj):
    selectionList = om.MSelectionList()
    selectionList.add(obj)
    nodeDagPath = selectionList.getDagPath(0)
    
    mit = om.MItMeshPolygon(nodeDagPath)
    
    tris = []
    ngons = []
    quads = []
    
    for face in range(mit.count()):
        mit.setIndex(face)
        edges = mit.getEdges()
        if len(edges) == 3:
            tris.append(face)
        elif len(edges) > 4:
            ngons.append(face)
        elif len(edges) == 4:
            quads.append(face)
    return {'triangles':tris, 'ngons':ngons, 'quads':quads}

def get_boundary_edges(obj):
    selectionList = om.MSelectionList()
    selectionList.add(obj)
    nodeDagPath = selectionList.getDagPath(0)
    
    mit = om.MItMeshEdge(nodeDagPath)
    edges = {0:[]}
    for edge in range(mit.count()):
        mit.setIndex(edge)

        onBoundary = mit.onBoundary()
        if onBoundary:
            edges[0].append(edge)


    if edges[0]:
        return {'edges':edges}
    else:
        return {'edges':False}

def get_boundary_verticies(obj):
    selectionList = om.MSelectionList()
    selectionList.add(obj)
    nodeDagPath = selectionList.getDagPath(0)
    
    mit = om.MItMeshVertex(nodeDagPath)
    verts = {0:[]}
    for vert in range(mit.count()):
        mit.setIndex(vert)

        onBoundary = mit.onBoundary()
        if onBoundary:
            verts[0].append(vert)


    if verts[0]:
        return {'verticies':verts}
    else:
        return {'verticies':False}

def get_ray_mesh_intersection(mesh, direction=[0,-1 ,0], origin=[0,1,0]):
    direction_v = om.MFloatVector(direction[0],direction[1],direction[2])
    origin_p = om.MFloatPoint(origin[0],origin[1],origin[2])
    # return om.MVector(pnt1-pnt2).length()

    selectionList = om.MSelectionList()
    selectionList.add(mesh)
    nodeDagPath = selectionList.getDagPath(0)
    
    mfn = om.MFnMesh(nodeDagPath)

    intersection = mfn.closestIntersection(origin_p, direction_v, om.MSpace.kWorld, 99999999, False)


    #return intersection#list(intersection[0])[:-1]
    vector = list(intersection[0])[:-1]
    distance = maths.distanceBetween(origin, vector)
    return {'vector':vector, 'distance':distance}




def get_closest_point(mesh, point):
    point_p = om.MPoint(point[0],point[1],point[2])
    # return om.MVector(pnt1-pnt2).length()

    selectionList = om.MSelectionList()
    selectionList.add(mesh)
    nodeDagPath = selectionList.getDagPath(0)
    
    mfn = om.MFnMesh(nodeDagPath)

    intersection = mfn.getClosestPoint(point_p, om.MSpace.kWorld)


    #return intersection#list(intersection[0])[:-1]
    vector = list(intersection[0])
    MPoint = intersection[0]
    distance = maths.distanceBetween(point, vector)


    return {'vector':vector, 'distance':distance, 'MPoint':MPoint}


def get_closest_uv_on_mesh(mesh, transform):
    """
    get closest uv value to mesh
    :param mesh: str | mesh
    :param transform: str | node
    :return: MPoint
    """

    # get mesh
    
    print om.MSelectionList().add(mesh).getDagPath(0)
    
    mfn_mesh = om.MFnMesh(om.MSelectionList().add(mesh).getDagPath(0))

    point = get_closest_point(mesh, transform)['MPoint']

    closest_uv = mfn_mesh.getUVAtPoint(point, om.MSpace.kWorld)

    return closest_uv
