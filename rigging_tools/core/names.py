"""
generic lib for namning convention standards related to secret garden
"""
from maya import cmds
from ooutdmaya.common.util import names
reload(names)
    
NODENAMEDICT = names.NODENAMEDICT

    
def nodeName(*args, **kwargs):
    # cmds.warning('ooutdmaya.rigging.core.util.names.nodeName now DEPRECIATED... please use\n\tooutdmaya.common.util.names.nodeName instead')
    return names.nodeName(*args, **kwargs)

def addModifier(*args, **kwargs):
    # cmds.warning('ooutdmaya.rigging.core.util.names.addModifier now DEPRECIATED... please use\n\tooutdmaya.common.util.names.addModifier instead')
    return names.addModifier(*args, **kwargs)

def getNS(*args, **kwargs):
    # cmds.warning('ooutdmaya.rigging.core.util.names.getNS now DEPRECIATED... please use\n\tooutdmaya.common.util.names.getNS instead')
    return names.getNS(*args, **kwargs)

def getSuffix(*args, **kwargs):
    # cmds.warning('ooutdmaya.rigging.core.util.names.getSuffix now DEPRECIATED... please use\n\tooutdmaya.common.util.names.getSuffix instead')
    return names.getSuffix(*args, **kwargs)

def getSide(*args, **kwargs):
    # cmds.warning('ooutdmaya.rigging.core.util.names.getSide now DEPRECIATED... please use\n\tooutdmaya.common.util.names.getSide instead')
    return names.getSide(*args, **kwargs)

def getDescriptor(*args, **kwargs):
    # cmds.warning('ooutdmaya.rigging.core.util.names.getDescriptor now DEPRECIATED... please use\n\tooutdmaya.common.util.names.getDescriptor instead')
    return names.getDescriptor(*args, **kwargs)
