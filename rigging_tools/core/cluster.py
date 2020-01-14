from maya import cmds, mel

def createMaskClusters(maskGeo, prefix, padding=5, skipList=None):
    """
    """
    vtxCount = cmds.polyEvaluate(maskGeo, vertex=1)
    csrList = []
    for i in xrange(0, vtxCount):
        vtxAttrPath = maskGeo+'.vtx['+str(i)+']'
        if skipList:
            if str(vtxAttrPath) in [str(each) for each in skipList]:
                continue
        cmds.select(cl=1)
        csr = cmds.cluster(vtxAttrPath)
        index = str(i+1).zfill(padding)
        csrName = prefix+index+'_CSR'
        cmds.rename(csr[0], csrName)
        csrHandle = prefix+index+'Csr_GRP'
        cmds.rename(csr[1], csrHandle)
        csrList.append(csrHandle)
    return csrList
    

def createControlPerCluster(csrList, scale=1, local=True, color=17, suffix='CTRL'):
    """
    """
    ctlData = {}
    ctlData['control'] = []
    ctlData['setupGroup'] = []
    ctlData['controlGroup'] = []
    for csr in csrList:
        # create the control
        prefix = csr.replace('Csr_GRP', '')
        ctlInfo = createControl(prefix, match=csr, suffix=suffix)
        ctl = ctlInfo['control']
        # lock and hide
        for each in ctl:
            for multi in ['s', 'r']:
                for single in ['x', 'y', 'z']:
                    cmds.setAttr('{0}.{1}{2}'.format(each, multi, single), l=1, k=0)
            cmds.setAttr('{0}.v'.format(each, multi, single), l=1, k=0)
        ctlGrp = ctlInfo['group']
        cmds.setAttr('{0}.scale'.format(ctlGrp[0]), scale, scale, scale)
        # store info
        ctlData['control'].extend(ctl)
        ctlData['controlGroup'].extend(ctlGrp)
        
        # Connect the cluster to the contorl
        # create a local transformation group to connect the cluster to the control
        if local:
            localGrpName = '{0}Local_GRP'.format(prefix)
            localGrp = cmds.createNode('transform', n=localGrpName)
            localLocName = '{0}Local_LOC'.format(prefix)
            localLoc = cmds.spaceLocator(n=localLocName)[0]
            cmds.parent(localLoc, localGrp)
            for attr in ['x', 'y', 'z']:
                '''
                cmds.connectAttr(
                    '{0}.translate{1}'.format(ctlGrp[-1], attr.upper()),
                    '{0}.translate{1}'.format(localGrp, attr.upper()))
                cmds.connectAttr(
                    '{0}.rotate{1}'.format(ctlGrp[-1], attr.upper()),
                    '{0}.rotate{1}'.format(localGrp, attr.upper()))
                cmds.connectAttr(
                    '{0}.scale{1}'.format(ctlGrp[-1], attr.upper()),
                    '{0}.scale{1}'.format(localGrp, attr.upper()))
                '''
                cmds.setAttr(
                    '{0}.translate{1}'.format(localGrp, attr.upper()),
                    cmds.getAttr('{0}.translate{1}'.format(ctlGrp[-1], attr.upper())))
                cmds.setAttr(
                    '{0}.rotate{1}'.format(localGrp, attr.upper()),
                    cmds.getAttr('{0}.rotate{1}'.format(ctlGrp[-1], attr.upper())))
                cmds.setAttr(
                    '{0}.scale{1}'.format(localGrp, attr.upper()),
                    cmds.getAttr('{0}.scale{1}'.format(ctlGrp[-1], attr.upper())))
                
                cmds.connectAttr(
                    '{0}.translate{1}'.format(ctl[-1], attr.upper()),
                    '{0}.translate{1}'.format(localLoc, attr.upper()))
                cmds.connectAttr(
                    '{0}.rotate{1}'.format(ctl[-1], attr.upper()),
                    '{0}.rotate{1}'.format(localLoc, attr.upper()))
            # parent the cluster under the locator
            cmds.parent(csr, localLoc)
            # store info
            ctlData['setupGroup'].append(localGrp)
        else:
            # parent the cluster under the control
            cmds.parent(csr, ctl)
        for each in ctlData['control']:
            cmds.setAttr('{0}.overrideEnabled'.format(each), 1)
            cmds.setAttr('{0}.overrideColor'.format(each), color)

    return ctlData


    
