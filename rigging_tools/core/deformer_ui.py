'''
Created on 1 Oct 2018

@author: lasse-r
'''
import maya.cmds as cmds

from ooutdmaya.rigging.core.util.IO import deformerData
from ooutdmaya.rigging.core.util import easy

import os.path


def export(exportPath, deformerList, force=False):
    '''
    '''
    # Check export path
    if not os.path.isdir(exportPath):
        
        # Create directories if they dont exist
        os.makedirs(exportPath)
    
    # Export Deformers
    for deformer in deformerList:
        
        # Check deformer
        if not easy.isDeformer(deformer):
            print('Object {0} is not a valid deformer! Skipping...'.format(deformer))
            continue
        
        # Initialize Deformer Data
        defData = deformerData.DeformerData(deformer)
        
        # Build export file path
        deformerDataPath = ("{0}/{1}.pkl".format(exportPath, deformer))
        
        # Check file exists
        if os.path.isfile(deformerDataPath) and not force:
            print('File path {0} exists! Use force=True to overwrite.'.format(deformerDataPath))
            continue
        
        # Export Deformer Data
        print('Exporting deformer data for {0} to - {1}'.format(deformer, deformerDataPath))
        defData.save(deformerDataPath)
    
    # Return Result
    print('Exporting deformers complete!')
    return 1


def importData(importPath):
    '''
    '''
    # Check import path
    if not os.path.isfile(importPath):
        raise Exception('Path {0} does not exist!'.format(importPath))
    
    # Import Deformer Data
    defData = deformerData.DeformerData().load(importPath)
    defData.rebuild()
    

def exportUI():
    '''
    '''
    # Window
    window = 'exportDeformerDataUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, t='Export Deformer Data', s=True)
    
    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)
    
    # UI Elements
    pathTBG = cmds.textFieldButtonGrp('exportDeformer_pathTBG', label='Export Path', buttonLabel='...', h=30)
    deformerTSL = cmds.textScrollList('exportDeformer_deformerTSL', allowMultiSelection=True)
    exportB = cmds.button('exportDeformer_exportB', label='Export', c='deformerUI.exportFromUI()')
    closeB = cmds.button('exportDeformer_closeB', label='Close', c='cmds.deleteUI("' + window + '")')
    
    # Populate deformer list
    deformerList = cmds.ls(type='weightGeometryFilter')
    deformerList.sort()
    for deformer in deformerList:
        cmds.textScrollList(deformerTSL, e=True, a=deformer)
    
    # UI Callbacks
    cmds.textFieldButtonGrp(pathTBG, e=True, bc='easy.exportFolderBrowser("' + pathTBG + '")')
    
    # Form LAYOUT
    cmds.formLayout(FL, e=True, af=[(pathTBG, 'top', 5), (pathTBG, 'left', 5), (pathTBG, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(closeB, 'bottom', 5), (closeB, 'left', 5), (closeB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(exportB, 'left', 5), (exportB, 'right', 5)], ac=[(exportB, 'bottom', 5, closeB)])
    cmds.formLayout(FL, e=True, af=[(deformerTSL, 'left', 5), (deformerTSL, 'right', 5)], ac=[(deformerTSL, 'top', 5, pathTBG), (deformerTSL, 'bottom', 5, exportB)])
    
    # Show Window
    cmds.window(window, e=True, w=450, h=262)
    cmds.showWindow(window)


def exportFromUI():
    '''
    '''
    # Get export path
    exportPath = cmds.textFieldButtonGrp('exportDeformer_pathTBG', q=True, text=True)
    deformerList = cmds.textScrollList('exportDeformer_deformerTSL', q=True, si=True)
    
    # Export Deformer Data
    export(exportPath, deformerList, force=True)


def importUI():
    '''
    '''
    # Window
    window = 'importDeformerDataUI'
    if cmds.window(window, q=True, ex=True): cmds.deleteUI(window)
    window = cmds.window(window, t='Import Deformer Data', s=True)
    
    # Layout
    FL = cmds.formLayout(numberOfDivisions=100)
    
    # UI Elements
    pathTBG = cmds.textFieldButtonGrp('importDeformer_pathTBG', label='Import Path', buttonLabel='...', h=30)
    populateB = cmds.button('importDeformer_populate', label='Populate', c='deformerUI.updateImportList()')
    deformerTSL = cmds.textScrollList('importDeformer_deformerTSL', allowMultiSelection=True)
    exportB = cmds.button('importDeformer_exportB', label='Import', c='deformerUI.importFromUI()')
    closeB = cmds.button('importDeformer_closeB', label='Close', c='cmds.deleteUI("' + window + '")')
    
    # UI Callbacks
    cmds.textFieldButtonGrp(pathTBG, e=True, bc='easy.exportFolderBrowser("' + pathTBG + '")')
    cmds.textFieldButtonGrp(pathTBG, e=True, cc='deformerUI.updateImportList()')
    
    # Form LAYOUT
    cmds.formLayout(FL, e=True, af=[(pathTBG, 'top', 5), (pathTBG, 'left', 5), (pathTBG, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(populateB, 'top', 35), (populateB, 'left', 5), (populateB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(closeB, 'bottom', 5), (closeB, 'left', 5), (closeB, 'right', 5)])
    cmds.formLayout(FL, e=True, af=[(exportB, 'left', 5), (exportB, 'right', 5)], ac=[(exportB, 'bottom', 5, closeB)])
    cmds.formLayout(FL, e=True, af=[(deformerTSL, 'left', 5), (deformerTSL, 'right', 5)], ac=[(deformerTSL, 'top', 35, pathTBG), (deformerTSL, 'bottom', 5, exportB)])
    
    # Show Window
    cmds.window(window, e=True, w=450, h=262)
    cmds.showWindow(window)


def importFromUI():
    '''
    '''
    # Get import path
    importPath = cmds.textFieldButtonGrp('importDeformer_pathTBG', q=True, text=True)
    deformerList = cmds.textScrollList('importDeformer_deformerTSL', q=True, si=True)
    
    # Import Deformer Data
    for deformer in deformerList: importData("{0}/{1}.pkl".format(importPath, deformer))


def updateImportList():
    '''
    '''
    # Get import path
    importPath = cmds.textFieldButtonGrp('importDeformer_pathTBG', q=True, text=True)
    deformerList = [i.split('.')[0] for i in os.listdir(importPath) if i.endswith('.pkl')]
    
    # Clear deformer list
    cmds.textScrollList('importDeformer_deformerTSL', e=True, ra=True)
    
    # Populate deformer list
    for deformer in deformerList:
        cmds.textScrollList('importDeformer_deformerTSL', e=True, a=deformer)
        
