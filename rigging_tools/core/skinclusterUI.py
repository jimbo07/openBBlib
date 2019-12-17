'''
Created on 28 Sep 2018

@author: lasse-r
'''
import maya.cmds as cmds

from ooutdmaya.rigging.core.util.IO import skinClusterData, data, meshData
from ooutdmaya.rigging.core.util import IO
from ooutdmaya.rigging.core.util import easy

def skinClusterDataUI():
    ''' Creates a UI for handling skinClusters
    Example:
        from ooutdmaya.rigging.core.util.IO import skinClusterUI
        skinClusterUI.skinClusterDataUI()
    '''
    # Window
    win = 'skinClusterDataUI'
    if cmds.window(win,q=True,ex=True): cmds.deleteUI(win)
    win = cmds.window(win,t='SkinClusterData')
    
    # ===============
    # - UI Elements -
    # ===============
    
    cw1=(1,120)
    
    # Form Layout
    mainFL = cmds.formLayout(numberOfDivisions=100)
    
    # Load/Buld Buttons
    loadB = cmds.button(label='Load Data...', c='skinClusterUI.loadData()')
    buildB = cmds.button(label='Build Data (from selected)', c='skinClusterUI.buildData()')
    rebuildB = cmds.button(label='Rebuild SkinCluster', c='skinClusterUI.rebuildSkinCluster()')
    saveB = cmds.button(label='Save Data', c='skinClusterUI.saveData()')
    closeB = cmds.button(label='Close', c='cmds.deleteUI("'+win+'")')
    
    # Scroll Layout
    scrollLayout = cmds.scrollLayout(horizontalScrollBarThickness=16,verticalScrollBarThickness=16,cr=1)
    
    # SkinCluster Name
    skinClusterNameTFG = cmds.textFieldGrp('skinCluster_nameTFG',label='SkinCluster',text='',cw=cw1)
    
    # Scroll FL
    scrollFL = cmds.formLayout(numberOfDivisions=100)
    
    # ==============
    # - Basic Data -
    # ==============
    
    basicDataFRL = cmds.frameLayout(label='SkinCluster Data',collapsable=True,p=scrollFL)
    basicDataFL = cmds.formLayout(numberOfDivisions=100)
    
    # Affected Geometry
    skinClusterGeoTFB = cmds.textFieldButtonGrp('skinCluster_geoTFB',label='Geometry',text='',editable=False,buttonLabel='Remap',cw=cw1)
    skinClusterMethodOMG = cmds.optionMenuGrp('skinCluster_methodOMG',label='Skinning Method',cw=cw1)
    cmds.menuItem('Classic Linear')
    cmds.menuItem('Dual Quaternion')
    cmds.menuItem('Weight Blended')
    skinClusterComponentCBG = cmds.checkBoxGrp('skinCluster_componentCBG',label='Use Components',cw=cw1)
    skinClusterNormalizeOMG = cmds.optionMenuGrp('skinCluster_normalizeOMG',label='Normalize Weights',cw=cw1)
    cmds.menuItem('None')
    cmds.menuItem('Interactive')
    cmds.menuItem('Post')
    skinClusterDeformNormCBG = cmds.checkBoxGrp('skinCluster_deformNormCBG',label='Deform User Normals',cw=cw1)
    
    cmds.formLayout(basicDataFL,e=True,af=[(skinClusterGeoTFB,'top',5),(skinClusterGeoTFB,'left',5),(skinClusterGeoTFB,'right',5)])
    cmds.formLayout(basicDataFL,e=True,ac=[(skinClusterMethodOMG,'top',5,skinClusterGeoTFB)],af=[(skinClusterMethodOMG,'left',5),(skinClusterMethodOMG,'right',5)])
    cmds.formLayout(basicDataFL,e=True,ac=[(skinClusterComponentCBG,'top',5,skinClusterMethodOMG)],af=[(skinClusterComponentCBG,'left',5),(skinClusterComponentCBG,'right',5)])
    cmds.formLayout(basicDataFL,e=True,ac=[(skinClusterNormalizeOMG,'top',5,skinClusterComponentCBG)],af=[(skinClusterNormalizeOMG,'left',5),(skinClusterNormalizeOMG,'right',5)])
    cmds.formLayout(basicDataFL,e=True,ac=[(skinClusterDeformNormCBG,'top',5,skinClusterNormalizeOMG)],af=[(skinClusterDeformNormCBG,'left',5),(skinClusterDeformNormCBG,'right',5)])
    
    # ==================
    # - Influence Data -
    # ==================
    
    influenceDataFRL = cmds.frameLayout(label='Influence Data',collapsable=True,p=scrollFL)
    influenceDataFL = cmds.formLayout(numberOfDivisions=100)
    
    skinCluster_infTXT = cmds.text( label='Influence List' )
    skinCluster_infTSL = cmds.textScrollList('skinCluster_infTSL',numberOfRows=15,allowMultiSelection=True)
    skinCluster_wtTXT = cmds.text( label='Influence Weights' )
    skinCluster_wtTSL = cmds.textScrollList('skinCluster_wtTSL',numberOfRows=15,allowMultiSelection=True)
    
    cmds.formLayout(influenceDataFL,e=True,af=[(skinCluster_infTXT,'top',5),(skinCluster_infTXT,'left',5),(skinCluster_infTXT,'right',5)])
    cmds.formLayout(influenceDataFL,e=True,ac=[(skinCluster_infTSL,'top',5,skinCluster_infTXT)],af=[(skinCluster_infTSL,'left',5),(skinCluster_infTSL,'right',5)])
    cmds.formLayout(influenceDataFL,e=True,ac=[(skinCluster_wtTXT,'top',5,skinCluster_infTSL)],af=[(skinCluster_wtTXT,'left',5),(skinCluster_wtTXT,'right',5)])
    cmds.formLayout(influenceDataFL,e=True,ac=[(skinCluster_wtTSL,'top',5,skinCluster_wtTXT)],af=[(skinCluster_wtTSL,'left',5),(skinCluster_wtTSL,'right',5)])
    
    # ====================
    # - World Space Data -
    # ====================
    
    worldSpaceDataFRL = cmds.frameLayout(label='World Space Data',collapsable=True,p=scrollFL)
    worldSpaceDataFL = cmds.formLayout(numberOfDivisions=100)
    
    buildWorldSpaceMeshB = cmds.button(label='Build World Space Mesh',c='skinClusterUI.buildWorldSpaceMesh()')
    storeWorldSpaceMeshB = cmds.button(label='Store World Space Mesh',c='skinClusterUI.storeWorldSpaceMesh()')
    rebuildWorldSpaceDataB = cmds.button(label='Rebuild World Space Data',c='skinClusterUI.rebuildWorldSpaceData()')
    worldSpaceMeshTFG = cmds.textFieldGrp('skinCluster_wsMeshTFG',label='World Space Mesh',text='',editable=False,cw=cw1)
    
    cmds.formLayout(worldSpaceDataFL,e=True,af=[(buildWorldSpaceMeshB,'top',5),(buildWorldSpaceMeshB,'left',5),(buildWorldSpaceMeshB,'right',5)])
    cmds.formLayout(worldSpaceDataFL,e=True,ac=[(storeWorldSpaceMeshB,'top',5,buildWorldSpaceMeshB)],af=[(storeWorldSpaceMeshB,'left',5),(storeWorldSpaceMeshB,'right',5)])
    cmds.formLayout(worldSpaceDataFL,e=True,ac=[(rebuildWorldSpaceDataB,'top',5,storeWorldSpaceMeshB)],af=[(rebuildWorldSpaceDataB,'left',5),(rebuildWorldSpaceDataB,'right',5)])
    cmds.formLayout(worldSpaceDataFL,e=True,ac=[(worldSpaceMeshTFG,'top',5,rebuildWorldSpaceDataB)],af=[(worldSpaceMeshTFG,'left',5),(worldSpaceMeshTFG,'right',5)])
    
    # ====================
    # - PopUp Menu Items -
    # ====================
    
    # Influence Menu
    cmds.popupMenu(parent=skinCluster_infTSL)
    cmds.menuItem(label='Remap Influence',c='skinClusterUI.remapSelectedInfluence()')
    cmds.menuItem(label='Combine Influences',c='skinClusterUI.combineSelectedInfluences()')
    cmds.menuItem(label='Swap Weights',c='skinClusterUI.swapInfluenceWeights()')
    cmds.menuItem(label='Move Weights',c='skinClusterUI.moveInfluenceWeights()')
    
    cmds.popupMenu(parent=skinCluster_wtTSL)
    
    # ========================
    # - UI Callback Commands -
    # ========================
    
    cmds.textFieldGrp(skinClusterNameTFG,e=True,cc='skinClusterUI.renameSkinCluster()')
    cmds.textFieldButtonGrp(skinClusterGeoTFB,e=True,bc='skinClusterUI.remapGeometry()')
    cmds.optionMenuGrp(skinClusterMethodOMG,e=True,cc='skinClusterUI.updateBasicData()')
    cmds.checkBoxGrp(skinClusterComponentCBG,e=True,cc='skinClusterUI.updateBasicData()')
    cmds.optionMenuGrp(skinClusterNormalizeOMG,e=True,cc='skinClusterUI.updateBasicData()')
    cmds.checkBoxGrp(skinClusterDeformNormCBG,e=True,cc='skinClusterUI.updateBasicData()')
    cmds.textScrollList(skinCluster_infTSL,e=True,sc='skinClusterUI.selectInfluencesFromUI();skinClusterUI.displayWeightList()')
    
    # ================
    # - Form Layouts -
    # ================
    
    cmds.formLayout(mainFL,e=True,af=[(loadB,'top',5),(loadB,'left',5)],ap=[(loadB,'right',5,50)])
    cmds.formLayout(mainFL,e=True,af=[(buildB,'top',5),(buildB,'right',5)],ap=[(buildB,'left',5,50)])
    cmds.formLayout(mainFL,e=True,af=[(saveB,'bottom',5),(saveB,'left',5)],ap=[(saveB,'right',5,50)])
    cmds.formLayout(mainFL,e=True,af=[(closeB,'bottom',5),(closeB,'right',5)],ap=[(closeB,'left',5,50)])
    cmds.formLayout(mainFL,e=True,ac=[(rebuildB,'bottom',5,closeB)],af=[(rebuildB,'right',5),(rebuildB,'left',5)])
    cmds.formLayout(mainFL,e=True,ac=[(scrollLayout,'top',5,loadB),(scrollLayout,'bottom',5,rebuildB)],af=[(scrollLayout,'left',5),(scrollLayout,'right',5)])
    
    cmds.formLayout(scrollFL,e=True,af=[(basicDataFRL,'top',5),(basicDataFRL,'left',5),(basicDataFRL,'right',5)])
    cmds.formLayout(scrollFL,e=True,ac=[(influenceDataFRL,'top',5,basicDataFRL)],af=[(influenceDataFRL,'left',5),(influenceDataFRL,'right',5)])
    cmds.formLayout(scrollFL,e=True,ac=[(worldSpaceDataFRL,'top',5,influenceDataFRL)],af=[(worldSpaceDataFRL,'left',5),(worldSpaceDataFRL,'right',5)])
    
    # ===============
    # - Show Window -
    # ===============
    
    reloadUI()
    cmds.showWindow(win)

def loadData():
    '''
    '''
    # Load SkinCluster Data
    skinData = data.Data().load()
    easy.GlobalSkinClusterData = skinData
    
    # Rebuild UI
    reloadUI()

def buildData():
    '''
    '''
    # Get Selected Objects
    sel = cmds.ls(sl=1)
    if not sel:
        print('Nothing selected! Unable to load skinCluster data...')
        return
    
    # Get SkinCluster of First Selected Geometry
    geo = sel[0]
    # Check Geometry
    shapes = cmds.listRelatives(geo,s=True)
    if not shapes:
        print('Selected object "'+geo+'" has no shape children! Unable to load skinCluster data...')
        return
    
    # Get SkinCluster
    skc = IO.skinCluster.findRelatedSkinCluster(geo)
    if not skc:
        print('Selected geometry "'+geo+'" has no skinCluster! Unable to load skinCluster data...')
        return
    
    # Build Data
    skinData = skinClusterData.SkinClusterData(skc)
    easy.GlobalSkinClusterData = skinData
    
    # Rebuild UI
    reloadUI()

def saveData():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Save GlobalSkinClusterData to File
    skinData.saveAs()

def rebuildSkinCluster():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Rebuild SkinCluster
    skinData.rebuild()

def renameSkinCluster():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Check Window
    win = 'skinClusterDataUI'
    if not cmds.window(win,q=True,ex=True): return
    
    # Get New SkinCluster Name
    skinName = cmds.textFieldGrp('skinCluster_nameTFG',q=True,text=True)
    if not skinName:
        skinName = easy.GlobalSkinClusterData._data['name']
        cmds.textFieldGrp('skinCluster_nameTFG',e=True,text=skinName)
    
    # Update skinClusterData
    easy.GlobalSkinClusterData._data['name'] = skinName
    
    # Refresh UI
    reloadUI()
    
    # Return Result
    return skinName

def remapGeometry():
    '''
    '''
    # Check Window
    win = 'skinClusterDataUI'
    if not cmds.window(win,q=True,ex=True): return
    
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Get User Selections
    geo = ''
    sel = cmds.ls(sl=1,dag=True)
    if not sel:
        result = cmds.promptDialog(title='Remap Geometry',message='Enter Name:',button=['Remap', 'Cancel'],defaultButton='Remap',cancelButton='Cancel',dismissString='Cancel')
        if result == 'Remap':
            geo = cmds.promptDialog(q=True,text=True)
        else:
            print('User cancelled!')
            return
    else:
        geo = sel[0]
    
    # Remap Geometry
    skinData.remapGeometry(geometry=geo)
    
    # Refresh UI
    reloadUI()
    
    # Return Result
    return geo

def updateBasicData():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData:
        print('No SkinClusterData to load...')
        return
    
    # Get Basic Data from UI
    skinMethod = cmds.optionMenuGrp('skinCluster_methodOMG',q=True,sl=True)
    useComponents = cmds.checkBoxGrp('skinCluster_componentCBG',q=True,v1=True)
    normalizeWt = cmds.optionMenuGrp('skinCluster_normalizeOMG',q=True,sl=True)
    deformNormal = cmds.checkBoxGrp('skinCluster_deformNormCBG',q=True,v1=True)
    
    # Update Basic SkinCluster Data
    skinData._data['attrValueDict']['skinningMethod'] = skinMethod-1
    skinData._data['attrValueDict']['useComponents'] = useComponents
    skinData._data['attrValueDict']['normalizeWeights'] = normalizeWt-1
    skinData._data['attrValueDict']['deformUserNormals'] = deformNormal

def remapSelectedInfluence():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return

def swapInfluenceWeights():
    '''
    '''
    # Check Window
    win = 'skinClusterDataUI'
    if not cmds.window(win,q=True,ex=True): return
    
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Get Influence Selection
    influenceSel = cmds.textScrollList('skinCluster_infTSL',q=True,si=True)
    if len(influenceSel) < 2:
        print('Select 2 influences to swap weights between!')
        return
    
    # Swap Influence Weights
    skinData.swapWeights(influenceSel[0],influenceSel[1])

def moveInfluenceWeights():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return

def combineSelectedInfluences():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return

def displayWeightList():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Check Window
    win = 'skinClusterDataUI'
    if not cmds.window(win,q=True,ex=True): return
    
    # Clear Weight List
    cmds.textScrollList('skinCluster_wtTSL',e=True,ra=True)
    
    # Get Influence Selection
    influenceSel = cmds.textScrollList('skinCluster_infTSL',q=True,si=True)
    if not influenceSel: return
    inf = influenceSel[0]
    
    # Check Weights
    if not skinData._influenceData.has_key(inf): return
    wt = skinData._influenceData[inf]['wt']
    
    # Display Weights
    for i in range(len(wt)): cmds.textScrollList('skinCluster_wtTSL',e=True,a='['+str(i)+']: '+str(wt[i]))

def selectInfluencesFromUI():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Check Window
    win = 'skinClusterDataUI'
    if not cmds.window(win,q=True,ex=True): return
    
    # Clear Weight List
    cmds.textScrollList('skinCluster_wtTSL',e=True,ra=True)
    
    # Get Influence Selection
    influenceSel = cmds.textScrollList('skinCluster_infTSL',q=True,si=True)
    if not influenceSel: return
    
    # Select Influences
    cmds.select(cl=True)
    for inf in influenceSel:
        try: cmds.select(inf,add=True)
        except: print('Unable to select influence ""! Object does not exist...')

def buildWorldSpaceMesh():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Get Affected Geometry
    if not skinData._data.has_key('affectedGeometry'):
        raise Exception('No skin geometry data! Unable to rebuild worldSpace mesh...')
    skinGeo = skinData._data['affectedGeometry'][0]
    if not skinData._data.has_key(skinGeo):
        raise Exception('No skin geometry data for "'+skinGeo+'"! Unable to rebuild worldSpace mesh...')
    if skinData._data[skinGeo]['geometryType'] != 'mesh':
        raise Exception('Skin geometry "'+skinGeo+'" is not a mesh! Unable to rebuild worldSpace mesh...')
    if not skinData._data[skinGeo].has_key('mesh'):
        raise Exception('No world space data for "'+skinGeo+'"! Unable to rebuild worldSpace mesh...')
    
    # Rebuild Mesh
    mesh = skinData._data[skinGeo]['mesh'].rebuildMesh()
    if not mesh.endswith('_worldSpaceMesh'): mesh = cmds.rename(mesh,skinGeo+'_worldSpaceMesh')
    
    # Update TextFieldGrp
    cmds.textFieldGrp('skinCluster_wsMeshTFG',e=True,text=mesh)
    
    # Return Result
    return mesh

def storeWorldSpaceMesh():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Get Affected Geometry
    if not skinData._data.has_key('affectedGeometry'):
        raise Exception('No skin geometry data! Unable to rebuild worldSpace mesh...')
    skinGeo = skinData._data['affectedGeometry'][0]
    if not skinData._data.has_key(skinGeo):
        raise Exception('No skin geometry data for "'+skinGeo+'"! Unable to rebuild worldSpace mesh...')
    if skinData._data[skinGeo]['geometryType'] != 'mesh':
        raise Exception('Skin geometry "'+skinGeo+'" is not a mesh! Unable to rebuild worldSpace mesh...')
    
    # Initialize MeshData
    if not skinData._data[skinGeo].has_key('mesh'):
        skinData._data[skinGeo]['mesh'] = meshData.MeshData()
    
    # Store MeshData
    worldSpaceMesh = cmds.textFieldGrp('skinCluster_wsMeshTFG',q=True,text=True)
    if not cmds.objExists(worldSpaceMesh): raise Exception('World space mesh "'+worldSpaceMesh+'" doesn`t exist!')
    skinData._data[skinGeo]['mesh'].buildData(worldSpaceMesh)
    
    # Delete World Space Mesh
    cmds.delete(worldSpaceMesh)
    
    # Update TextFieldGrp
    cmds.textFieldGrp('skinCluster_wsMeshTFG',e=True,text='')

def rebuildWorldSpaceData():
    '''
    '''
    # Check SkinClusterData
    skinData = easy.GlobalSkinClusterData
    if not skinData: return
    
    # Rebuild World Space Data
    skinData.rebuildWorldSpaceData()

def reloadUI():
    '''
    '''
    # ============
    # - Reset UI -
    # ============
    cmds.textFieldGrp('skinCluster_nameTFG',e=True,text='')
    cmds.textFieldButtonGrp('skinCluster_geoTFB',e=True,text='')
    cmds.textScrollList('skinCluster_infTSL',e=True,ra=True)
    cmds.textScrollList('skinCluster_wtTSL',e=True,ra=True)
    
    cmds.optionMenuGrp('skinCluster_methodOMG',e=True,sl=1)
    cmds.checkBoxGrp('skinCluster_componentCBG',e=True,v1=0)
    cmds.optionMenuGrp('skinCluster_normalizeOMG',e=True,sl=1)
    cmds.checkBoxGrp('skinCluster_deformNormCBG',e=True,v1=0)
    
    cmds.textFieldGrp('skinCluster_wsMeshTFG',e=True,text='')
    
    # =====================================
    # - Get Global SkinClusterData Object -
    # =====================================
    
    skinData = easy.GlobalSkinClusterData
    # Check SkinClusterData
    if not skinData:
        print('No SkinClusterData to load...')
        return
    
    # =================
    # - Repopulate UI -
    # =================
    
    skinName = skinData._data['name']
    cmds.textFieldGrp('skinCluster_nameTFG',e=True,text=skinName)
    skinGeo = skinData._data['affectedGeometry'][0]
    cmds.textFieldGrp('skinCluster_geoTFB',e=True,text=skinGeo)
    influenceList = skinData._influenceData.keys()
    for inf in sorted(influenceList): cmds.textScrollList('skinCluster_infTSL',e=True,a=inf)
    
    attrValues = skinData._data['attrValueDict']
    if attrValues.has_key('skinningMethod'):
        cmds.optionMenuGrp('skinCluster_methodOMG',e=True,sl=(attrValues['skinningMethod']+1))
    if attrValues.has_key('useComponents'):
        cmds.checkBoxGrp('skinCluster_componentCBG',e=True,v1=attrValues['useComponents'])
    if attrValues.has_key('normalizeWeights'):
        cmds.optionMenuGrp('skinCluster_normalizeOMG',e=True,sl=(attrValues['normalizeWeights']+1))
    if attrValues.has_key('deformUserNormals'):
        cmds.checkBoxGrp('skinCluster_deformNormCBG',e=True,v1=attrValues['deformUserNormals'])
    
