#Move this stuff to a library!
try:
    import zBuilder.builders.ziva as zva
except:
    print 'ZivaPlugin not loaded'
import os
from maya import cmds,mel



def save_ziva(file_path, solver=False):
    if solver:
        if not cmds.objExists(solver):
            cmds.warning('Solver "{}" cannot be found.'.format(solver))
            return
        if not cmds.objectType(solver) == 'zSolverTransform':
            cmds.warning('{} is of type {} not zSolverTransform.'.format(solver, cmds.objectType(solver)))            
            return
        if not os.path.isdir(file_path.rpartition('/')[0]):
            cmds.warning('Directory {} does not exist.'.format(file_path.rpartition('/')[0]))
            return

        z = zva.Ziva()
        z.retrieve_from_scene()
        z.write(file_path)

def load_ziva(file_path):
    if not os.path.isdir(file_path.rpartition('/')[0]):
        cmds.warning('File {} does not exist.'.format(file_path))
        return

    z = zva.Ziva()
    z.retrieve_from_file(file_path)
    z.build()

def zPolyCombine(meshes, name, parent=False):
    current_selection = cmds.ls(sl=True)

    cmds.select(meshes, r=True)
    node,transform = mel.eval('zPolyCombine')
    transform = cmds.rename(transform, name)
    node = cmds.rename(node, '{}_zPolyCombine'.format(name))
    if parent:
        cmds.parent(transform, parent)

    cmds.select(current_selection)
    return node

def zSolver(
    name=None,
    enable=1,
    startFrame=1,
    collisionDetection=0,
    collisionPointSpacing=0.1,
    quasiStatic=0,
    maxNewtonIterations=10,
    substeps=1,
    framesPerSecond=24,
    stiffnessDamping=0.01,
    massDamping=0,
    gravityX=0,
    gravityY=-9.8,
    gravityZ=0,
    showBones=1,
    showTetMeshes=1,
    showAttachments=1,
    showCollisions=1,
    showMaterials=1,
    showMuscleFibers=1,
    showAxes=1,
    parent='dynamics_grp'
    ):
    shape,transform,embedder = mel.eval('ziva -solver')
    
    if name:
        shape = cmds.rename(shape,'{}_zSolverShape'.format(name))
        transform = cmds.rename(transform,'{}_zSolver'.format(name))
        embedder = cmds.rename(embedder,'{}_zEmbedder'.format(name))

    if cmds.objExists(parent):
        cmds.parent(transform, parent)
    else:
        print '{} does not exist, cannot parent.'.format(parent)

    cmds.setAttr("{}.enable".format(transform), enable)
    cmds.setAttr("{}.startFrame".format(transform), startFrame)

    cmds.setAttr("{}.collisionDetection".format(shape), collisionDetection)
    cmds.setAttr("{}.quasiStatic".format(shape), quasiStatic)
    cmds.setAttr("{}.maxNewtonIterations".format(shape), maxNewtonIterations)
    cmds.setAttr("{}.substeps".format(shape), substeps)
    cmds.setAttr("{}.framesPerSecond".format(shape), framesPerSecond)
    cmds.setAttr("{}.stiffnessDamping".format(shape), stiffnessDamping)
    cmds.setAttr("{}.massDamping".format(shape), massDamping)
    cmds.setAttr("{}.gravityX".format(shape), gravityX)
    cmds.setAttr("{}.gravityY".format(shape), gravityY)
    cmds.setAttr("{}.gravityZ".format(shape), gravityZ)
    cmds.setAttr("{}.showBones".format(shape), showBones)
    cmds.setAttr("{}.showTetMeshes".format(shape), showTetMeshes)
    cmds.setAttr("{}.showAttachments".format(shape), showAttachments)
    cmds.setAttr("{}.showCollisions".format(shape), showCollisions)
    cmds.setAttr("{}.showMaterials".format(shape), showMaterials)
    cmds.setAttr("{}.showMuscleFibers".format(shape), showMuscleFibers)
    cmds.setAttr("{}.showAxes".format(shape), showAxes)

    return [shape,transform,embedder]


def zBone(
        mesh,
        name=None,
        solver=False,
        collisions=1,
        collisionVolume=1,
        hardContact=0,
        contactStiffness=1,
        contactStiffnessExp=8,
        contactSliding=1
        ):

    if solver:
        if not cmds.objExists(solver):
            cmds.warning('{} does not exist.'.format(solver))
            return
        if not cmds.objectType(solver) == 'zSolverTransform':
            cmds.warning('{} is not a ziva solver.'.format(solver))
            return
    
    if not name and '_mesh' in mesh:
        name = mesh.replace('_mesh', '')
    elif not name:
        name = mesh
    
    current_selection = cmds.ls(sl=True)

    cmds.select(mesh, r=True)
    if solver:
        cmds.select(solver, add=True)
    geo,bone = mel.eval('ziva -bone')

    geo = cmds.rename(geo, '{}_zGeo'.format(name))
    bone = cmds.rename(bone, '{}_zBone'.format(name))

    cmds.setAttr("{}.collisions".format(bone), collisions)
    cmds.setAttr("{}.collisionVolume".format(bone), collisionVolume)
    cmds.setAttr("{}.hardContact".format(bone), hardContact)
    cmds.setAttr("{}.contactStiffness".format(bone), contactStiffness)
    cmds.setAttr("{}.contactStiffnessExp".format(bone), contactStiffnessExp)
    cmds.setAttr("{}.contactSliding".format(bone), contactSliding)
    
    cmds.select(current_selection)

    return [geo,bone]


def zTissue(
        mesh,
        name=None,
        solver=False,
        # Tissue attributes
        enable=1,
        material=0,
        compressionResistance=2000,
        inertialDamping=0,
        collisions=1,
        collisionVolume=1,
        selfCollisions=0,
        hardContact=0,
        contactStiffness=1,
        contactStiffnessExp=8,
        contactSliding=1,
        # Tet attributes
        tetSize=False,
        surfaceRefinement=1,
        refinementPropagation=0,
        fillInterior=1,
        maxResolution=150,
        # Material attributes
        youngsModulus=12,
        youngsModulusExp=3,
        poissonsRatio=0.4,
        volumeConservation=0,
        volumeConservationExp=6,
        massDensity=1060
        ):

    if solver:
        if not cmds.objExists(solver):
            cmds.warning('{} does not exist.'.format(solver))
            return
        if not cmds.objectType(solver) == 'zSolverTransform':
            cmds.warning('{} is not a ziva solver.'.format(solver))
            return
    else:
        print 'Target solver must be supplied'
        return
        
    if not name and '_mesh' in mesh:
        name = mesh.replace('_mesh', '')
    elif not name:
        name = mesh
        
    current_selection = cmds.ls(sl=True)

    cmds.select(mesh, r=True)
    if solver:
        cmds.select(solver, add=True)

    zGeo, zTissue, zTet, zMaterial = mel.eval('ziva -tissue')

    zGeo = cmds.rename(zGeo, '{}_zGeo'.format(name))
    zTissue = cmds.rename(zTissue, '{}_zTissue'.format(name))
    zTet = cmds.rename(zTet, '{}_zTet'.format(name))
    zMaterial = cmds.rename(zMaterial, '{}_zMaterial'.format(name))

    # Tissue attributes.
    cmds.setAttr("{}.enable".format(zTissue), enable)
    cmds.setAttr("{}.material".format(zTissue), material)
    cmds.setAttr("{}.compressionResistance".format(zTissue), compressionResistance)
    cmds.setAttr("{}.inertialDamping".format(zTissue), inertialDamping)
    cmds.setAttr("{}.collisions".format(zTissue), collisions)
    if collisionVolume:
        cmds.setAttr("{}.collisionVolume".format(zTissue), l=False)
        cmds.setAttr("{}.collisionVolume".format(zTissue), collisionVolume)
    cmds.setAttr("{}.selfCollisions".format(zTissue), selfCollisions)
    cmds.setAttr("{}.hardContact".format(zTissue), hardContact)
    cmds.setAttr("{}.contactStiffness".format(zTissue), contactStiffness)
    cmds.setAttr("{}.contactStiffnessExp".format(zTissue), contactStiffnessExp)
    cmds.setAttr("{}.contactSliding".format(zTissue), contactSliding)

    # Tet attributes.
    if tetSize:
        cmds.setAttr("{}.tetSize".format(zTet), tetSize)
    cmds.setAttr("{}.surfaceRefinement".format(zTet), surfaceRefinement)
    cmds.setAttr("{}.refinementPropagation".format(zTet), refinementPropagation)
    cmds.setAttr("{}.fillInterior".format(zTet), fillInterior)
    cmds.setAttr("{}.maxResolution".format(zTet), maxResolution)

    # Material attributes.
    cmds.setAttr("{}.youngsModulus".format(zMaterial), youngsModulus)
    cmds.setAttr("{}.youngsModulusExp".format(zMaterial), youngsModulusExp)
    cmds.setAttr("{}.poissonsRatio".format(zMaterial), poissonsRatio)
    cmds.setAttr("{}.volumeConservation".format(zMaterial), volumeConservation)
    cmds.setAttr("{}.volumeConservationExp".format(zMaterial), volumeConservationExp)
    cmds.setAttr("{}.massDensity".format(zMaterial), massDensity)

    cmds.select(current_selection)

    return [zGeo, zTissue, zTet, zMaterial]


def zAttachment(
    mesh1,
    mesh2,
    name=False,
    tag=False,
    solver=False,
    envelope=1,
    attachmentMode='fixed',
    stiffness=1,
    stiffnessExp=8,
    isHard=0,
    maintainOffset=1,
    correspondence=0,
    show=1,
    # paintByProximity settings.
    paintByProximity=True,
    falloff_min=0,
    falloff_max=2
    ):
    current_selection = cmds.ls(sl=True)

    cmds.select([mesh1,mesh2], r=True)
    if solver:
        cmds.select(solver, add=True)

    zAttachment = mel.eval('ziva -attachment')

    if name:
        if tag:
            zAttachment = cmds.rename(zAttachment, '{}_{}_zAttachment'.format(name, tag))
        else:
            zAttachment = cmds.rename(zAttachment, '{}_zAttachment'.format(name))
    else:
        if tag:
            zAttachment = cmds.rename(zAttachment, '{}_{}_{}_zAttachment'.format(mesh1, mesh2, tag))
        else:
            zAttachment = cmds.rename(zAttachment, '{}_{}_zAttachment'.format(mesh1, mesh2))

    if attachmentMode == 'none':
        attachmentMode = 0
    if attachmentMode == 'fixed':
        attachmentMode = 1
    if attachmentMode == 'sliding':
        attachmentMode = 2

    cmds.setAttr("{}.envelope".format(zAttachment), envelope)
    cmds.setAttr("{}.attachmentMode".format(zAttachment), attachmentMode)
    cmds.setAttr("{}.stiffness".format(zAttachment), stiffness)
    cmds.setAttr("{}.stiffnessExp".format(zAttachment), stiffnessExp)
    cmds.setAttr("{}.isHard".format(zAttachment), isHard)
    cmds.setAttr("{}.maintainOffset".format(zAttachment), maintainOffset)
    cmds.setAttr("{}.correspondence".format(zAttachment), correspondence)
    cmds.setAttr("{}.show".format(zAttachment), show)

    if paintByProximity:
        paint_attachments_by_proximity(zAttachment, falloff_min, falloff_max)

    cmds.select(current_selection)
    return zAttachment




def zFiber(
        mesh,
        name=None,
        ):

    if not name and '_mesh' in mesh:
        name = mesh.replace('_mesh', '')
    elif not name:
        name = mesh
    
    current_selection = cmds.ls(sl=True)

    cmds.select(mesh, r=True)
    
    fiber = mel.eval('ziva -f')[0]

    fiber = cmds.rename(fiber, '{}_zFiber'.format(name))

#     cmds.setAttr("{}.collisions".format(bone), collisions)
    
    cmds.select(current_selection)

    return fiber

def zLineOfAction(
        crv,
        mesh,
        name=None,
        ):

    if not name and '_mesh' in mesh:
        name = mesh.replace('_mesh', '')
    elif not name:
        name = mesh
    
    current_selection = cmds.ls(sl=True)
    
    cmds.select(crv, r=True)
    cmds.select(mesh, add=True)
    
    loa = mel.eval('ziva -loa')[0]

    loa = cmds.rename(loa, '{}_zLineOfAction'.format(name))

#     cmds.setAttr("{}.collisions".format(bone), collisions)
    
    cmds.select(current_selection)

    return loa



def paint_attachments_by_proximity(attachments, falloff_min=0, falloff_max=2):
    '''
    A wrapper for ziva's proximity painting tool.
    :param attachments: list | list of attachments to proccess.
    :param falloff_min: minimum distance for falloff
    :param falloff_max: maximum distance for falloff
    '''
    if not isinstance(attachments, list):
        attachments = [attachments]
    current_selection = cmds.ls(sl=True)
    for attachment in attachments:
        cmds.select(attachment, r=True)
        mel.eval('zPaintAttachmentsByProximity -min {} -max {};'.format(falloff_min, falloff_max))
    cmds.select(current_selection)

def zQuery(mesh):
    '''
    Query a mesh for its attached ziva nodes.
    :param mesh: str | mesh object to be queried.
    :return: dict | dictionary with keys of each type and the result as the value.
    '''
    current_selection = cmds.ls(sl=True)

    cmds.select(mesh)
    tissue = mel.eval('zQuery -t zTissue')

    cmds.select(mesh)
    bone = mel.eval('zQuery -t zBone')

    cmds.select(mesh)
    attachments = mel.eval('zQuery -t zAttachment')

    cmds.select(mesh)
    cloth = mel.eval('zQuery -t zCloth')

    cmds.select(mesh)
    tet = mel.eval('zQuery -t zTet')

    cmds.select(mesh)
    materials = mel.eval('zQuery -t zMaterial')

    cmds.select(mesh)
    fibers = mel.eval('zQuery -t zFiber')

    cmds.select(current_selection)
    results = {
        'tissue':tissue,
        'bone':bone,
        'attachments':attachments,
        'cloth':cloth,
        'tet':tet,
        'materials':materials,
        'fibers':fibers
        }
    return results

def add_cache(solver):
    '''
    Adds ziva cache node to supplied ziva solver.
    :param solver: str | the zSolver which will have the cache node applied
    :return: list | [cache node transform, cache node shape]
    '''
    cache = mel.eval('ziva -acn')
    print cache
    return


