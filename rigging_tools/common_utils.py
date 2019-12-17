from .mesh import lib as mesh
reload(mesh)

from maya import cmds
#test

# Method for finding closest UV value on mesh and attaching anchor point.
def makePointOnMesh(objectOne,objectTwo,type='follicle'):

    closestUV_point = mesh.get_closest_uv_on_mesh(objectTwo, cmds.xform(objectOne, t=True, q=True, ws=True))
    closestUV = [closestUV_point[0], closestUV_point[1]]

    if type == "pointOnPoly":
        # Create Null to attach to surface.
        anchorPoint = cmds.group(em=1,n="{}_polyAnchor".format(objectOne))
        # Create constraint between input object and mesh.
        polyConstraint = cmds.pointOnPolyConstraint(objectTwo,anchorPoint)
        
        # Set constraint UV value to closest UV value stored previously.
        cmds.setAttr( '{}.{}U0'.format(polyConstraint[0],objectTwo), closestUV[0] )

        cmds.setAttr('{}.{}V0'.format(polyConstraint[0],objectTwo), closestUV[1] )

        return anchorPoint

    elif type == "follicle":
        anchorPoint = cmds.createNode("follicle",n='{}_polyAnchorShape'.format(objectOne))

        anchorParent = cmds.listRelatives(anchorPoint,p=1)
        cmds.rename(anchorParent,str(objectOne)+"_polyAnchor")
        inputMeshShape = cmds.listRelatives(objectTwo,type="shape")
        cmds.connectAttr("{}.outMesh".format(inputMeshShape[0]), "{}.inputMesh".format(anchorPoint))
        cmds.connectAttr("{}.worldMatrix[0]".format(objectTwo),"{}.inputWorldMatrix".format(anchorPoint))
        cmds.connectAttr("{}.outRotate".format(anchorPoint),"{}.rotate".format(anchorParent[0]))
        cmds.connectAttr("{}.outTranslate".format(anchorPoint),"{}.translate".format(anchorParent[0]))
        cmds.setAttr("{}.parameterU".format(anchorPoint), closestUV[0] )
        cmds.setAttr("{}.parameterV".format(anchorPoint), closestUV[1] )
        return anchorParent
    

def find_neighbours(source, targets, threshold=1):
    '''
    Finds neighbours from list of potential candidates within a threshold.
    :param source: str | main object to measure from
    :param targets: list | list of potential neighbours
    :param threshold: float | minimum distance to be considered a neighbour
    :return: list of neighbors
    '''
    verts = cmds.polyEvaluate(source, v=True)

    inside = []
    for vert in range(0,verts,3):
        vert_pos = cmds.xform('{}.vtx[{}]'.format(source, vert), t=True, q=True, ws=True)
        for other in targets:
            closest = mesh.get_closest_point(other, vert_pos)
            if closest['distance'] < threshold:
                inside.append(other)
    inside = list(set(inside))
    return inside


def find_closest_mesh(point, targets):
    '''
    Finds closest mesh to a point in a list of meshes.
    :param point: list | point to measure from
    :param targets: list | list of meshes to check from.
    :return: closest mesh
    '''
    
    
    closest_mesh = []
    shortest = None
    for msh in targets:
        if cmds.objectType(msh) == 'mesh':
            msh = cmds.listRelatives(msh, parent=True)[0]
        closest_point = mesh.get_closest_point(msh, point)
        if closest_point['distance'] < shortest or not shortest:
            closest_mesh = msh
            shortest = closest_point['distance']
    
    return closest_mesh
