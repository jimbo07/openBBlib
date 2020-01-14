"""
generic lib for namning convention standards related to secret garden
"""
    
NODENAMEDICT = {
    'transform':'grp',
    'locator':'loc',
    'spaceLocator':'loc',
    'objectSet':'set',
    'curveInfo':'cvi',
    'pointOnCurveInfo':'pci',
    'joint':'jnt',
    'ikHandle':'ikh',
    'ikEffector':'eff',
    'endEffector':'eff',
    'plusMinusAverage': 'pma',
    'multDoubleLinear': 'mdl',
    'addDoubleLinear': 'adl',
    'multiplyDivide': 'mdn',
    'choice': 'chc',
    'blendShape': 'bls',
    'wrap': 'wrp',
    'skinCluster': 'skc',
    'cluster': 'csr',
    'clusterHandle': 'csh',
    'parentConstraint': 'pac',
    'pointConstraint': 'poc',
    'orientConstraint': 'oic',
    'scaleConstraint': 'sca',
    'aimConstraint': 'aic',
    'nurbsCurve': 'crv',
    'reverse': 'rvs',
    'multMatrix': 'mmx',
    'decomposeMatrix': 'dmx',
    'condition': 'cnd',
    'remapValue': 'rmv',
    'clamp': 'cmp',
    'cMuscleSmartConstraint':'msc',
    'avgCurves': 'avc',
    'geometry':'geo',
    'wireDeformer':'wrd',
    'pointOnPolyConstraint':'popc',
    'softMod':'smd',
    'motionPath':'mph',
    'rebuildCurve':'rbc',
    'starterCurve':'scrv',
    'displayLayer':'dsp',
    'control':'ctl',
    'quatToEuler':'qte',
    'unitConversion':'ucn',
    'mesh':'geo',
    'polygon':'geo'
}

    
def nodeName(nodeType, description, side=None, ignoreSuffix=False):
    suffix = nodeType
    if nodeType in NODENAMEDICT:
        suffix = NODENAMEDICT[nodeType]
    if ignoreSuffix:
        name = description
    else:
        name = '{0}_{1}'.format(description, suffix)
    if side:
        name = '{0}_{1}'.format(side, name)
    return name


def addModifier(node, nodeType, addSuffix=None):
    """    
    
    nodeName = 'loc_spineHips'
    
    oicName = util.names.addModifier(nodeName, 'orientConstraint')
    # Result: 'oic_spineHipsLoc' # 
    oicName = util.names.addModifier(nodeName, 'orientConstraint', addSuffix='Special')
    # Result: 'oic_spineHipsSpecial' # 
    
    nodeName = 'loc_spineHips_center'
    
    oicName = util.names.addModifier(nodeName, 'orientConstraint')
    # Result: 'oic_spineHipsLoc_center' # 
    oicName = util.names.addModifier(nodeName, 'orientConstraint', addSuffix='Special')
    # Result: 'oic_spineHipsSpecial_center' # 
    """
    descriptor = getDescriptor(node)
    suffix = getSuffix(node)
    side = getSide(node)
    if len(suffix):
        if addSuffix:
            descriptor = '{0}{1}{2}{3}{4}'.format(descriptor, suffix[0].upper(), suffix[1:], addSuffix[0].upper(), addSuffix[1:])
        else:
            descriptor = '{0}{1}{2}'.format(descriptor, suffix[0].upper(), suffix[1:])
    elif addSuffix:
        descriptor = '{0}{1}{2}'.format(descriptor, addSuffix[0].upper(), addSuffix[1:])
    retName = '{0}{1}'.format(getNS(node), nodeName(nodeType, descriptor, side=side)) 
    return retName


def getNS(name):
    nsSplit = name.split(':')
    nsPrefix = ''
    for x in xrange(0, len(nsSplit) - 1):
        nsPrefix = '{0}{1}:'.format(nsPrefix, nsSplit[x])
    return nsPrefix 
    
    
def getSuffix(name):
    nsSplit = name.split(':')
    nameMinusNS = nsSplit[-1]
    splitList = nameMinusNS.split('_')
    suffix = None
    if len(splitList) > 1:
        suffix = splitList[-1]
    else:
        suffix = ""
    return suffix


def getSide(name):
    nameMinusNS = name.split(':')[-1]
    splitList = nameMinusNS.split('_')
    if len(splitList) > 2:
        side = splitList[0]
    else:
        side = ''
    return side


def getDescriptor(name):
    nsSplit = name.split(':')
    nameMinusNS = nsSplit[-1]
    splitList = nameMinusNS.split('_')
    if len(splitList) == 2:
        descriptor = splitList[0]
    elif len(splitList) > 2:
        descriptor = splitList[1]
    else:
        descriptor = nameMinusNS
    return descriptor

