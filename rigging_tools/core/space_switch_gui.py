"""
see this page for a reference for the context menu stuff
https://wiki.python.org/moin/PyQt/Handling%20context%20menus

and this one for custom default injection in kwargs
https://stackoverflow.com/questions/14003939/python-function-args-and-kwargs-with-other-specified-keyword-arguments
"""
import os

shikokenAvail = True
try:
    from shiboken import wrapInstance
except:
    shikokenAvail = False
    
try:
    from PySide2 import QtCore, QtWidgets
except:
    from PySide import QtCore, QtGui
    QtWidgets = QtGui

from maya import cmds, mel
from maya import OpenMayaUI

import spaceSwitch
reload(spaceSwitch)
import constrain

class SpaceSwitchGui(QtWidgets.QDialog):
    """
    import spaceSwitchGui
    reload(spaceSwitchGui)
    spaceGui = spaceSwitchGui.SpaceSwitchGui()
    spaceGui.show()
    """
    
    def __init__(self, *args, **kwargs):
        """
        """
        if shikokenAvail:
            parent = kwargs.get('parent', self.maya_main_window())
        else:
            parent = kwargs.get('parent', None)
        QtWidgets.QDialog.__init__(self)
        self.qtSignal = QtCore.Signal()
        self.setWindowFlags(QtCore.Qt.Tool)

        self.setWindowTitle('Constraint Locators')

        #self.resize(400, 250) # re-size the window
        ''' 
        self.setGeometry(650, 200, 600, 300)
        self.setFixedHeight(580)
        self.setFixedWidth(300)
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10)) 
        ''' 
                
        self.debug = False
        self.useFrameRange = False
        self.keyEveryFrame = False
        self.displayConstrainOptions = False
        self.displayBakeOptions = False
        self._buildWidgets()
        self._buildLayout()
        self._connectSignals()
        # self.show(dockable=True)
        # https://groups.google.com/forum/#!msg/python_inside_maya/I-sufW_HCjo/KYPvpDI9dDsJ
        '''
        from maya import OpenMayaUI
        ptr = OpenMayaUI.MQtUtil.mainWindow()
        mainWin = shiboken.wrapInstance(long(ptr), spaceSwitchGui.QtWidgets.QMainWindow)
        spaceGui = spaceSwitchGui.SpaceSwitchGui(parent=mainWin)
        mainWin = spaceSwitchGui.QtGui.QApplication.activeWindow()
        spaceGui = spaceSwitchGui.SpaceSwitchGui(parent=mainWin)
        '''
        # https://www.mail-archive.com/python_inside_maya@googlegroups.com/msg07056.html
        # ptr = OpenMayaUI.MQtUtil.mainWindow()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) 
     

    def maya_main_window(self):
        """
        Return the Maya main window widget as a Python object
        https://forums.autodesk.com/t5/maya-programming/pyside-window-remember-position-and-size/td-p/6562097
        """
        main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
        if shikokenAvail:
            return wrapInstance(long(main_window_ptr), QtGui.QWidget)
        else:
            return None


    def _onDebugCheckboxClicked(self):
        """
        """
        state = self.debugAction.isChecked()
        self.debug = True if state else False


    def _onConstrainSelectedButtonClicked(self):
        """
        """
        spaceSwitch.constrainSelected(info=self.debug, frameRange=False,
            keyLocOnEveryFrame=False)


    def _onConstrainSelectedFRButtonClicked(self):
        """
        """
        spaceSwitch.constrainSelected(info=self.debug, frameRange=True,
            keyLocOnEveryFrame=False)


    def _onConstrainSelectedEFButtonClicked(self):
        """
        """
        spaceSwitch.constrainSelected(info=self.debug, frameRange=True,
            keyLocOnEveryFrame=True)


    def _onBakeSelectedButtonClicked(self):
        """
        """
        spaceSwitch.bakeSelected(info=self.debug, frameRange=False,
            everyFrame=False)


    def _onBakeSelectedFRButtonClicked(self):
        """
        """
        spaceSwitch.bakeSelected(info=self.debug, frameRange=True,
            everyFrame=False)


    def _onBakeSelectedEFButtonClicked(self):
        """
        """
        spaceSwitch.bakeSelected(info=self.debug, frameRange=True,
            everyFrame=True)


    def _onBakePairButtonClicked(self):
        """
        """
        spaceSwitch.bakePair()


    def _onParentConstraintSelectedButtonClicked(self):
        """
        """
        constrain.parentConstraint()


    def _onParentConstrainTranslateSelectedButtonClicked(self):
        """
        """
        constrain.parentConstraintTranslate()


    def _onRemoveConstraintSelectedButtonClicked(self):
        """
        """
        cmds.undoInfo(openChunk=True)
        constrain.removeConstraint(setKeys=False)
        cmds.undoInfo(closeChunk=True)


    def _onEulerFilterButtonClicked(self):
        """
        """
        mel.eval('filterCurve')


    def _onSelectConstrainedButtonClicked(self):
        """
        """
        nodeList = None
        sl = cmds.ls(sl=1)
        if sl:
            nodeList = sl
        data = spaceSwitch.getConstrained(nodeList=nodeList)
        if data:
            cmds.select(data)
        else:
            cmds.warning('no constrained nodes for selected')


    def _onSelectLocatorsButtonClicked(self):
        """
                """
        data = spaceSwitch.getLocator(nodeList=cmds.ls(sl=1))
        if data:
            cmds.select(data)
        else:
            cmds.warning('no locators for selected')


    def _onConstrainExpansionButtonClicked(self):
        """
        """
        if self.displayConstrainOptions:
            self.constrainContainerVWidget2.hide()
            self.displayConstrainOptions = False
            self.constrainExpansionButton.setText("Constrain Options >")
        else:
            self.constrainContainerVWidget2.show()
            self.displayConstrainOptions = True
            self.constrainExpansionButton.setText("Constrain Options v")
        # self.resize(minimumSizeHint())
        # self.mainLayout.resize(minimumSizeHint())
        self.adjustSize()


    def _onBakeExpansionButtonClicked(self):
        """
        """
        if self.displayBakeOptions:
            self.bakeContainerVWidget2.hide()
            self.displayBakeOptions = False
            self.bakeExpansionButton.setText("Bake Options >")
        else:
            self.bakeContainerVWidget2.show()
            self.displayBakeOptions = True
            self.bakeExpansionButton.setText("Bake Options v")
        # self.resize(minimumSizeHint())
        # self.mainLayout.resize(minimumSizeHint())
        self.adjustSize()


    def _buildWidgets(self):
        """
        """
        # self.statusBar()
        # self.constrainSelectedToLocatorsButton = QtWidgets.QPushButton(self)
        self.constrainSelectedToLocatorsButton = QPushButton(self)
        self.constrainSelectedToLocatorsButton.setText("Constrain Selected")
        self.bakeSelectedButton = QtWidgets.QPushButton(self)
        self.bakeSelectedButton.setText("Bake Selected")
        self.removeConstraintButton = QtWidgets.QPushButton(self)
        self.removeConstraintButton.setText("Remove Constraint")
        self.eulerFilterButton = QtWidgets.QPushButton(self)
        self.eulerFilterButton.setText("Euler Filter")

        # self.constrainLabel = QtWidgets.QLabel('Constrain >')
        self.constrainExpansionButton = QtWidgets.QPushButton(self)
        self.constrainExpansionButton.setText("Constrain Options >")
        self.constrainSelectedFRButton = QtWidgets.QPushButton(self)
        self.constrainSelectedFRButton.setText("Constrain Selected\n(Frame Range)")
        self.constrainSelectedEFButton = QtWidgets.QPushButton(self)
        self.constrainSelectedEFButton.setText("Constrain Selected\n(Key Locators on Every Frame)")

        # self.bakeLabel = QtWidgets.QLabel('Bake:')
        self.bakeExpansionButton = QtWidgets.QPushButton(self)
        self.bakeExpansionButton.setText("Bake Options >")
        self.bakeSelectedFRButton = QtWidgets.QPushButton(self)
        self.bakeSelectedFRButton.setText("Bake Selected\n(Frame Range)")
        self.bakeSelectedEFButton = QtWidgets.QPushButton(self)
        self.bakeSelectedEFButton.setText("Bake Selected\n(Set Keys on Every Frame)")
        self.bakePairButton = QtWidgets.QPushButton(self)
        self.bakePairButton.setText("Bake Pair")

        self.utilitiesLabel = QtWidgets.QLabel('Utilities:')
        self.selectConstrainedButton = QtWidgets.QPushButton(self)
        self.selectConstrainedButton.setText("Select Constrained")
        self.selectLocatorsButton = QtWidgets.QPushButton(self)
        self.selectLocatorsButton.setText("Select Locators")

        self.debugAction = QtWidgets.QAction("Debug", self)
        self.debugAction.setStatusTip('Enable more info')
        self.debugAction.setCheckable(True)
        self.debugAction.triggered.connect(self._onDebugCheckboxClicked)
        if self.debug:
            self.debugAction.setChecked(QtCore.Qt.CheckState.Checked)
        else:
            self.debugAction.setChecked(QtCore.Qt.CheckState.Unchecked)

        self.mainMenu = QtWidgets.QMenuBar()
        fileMenu = self.mainMenu.addMenu('&Preferences >')
        fileMenu.addAction(self.debugAction)


    def _buildLayout(self):
        """
        """
        # -----------------
        # simple
        # Create a widget with a vertical layout to hold our simple label
        # and simple buttons
        simpleContainerVWidget = QtWidgets.QWidget()
        self.simpleContainerVLayout = QtWidgets.QVBoxLayout()
        simpleContainerVWidget.setLayout(self.simpleContainerVLayout)
        
        # add 'simple:' label to vertical layout
        self.simpleContainerVLayout.addWidget(self.constrainSelectedToLocatorsButton)
        self.simpleContainerVLayout.addWidget(self.bakeSelectedButton)
        self.simpleContainerVLayout.addWidget(self.removeConstraintButton)
        self.simpleContainerVLayout.addWidget(self.eulerFilterButton)
        self.simpleContainerVLayout.addWidget(self.selectConstrainedButton)
        self.simpleContainerVLayout.addWidget(self.selectLocatorsButton)

        # http://doc.qt.io/qt-5/stylesheet-reference.html
        self.constrainSelectedToLocatorsButton.setStyleSheet("QPushButton { text-align: left; background-color: #cc6666; padding: 5px; }")
        self.bakeSelectedButton.setStyleSheet("QPushButton { text-align: left; background-color: #999933; padding: 5px; }")
        self.removeConstraintButton.setStyleSheet("QPushButton { text-align: left; background-color: #669933; padding: 5px; }")
        self.eulerFilterButton.setStyleSheet("QPushButton { text-align: left; padding: 5px; }")
        self.selectConstrainedButton.setStyleSheet("QPushButton { text-align: left; color: #ffffcc; padding: 5px; }")
        self.selectLocatorsButton.setStyleSheet("QPushButton { text-align: left; color: #ffcccc; padding: 5px; }")

        # -----------------
        # constrain
        # Create a widget with a vertical layout to hold our constrain label
        # and constrain button
        constrainContainerVWidget = QtWidgets.QWidget()
        self.constrainContainerVLayout = QtWidgets.QVBoxLayout()
        constrainContainerVWidget.setLayout(self.constrainContainerVLayout)

        # add 'constrain:' label to vertical layout
        # self.constrainContainerVLayout.addWidget(self.constrainLabel)
        self.constrainContainerVLayout.addWidget(self.constrainExpansionButton)
        self.constrainExpansionButton.setStyleSheet("QPushButton { text-align: left; \
            background-color: rgba(255, 255, 255, 0); border: none; padding: 0px; }")

        # Create a seond widget with a vertical layout to hold our buttons
        self.constrainContainerVWidget2 = QtWidgets.QWidget()
        self.constrainContainerVLayout2 = QtWidgets.QVBoxLayout()
        self.constrainContainerVWidget2.setLayout(self.constrainContainerVLayout2)
        
        if self.displayConstrainOptions:
            self.constrainContainerVWidget2.show()
        else:
            self.constrainContainerVWidget2.hide()

        # add 'constrain:' buttons to vertical layout
        self.constrainContainerVLayout2.addWidget(self.constrainSelectedFRButton)
        self.constrainContainerVLayout2.addWidget(self.constrainSelectedEFButton)

        # self.constrainLabel.setStyleSheet("QLabel {color: #ff9999; padding: 5px; }")
        self.constrainSelectedFRButton.setStyleSheet("QPushButton { text-align: left; color: #ffcccc; padding: 5px; }")
        self.constrainSelectedEFButton.setStyleSheet("QPushButton { text-align: left; color: #ffcccc; padding: 5px;  }")

        # -----------------
        # bake
        # Create a widget with a vertical layout to hold our bake label
        # and bake button
        bakeContainerVWidget = QtWidgets.QWidget()
        self.bakeContainerVLayout = QtWidgets.QVBoxLayout()
        bakeContainerVWidget.setLayout(self.bakeContainerVLayout)

        self.bakeContainerVLayout.addWidget(self.bakeExpansionButton)
        self.bakeExpansionButton.setStyleSheet("QPushButton { text-align: left; \
            background-color: rgba(255, 255, 255, 0); border: none; padding: 0px; }")

        self.bakeContainerVWidget2 = QtWidgets.QWidget()
        self.bakeContainerVLayout2 = QtWidgets.QVBoxLayout()
        self.bakeContainerVWidget2.setLayout(self.bakeContainerVLayout2)
        
        if self.displayBakeOptions:
            self.bakeContainerVWidget2.show()
        else:
            self.bakeContainerVWidget2.hide()

        # add 'bake:' label to vertical layout
        # self.bakeContainerVLayout.addWidget(self.bakeLabel)
        self.bakeContainerVLayout2.addWidget(self.bakeSelectedFRButton)
        self.bakeContainerVLayout2.addWidget(self.bakeSelectedEFButton)
        self.bakeContainerVLayout2.addWidget(self.bakePairButton)

        self.bakeSelectedFRButton.setStyleSheet("QPushButton { text-align: left; color: #ffffcc; padding: 5px;  }")
        self.bakeSelectedEFButton.setStyleSheet("QPushButton { text-align: left; color: #ffffcc; padding: 5px;  }")
        self.bakePairButton.setStyleSheet("QPushButton { text-align: left; color: #ffffcc; padding: 5px;  }")
        '''
        # -----------------
        # utilities
        # Create a widget with a vertical layout to hold our bake label
        # and bake button
        utilitiesContainerVWidget = QtWidgets.QWidget()
        self.utilitiesContainerVLayout = QtWidgets.QVBoxLayout()
        utilitiesContainerVWidget.setLayout(self.utilitiesContainerVLayout)
        
        # add 'utilities:' label to vertical layout
        self.utilitiesContainerVLayout.addWidget(self.utilitiesLabel)

        self.selectConstrainedButton.setStyleSheet("QPushButton { text-align: left; color: #ffffcc; padding: 5px; }")
        self.selectLocatorsButton.setStyleSheet("QPushButton { text-align: left; color: #ffcccc; padding: 5px; }")
        self.bakePairButton.setStyleSheet("QPushButton { text-align: left; color: #ffffcc; padding: 5px;  }")
        '''
        '''
        utilitiesContainerHWidget = QtWidgets.QWidget()
        self.utilitiesContainerHLayout = QtWidgets.QHBoxLayout()
        utilitiesContainerHWidget.setLayout(self.utilitiesContainerHLayout)

        # add 'utilities:' btns to horizontal layout
        self.utilitiesContainerHLayout.addWidget(self.selectConstrainedButton)
        self.utilitiesContainerHLayout.addWidget(self.selectLocatorsButton)

        # add utilities btn vertical layout to the utilities btn horizontal layout
        self.utilitiesContainerVLayout.addWidget(utilitiesContainerHWidget)

        utilitiesBakePairContainerHWidget = QtWidgets.QWidget()
        self.utilitiesBakePairContainerHLayout = QtWidgets.QHBoxLayout()
        utilitiesBakePairContainerHWidget.setLayout(self.utilitiesBakePairContainerHLayout)

        # add 'utilities:' btns to horizontal layout
        self.utilitiesBakePairContainerHLayout.addWidget(self.bakePairButton)

        # add utilities btn vertical layout to the utilities btn horizontal layout
        self.utilitiesContainerVLayout.addWidget(utilitiesBakePairContainerHWidget)
        '''

        # Make a main widget with a vertical layout to hold our qWidgets,
        # and make this the main widget of this dialog.
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(simpleContainerVWidget)
        self.mainLayout.addWidget(constrainContainerVWidget)
        self.mainLayout.addWidget(self.constrainContainerVWidget2)
        self.mainLayout.addWidget(bakeContainerVWidget)
        self.mainLayout.addWidget(self.bakeContainerVWidget2)
        # self.mainLayout.addWidget(utilitiesContainerVWidget)
        self.mainLayout.addWidget(self.mainMenu)
        self.setLayout(self.mainLayout)


    def _connectSignals(self):
        """
        """
        self.constrainSelectedToLocatorsButton.clicked.connect(self._onConstrainSelectedButtonClicked)
        self.bakeSelectedButton.clicked.connect(self._onBakeSelectedButtonClicked)
        self.removeConstraintButton.clicked.connect(self._onRemoveConstraintSelectedButtonClicked)
        self.eulerFilterButton.clicked.connect(self._onEulerFilterButtonClicked)

        self.constrainExpansionButton.clicked.connect(self._onConstrainExpansionButtonClicked)
        self.constrainSelectedFRButton.clicked.connect(self._onConstrainSelectedFRButtonClicked)
        self.constrainSelectedEFButton.clicked.connect(self._onConstrainSelectedEFButtonClicked)

        self.bakeExpansionButton.clicked.connect(self._onBakeExpansionButtonClicked)
        self.bakeSelectedFRButton.clicked.connect(self._onBakeSelectedFRButtonClicked)
        self.bakeSelectedEFButton.clicked.connect(self._onBakeSelectedEFButtonClicked)
        self.selectConstrainedButton.clicked.connect(self._onSelectConstrainedButtonClicked)
        self.selectLocatorsButton.clicked.connect(self._onSelectLocatorsButtonClicked)
        self.bakePairButton.clicked.connect(self._onBakePairButtonClicked)



class RightClickMenu(QtWidgets.QMenu):
 
    def __init__(self, *args, **kwargs):
        QtWidgets.QMenu.__init__(self, *args)

        # Prepare the parent widget for using the right-click menu
        self.parentWidget().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.parentWidget().customContextMenuRequested.connect(self.showMenu)
 
    def showMenu(self, *args):
 
        self.exec_(QtWidgets.QCursor.pos())


class QPushButton(QtWidgets.QPushButton):

    def __init__(self, *args, **kwargs):

        parent = kwargs.get('parent', None)

        QtWidgets.QPushButton.__init__(self, *args, **kwargs)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        quitAction = QtWidgets.QAction("check out the below Constrain Options", self)
        # quitAction.triggered.connect(self.reject)
        self.addAction(quitAction)
