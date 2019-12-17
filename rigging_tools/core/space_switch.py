"""
Tool for helping place animation controls into worldspace
"""
import traceback
import sys
import copy

from maya import cmds, mel

from ooutdmaya.animation import constrain
reload(constrain)

MESSAGEATTR = 'ConstraintLocators'

def keyframeInfo(keyframe):
    connections = cmds.listConnections(keyframe, plugs=1, s=0, d=1)
    for con in connections:
        if cmds.objectType(con.split('.')[0]) == 'nodeGraphEditorInfo':
            continue
        attr = con.split('.')[1]
        if cmds.objectType(con.split('.')[0]) == 'pairBlend':
            connections = cmds.listConnections(con, plugs=1, s=1, d=0, connections=1)
            for each in ['x', 'y', 'z']:
                if ('otate'+each.upper()) in con.split('.')[1]:
                    attr = 'rotate'+each.upper()
                if ('ranslate'+each.upper()) in con.split('.')[1]:
                    attr = 'translate'+each.upper()
                if ('cale'+each.upper()) in con.split('.')[1]:
                    attr = 'scale'+each.upper()
    ret = {}     
    ret['attr'] = attr
    ret['tList'] = cmds.keyframe(keyframe, query=1, timeChange=1)
    ret['vList'] = cmds.keyframe(keyframe, query=1, valueChange=1)
    ret['bdList'] = []
  
    # store breakdown info
    for index in range(0, len(ret['tList'])):
        breakdown = cmds.keyframe(keyframe,
            query=1,
            index=(index,index),
            breakdown=1)
        ret['bdList'].append(breakdown)

    return ret

def constrainSelected(copyBreakdowns=True, frameRange=False, nodeList=None,
        info=True, skipUD=True, keyLocOnEveryFrame=True, bakeGrp='ConstraintLocators_grp', smartKey=True):
    """
    """
    print 'info = {0}'.format(info)
    print 'keyLocOnEveryFrame = {0}'.format(keyLocOnEveryFrame)
    print 'frameRange = {0}'.format(frameRange)

    locDescriptor = 'Constraint'
    locSuffix = '_loc'
    cmds.refresh(suspend=True)
    locList = []
    currTime = cmds.currentTime(q=True)
    if frameRange:
        timeMin = cmds.playbackOptions(q=1, min=1)
        timeMax = cmds.playbackOptions(q=1, max=1)
        if info:
            print('timeMin = '+str(timeMin))
            print('timeMax = '+str(timeMax))
    nodeList = nodeList or cmds.ls(sl=True)
    try:
        cmds.undoInfo(openChunk=True)
        if info: print('nodeList = '+str(nodeList))

        if not len(nodeList):
            raise Exception()

        if not cmds.objExists(bakeGrp):
            cmds.createNode('transform', n=bakeGrp)

        keyFrameInfo = {}
        for (i, each) in enumerate(nodeList):
            print each, '(', i+1, '/', len(nodeList), ')'
            keyFrameInfo[each] = {}

            # Query keyframe info
            udList = cmds.listAttr(each, ud=1)
            if info: print('udList = '+str(udList))
            keyframes = cmds.keyframe(each, query=True, name=True)
            keyFrameInfo[each]['keyframes'] = keyframes
            if keyframes:
                timeList = sorted(list(set(cmds.keyframe(keyframes, query=True, timeChange=True))))
            else:
                timeList = [cmds.currentTime(q=1)]
            keyFrameInfo[each]['timeList'] = timeList
            keyFrameInfo[each]['udList'] = udList
            if info: print('timeList = '+str(timeList))

            locName = '{}{}{}'.format(each, locDescriptor, locSuffix)
            if cmds.objExists(locName):
                foo=0
                if info: print('locName "'+str(locName)+'" already exists...')
                while cmds.objExists(locName):
                    foo += 1
                    locName = '{}{}{}{}'.format(each, locDescriptor, foo, locSuffix)
                if info: print('new locName = "'+str(locName)+'" ')
            conLoc = cmds.spaceLocator(n=locName)[0]
            keyFrameInfo[each]['conLoc'] = conLoc
            if info: print('Created Constraint Locator "'+str(conLoc)+'"')
            cmds.addAttr(conLoc, at= 'message', ln= MESSAGEATTR)
            cmds.connectAttr('{0}.message'.format(each), '{0}.{1}'.format(conLoc, MESSAGEATTR))
            locList.append(conLoc)
            cmds.parent(conLoc, bakeGrp)

        # Gather the earliest start frame
        frameList = []
        for each in keyFrameInfo:
            timeList = keyFrameInfo[each]['timeList']
            if keyLocOnEveryFrame:
                if info: print('keyLocOnEveryFrame')
                keyLocEveryFrameMin = timeMin if frameRange else timeList[0]
                if info: print('keyLocEveryFrameMin = {0}'.format(keyLocEveryFrameMin))
                keyLocEveryFrameMax = timeMax if frameRange else timeList[-1]
                if info: print('keyLocEveryFrameMax = {0}'.format(keyLocEveryFrameMax))
                timeList = range(int(keyLocEveryFrameMin), int(keyLocEveryFrameMax+1))
                if info: print '"{0}" timeList = {1}'.format(each, timeList)
                keyFrameInfo[each]['timeList'] = timeList
            frameList = frameList + timeList
        frameList = sorted(set(frameList))
        if info: print 'frameList = {0}'.format(frameList)
        if info: print 'keyFrameInfo = {0}'.format(keyFrameInfo)

        if frameRange:
            frameListCopy = copy.copy(frameList)
            frameList = []
            for frame in frameListCopy:
                if frame < timeMin:
                    continue
                if frame > timeMax:
                    break
                frameList.append(frame)

        # Iterate through each frame
        pacList = []
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
        cmds.progressBar(gMainProgressBar,
                        edit=True,
                        beginProgress=True,
                        isInterruptable=True,
                        status='querying frames...',
                        maxValue=len(frameList) )
        progressBarCancelled = False
        for frame in frameList:
            if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
                progressBarCancelled = True
                break
            cmds.progressBar(gMainProgressBar, edit=True, step=1, status='frame {0}'.format(frame))

            cmds.currentTime(frame)

            if info: print '\n========================'
            if info: print 'frame: {0}'.format(frame)
            for each in keyFrameInfo:
                if info: print '{}'.format(each)

                # check if the current frame is in each timelist
                if not frame in keyFrameInfo[each]['timeList']:
                    # continue on if it's not
                    continue

                conLoc = keyFrameInfo[each]['conLoc']
                keyframes = keyFrameInfo[each]['keyframes']
                # check if we've already connected the locator for baking
                if not 'startFrame' in keyFrameInfo[each]:
                    if info: print '"startFrame" not in  keyFrameInfo["{0}"], defining...'.format(each)
                    # store the start frame if we haven't
                    keyFrameInfo[each]['startFrame'] = frame
                    # Setup constraint to constraint locator
                    # with an initial keyframe, so that when
                    # the constraint is made we get a pairblend
                    cmds.delete(cmds.parentConstraint(each, conLoc))
                    cmds.setKeyframe(conLoc)
                    pacList.append(cmds.parentConstraint(each, conLoc)[0])
                    # Query additional information for breakdowns settings
                    if copyBreakdowns:
                        if info: print('copyBreakdowns = '+str(copyBreakdowns))
                        roVal = cmds.getAttr('{0}.ro'.format(each))
                        cmds.setAttr('{0}.ro'.format(conLoc), roVal)
                        # query associated attributes
                        keyFrameInfo[each]['keyable'] = {}
                        for keyframe in keyframes:
                            connections = cmds.listConnections(keyframe, plugs=1, s=0, d=1)
                            xAttr = connections[0].split('.')[1]
                            if udList:
                                if skipUD and xAttr in keyFrameInfo[each]['udList']:
                                    if info: print 'xAttr "{0}" in udList, skipping...'.format(xAttr)
                                    continue
                            keyFrameInfo[each]['keyable'][keyframe] = {}
                            keyFrameInfo[each]['keyable'][keyframe]['attr'] = xAttr
                            if info: print('keyFrameInfo["{0}"]["{1}"][\'attr\'] = {2}'.format(each, keyframe, keyFrameInfo[each]['keyable'][keyframe]['attr']))
                            keyFrameInfo[each]['keyable'][keyframe]['tList'] = cmds.keyframe(keyframe, query=1, timeChange=1)
                            keyFrameInfo[each]['keyable'][keyframe]['vList'] = cmds.keyframe(keyframe, query=1, valueChange=1)
                # set keys
                if keyLocOnEveryFrame:
                    if info: print 'keyLocOnEveryFrame'
                    cmds.setKeyframe(conLoc)
                elif copyBreakdowns:
                    if info: print 'copyBreakdowns'
                    for keyframe in keyFrameInfo[each]['keyable']:
                        if info: print 'keyframe = "{0}"'.format(keyframe)
                        '''
                        if not keyframe in keyFrameInfo[each]['keyable']:
                            if info: print 'not "{0}" in {1}'.format(keyframe, keyFrameInfo[each]['keyable'])
                            continue
                        '''
                        if not frame in keyFrameInfo[each]['keyable'][keyframe]['tList']:
                            if info: print('not "{}" in {}'.format(frame, keyFrameInfo[each]['keyable'][keyframe]['tList']))
                            if smartKey:
                                cmds.setKeyframe(conLoc, attribute=keyFrameInfo[each]['keyable'][keyframe]['attr'])
                            continue
                        index = keyFrameInfo[each]['keyable'][keyframe]['tList'].index(frame)
                        breakdown = cmds.keyframe(keyframe,
                            query=1,
                            index=(index,index),
                            breakdown=1)
                        bd = True if breakdown else False
                        cmds.setKeyframe(conLoc, attribute=keyFrameInfo[each]['keyable'][keyframe]['attr'], breakdown=bd)
                        if info: print('setKeyframe("{}")'.format(conLoc))
                else:
                    if info: print 'not keyLocOnEveryFrame or copyBreakdowns'
                    cmds.setKeyframe(conLoc)

        # clean up
        cmds.delete(pacList)

        # Now attach destination nodes to constraint locators
        if not progressBarCancelled:
            for each in keyFrameInfo:
                conLoc = keyFrameInfo[each]['conLoc']
                constrainMulti = False
                try:
                    cmds.orientConstraint(conLoc, each)
                    constrainMulti = True
                    print 'could orient constrain'
                except:
                    pass
                try:
                    cmds.pointConstraint(conLoc, each)
                    constrainMulti = True
                    print 'could point constrain'
                except:
                    pass
                if not constrainMulti:
                    channels = ['x', 'y', 'z']
                    for channel in channels:
                        channelList = copy.copy(channels)
                        channelList.pop(channelList.index(channel))
                        try:
                            cmds.orientConstraint(conLoc, each, skip=channelList)
                            print 'could orient constrain ', channel
                        except:
                            pass
                        try:
                            cmds.pointConstraint(conLoc, each, skip=channelList)
                            print 'could point constrain ', channel
                        except:
                            pass
        else:
            cmds.warning('constrain selected cancelled, skipping constraining to locators...')
    except Exception as E:
        traceback.print_exc(file=sys.stderr)
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        cmds.refresh(suspend=False)
        cmds.undoInfo(closeChunk=True)
        
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    cmds.refresh(suspend=False)
    cmds.currentTime(currTime)
    cmds.select(nodeList)
    cmds.undoInfo(closeChunk=True)
    
    
def getConstrained(nodeList=None, messageAttr=MESSAGEATTR):
    if not nodeList:
        nodeList = cmds.ls('*.{0}'.format(MESSAGEATTR), r=1)
        nodeList = [each.split('.')[0] for each in nodeList]
    drivenList = []
    for (i, each) in enumerate(nodeList):
        # Query drive based on message attribute
        con = cmds.listConnections('{0}.{1}'.format(each, MESSAGEATTR), s=True, d=False)
        if not con: continue
        drivenList.append(con[0])
    return drivenList


def getLocator(nodeList=None, messageAttr=MESSAGEATTR):
    if not nodeList:
        nodeList = cmds.ls('*.{0}'.format(MESSAGEATTR), r=1)
        nodeList = [each.split('.')[0] for each in nodeList]
        return nodeList
    drivenList = []
    for (i, each) in enumerate(nodeList):
        # Query drive based on message attribute
        con = cmds.listConnections('{0}.message'.format(each), s=False, d=True, plugs=True)
        if not con: continue
        for each in con:
            if MESSAGEATTR in each:
                drivenList.append(each.split('.')[0])
    return drivenList
    
def _constrainFromDict(drivenDict):
    conList = []
    for source in drivenDict:
        dest = drivenDict[source]
        conList = conList + constrain.parentConstraint(mo=False, selection=[source, dest], info=False)['con']
    return conList
    
    
def reconstrainCtlsFromSelectedLocs(nodeList):
    drivenDict = {}
    for (i, each) in enumerate(nodeList):
        # Query drive based on message attribute
        plug = '{0}.{1}'.format(each, MESSAGEATTR)
        if not cmds.objExists(plug):
            continue
        con = cmds.listConnections(plug, s=True, d=False)
        if not con: continue
        drivenDict[each] = con[0]
    return _constrainFromDict(drivenDict)
    
    
def reconstrainFromSelectedCtls(nodeList):
    drivenDict = {}
    for (i, each) in enumerate(nodeList):
        # Query drive based on message attribute
        plug = '{0}.message'.format(each)
        if not cmds.objExists(plug):
            continue
        con = cmds.listConnections(plug, s=False, d=True, plugs=1)
        if not con: continue
        for foo in con:
            split = foo.split('.')
            if split[1] != MESSAGEATTR:
                continue
            drivenDict[split[0]] = each
    return _constrainFromDict(drivenDict)
    
def bakeResult(frameRange=False, selected=False, info=False,
        skipUD=True, everyFrame=False, bakeAsBreakdowns=False, deleteLocators=False,
        bakeGrp='ConstraintLocators_grp', smartKey=True):
    currTime = cmds.currentTime(q=True)
    sel = cmds.ls(sl=True)
    print('baking results')
    timeMin = cmds.playbackOptions(q=1, min=1)
    timeMax = cmds.playbackOptions(q=1, max=1)
    if frameRange:
        print('using timeslider frame range (from '+str(timeMin)+' to '+str(timeMax)+')')
    cmds.refresh(suspend=True)
    try:
        cmds.undoInfo(openChunk=True)
        if selected:
            children = sel
        else:
            children = getConstrained(bakeGrp)
        keyFrameInfo = {}
        for (i, each) in enumerate(children):
            print each, '(', i+1, '/', len(children), ')'
            keyFrameInfo[each] = {}
            # Query Keyframes
            udList = cmds.listAttr(each, ud=1)
            keyframes = cmds.keyframe(each, query=True, name=True)
            keyFrameInfo[each]['keyframes'] = keyframes
            timeList = sorted(list(set(cmds.keyframe(each, query=True, timeChange=True))))
            keyFrameInfo[each]['timeList'] = timeList
            if info: print('keyframes = {}'.format(keyframes))
            # cmds.currentTime(timeList[0])
             # query associated attributes
            keyFrameInfo[each]['keyable'] = {}
            for keyframe in keyframes:
                connections = cmds.listConnections(keyframe, plugs=1, s=0, d=1)
                xAttr = connections[0].split('.')[1]
                if skipUD and xAttr in udList:
                    continue
                if info: print('keyframe = {}'.format(keyframe))
                keyFrameInfo[each]['keyable'][keyframe] = keyframeInfo(keyframe)

        # Gather the earliest start frame
        frameList = []
        for each in keyFrameInfo:
            timeList = keyFrameInfo[each]['timeList']
            if everyFrame:
                if info: print('everyFrame')
                everyFrameMin = timeMin if frameRange else timeList[0]
                if info: print('everyFrameMin = {0}'.format(everyFrameMin))
                everyFrameMax = timeMax if frameRange else timeList[-1]
                if info: print('everyFrameMax = {0}'.format(everyFrameMax))
                timeList = range(int(everyFrameMin), int(everyFrameMax+1))
                if info: print '"{0}" timeList = {1}'.format(each, timeList)
                keyFrameInfo[each]['timeList'] = timeList
            frameList = frameList + timeList
        frameList = sorted(set(frameList))

        if info: print 'frameList = {0}'.format(frameList)
        if info: print 'keyFrameInfo = {0}'.format(keyFrameInfo)
        
        if frameRange:
            frameListCopy = copy.copy(frameList)
            frameList = []
            for frame in frameListCopy:
                if frame < timeMin:
                    continue
                if frame > timeMax:
                    break
                frameList.append(frame)

        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

        cmds.progressBar(gMainProgressBar,
                        edit=True,
                        beginProgress=True,
                        isInterruptable=True,
                        status='baking frames...',
                        maxValue=len(frameList) )
        progressBarCancelled = False
        for frame in frameList:
            if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
                progressBarCancelled = True
                break
            cmds.progressBar(gMainProgressBar, edit=True, step=1, status='frame {0}'.format(frame))
            if info: print '\n========================'
            cmds.currentTime(frame)
            if info: print 'cmds.currentTime({})'.format(frame)
            for each in keyFrameInfo:
                if info: print '\neach = "{}"'.format(each)

                # check if the current frame is in each timelist
                if not frame in keyFrameInfo[each]['timeList']:
                    # continue on if it's not
                    continue

                keyframes = keyFrameInfo[each]['keyframes']
                keyable = keyFrameInfo[each]['keyable']

                for keyframe in keyframes:
                    if not keyframe in keyFrameInfo[each]['keyable']:
                        continue
                    if not frame in keyFrameInfo[each]['keyable'][keyframe]['tList']:
                        if smartKey:
                            if info: print("smartKey on... cmds.setKeyframe(\""+each+"\", attribute=\""+keyFrameInfo[each]['keyable'][keyframe]['attr']+"\", breakdown="+str(bd)+")")
                            attrVal = cmds.getAttr(each+'.'+keyFrameInfo[each]['keyable'][keyframe]['attr'])
                            cmds.setKeyframe(each, attribute=keyFrameInfo[each]['keyable'][keyframe]['attr'], value=attrVal)
                        continue
                    index = keyFrameInfo[each]['keyable'][keyframe]['tList'].index(frame)
                    breakdown = cmds.keyframe(keyframe,
                        query=1,
                        index=(index,index),
                        breakdown=1)
                    bd = True if breakdown else False
                    if info: print("cmds.setKeyframe(\""+each+"\", attribute=\""+keyFrameInfo[each]['keyable'][keyframe]['attr']+"\", breakdown="+str(bd)+")")
                    attrVal = cmds.getAttr(each+'.'+keyFrameInfo[each]['keyable'][keyframe]['attr'])
                    # if info: print("cmds.getAttr(\""+each+"."+keyFrameInfo[each]['keyable'][keyframe]['attr']+"\" = "+str(attrVal)+")")
                    cmds.setKeyframe(each, attribute=keyFrameInfo[each]['keyable'][keyframe]['attr'], breakdown=bd, value=attrVal)
        if not progressBarCancelled:
            if deleteLocators:
                for each in keyFrameInfo:
                    driverConnections = cmds.listConnections('{0}.message'.format(each), d=True, s=False, plugs=1, type='transform')
                    driverLoc = None
                    for each in driverConnections:
                        if MESSAGEATTR in each:
                            driverLoc = each
                    if driverLoc:
                        plugNode = driverLoc.split('.')[0]
                        if info: print("deleting (\""+plugNode+"\"...")
                        cmds.delete(plugNode)
        else:
            cmds.warning('bake selected cancelled...')
    except Exception as E:
        traceback.print_exc(file=sys.stderr)
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        cmds.refresh(suspend=False)
        cmds.currentTime(currTime)
        cmds.select(sel)
        cmds.undoInfo(closeChunk=True)
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    cmds.refresh(suspend=False)
    cmds.currentTime(currTime)
    cmds.select(cl=True)
    replaceSelect = []
    for each in sel:
        if not cmds.objExists(each): continue
        replaceSelect.append(each)
    if len(replaceSelect): cmds.select(replaceSelect)
    if not selected:
        bakeGrpChildren = cmds.listRelatives(bakeGrp, children=True)
        if not bakeGrpChildren:
            cmds.delete(bakeGrp)
    cmds.undoInfo(closeChunk=True)


def bakeSelected(frameRange=True, info=False, everyFrame=False, bakeAsBreakdowns=False, smartKey=True):
    bakeResult(frameRange=frameRange, selected=True, info=info,
        everyFrame=everyFrame, bakeAsBreakdowns=bakeAsBreakdowns, smartKey=smartKey)

def bakeEveryFrame(nodeList=None, info=False):
    if info: print('baking every frame')
    currTime = cmds.currentTime(q=True)
    sel = cmds.ls(sl=True)
    if not nodeList:
        if info: print('no "nodeList" argument supplied, using selected nodes...')
        nodeList = sel
    timeMin = cmds.playbackOptions(q=1, min=1)
    timeMax = cmds.playbackOptions(q=1, max=1)
    if info: print('using frame range (from '+str(timeMin)+' to '+str(timeMax)+')')
    cmds.refresh(suspend=True)
    keyableAttrMap = {}
    for each in nodeList:
        keyableAttrMap[each] = cmds.listAttr(each, k=1)
    try:
        for frame in range(int(timeMin), int(timeMax)+1):
            for (i, each) in enumerate(nodeList):
                cmds.currentTime(frame)
                for attr in keyableAttrMap[each]:
                    attrVal = cmds.getAttr(each+'.'+attr)
                    # if info: print("cmds.getAttr(\""+driven+"."+keyable[keyframe]['attr']+"\" = "+str(attrVal)+")")
                    cmds.setKeyframe(each, attribute=attr, value=attrVal)
    except:
        cmds.refresh(suspend=False)
        cmds.currentTime(currTime)
        cmds.select(sel)
    cmds.refresh(suspend=False)
    cmds.currentTime(currTime)
    cmds.select(cl=True)
    replaceSelect = []
    for each in sel:
        if not cmds.objExists(each): continue
        replaceSelect.append(each)
    if len(replaceSelect): cmds.select(replaceSelect)

    
def deleteBreakdowns(nodeList, frameRange=False, info=False, skipUD=True):
    timeMin = cmds.playbackOptions(q=1, min=1)
    timeMax = cmds.playbackOptions(q=1, max=1)
    if frameRange:
        print('using timeslider frame range (from '+str(timeMin)+' to '+str(timeMax)+')')
    for (i, driven) in enumerate(nodeList):
        print driven, '(', i+1, '/', len(nodeList), ')'
        # Query Keyframes
        udList = cmds.listAttr(driven, ud=1)
        keyframes = cmds.keyframe(driven, query=True, name=True)
        timeList = sorted(list(set(cmds.keyframe(driven, query=True, timeChange=True))))
        if info: print('keyframes = {}'.format(keyframes))
         # query associated attributes
        keyable = {}
        for keyframe in keyframes:
            connections = cmds.listConnections(keyframe, plugs=1, s=0, d=1)
            xAttr = connections[0].split('.')[1]
            if udList:
                if skipUD and xAttr in udList:
                    continue
            if info: print('keyframe = {}'.format(keyframe))
            keyable[keyframe] = keyframeInfo(keyframe)
         # set keys on driven
        for frame in timeList:
            if info: print('frame = {}'.format(frame))
            if frameRange:
                if frame < timeMin:
                    continue
                if frame > timeMax:
                    break
            if info: print('frame = {}'.format(frame))
            for keyframe in keyframes:
                if not keyframe in keyable:
                    continue
                if not frame in keyable[keyframe]['tList']:
                    continue
                index = keyable[keyframe]['tList'].index(frame)
                breakdown = True if keyable[keyframe]['bdList'][index] else False
                if not breakdown:
                    continue
                cmds.cutKey(driven, time=(frame,frame), attribute=keyable[keyframe]['attr'], option="keys" )


def bakePair(sourceList=None, destList=None):
    """
    select driver first, then driven
    """
    sl1 = cmds.ls(sl=1)
    if not sourceList or not destList:
        sourceList = [sl1[0]]
        destList = [sl1[1]]

    currTime = cmds.currentTime(q=1)
    try:
        cmds.refresh(suspend=1)
        rangeMin = cmds.playbackOptions(q=1, min=1)
        rangeMax= cmds.playbackOptions(q=1, max=1)
        conList = []
        for i in range(0, len(sourceList)):
            conList = conList + constrain.parentConstraint(mo=False, selection=[sourceList[i], destList[i]])['con']
        # pac = cmds.parentConstraint()
        # cmds.select(destList)
        cmds.bakeResults(destList, simulation=1, t=(rangeMin, rangeMax))
        cmds.delete(conList)
    except:
        cmds.currentTime(currTime)
        cmds.select(sl1)
        cmds.refresh(suspend=0)
    cmds.currentTime(currTime)
    cmds.select(sl1)
    cmds.refresh(suspend=0)
