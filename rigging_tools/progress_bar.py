'''
Created on 28 Sep 2018

@author: lasse-r
'''
import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMaya as om

class UserInterupted(Exception): pass

def init(status,maxValue):
    '''
    Initialize Progress Bar
    '''
    # Check Interactive Session
    if om.MGlobal.mayaState(): return

    # Initialize Progress Bar
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar(gMainProgressBar,
                     e=True,
                     bp=True,
                     ii=True,
                     status=status,
                     maxValue=maxValue)

def update(step=0, status='', enableUserInterupt=False):
    '''
    Update Progress
    '''
    # Check Interactive Session
    if om.MGlobal.mayaState(): return

    # Update Progress Bar
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    # Check User Interuption
    if enableUserInterupt:
        if cmds.progressBar(gMainProgressBar, q=True, isCancelled=True):
            cmds.progressBar(gMainProgressBar, e=True, endProgress=True)
            raise UserInterupted('Operation cancelled by user!')

    # Update Status
    if status: cmds.progressBar( gMainProgressBar,e=True,status=status)

    # Step Progress
    if step: cmds.progressBar(gMainProgressBar,e=True,step=step)

def end():
    '''
    End Progress
    '''
    # Check Interactive Session
    if om.MGlobal.mayaState(): return

    # Update Progress Bar
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    # End Progress
    cmds.progressBar(gMainProgressBar, e=True, endProgress=True)
