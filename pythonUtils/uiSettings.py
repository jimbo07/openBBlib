import sys
from functools import partial
# from cupshelpers.config import prefix
try:
    from PySide2 import QtCore, QtWidgets, QtUiTools
except:
    from PyQt4 import QtCore, QtGui
    QtWidgets = QtGui

import sys

dev = "/jobs/generic/dev/chris-g/dev"

if dev not in sys.path:
    sys.path.append(dev)

import tab_widget
reload(tab_widget)

class UI(QtGui.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, None)

        self.current_workspace = None


        self.setGeometry(100, 50, 1500, 800)
        self.setMinimumSize(1000, 700)
        self.setWindowTitle('Rig builder')

        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        self.main_wrapper_layout = QtWidgets.QVBoxLayout()
        self.main_wrapper_frame = QtWidgets.QFrame()
        self.main_wrapper_frame.setLayout(self.main_wrapper_layout)
#         self.main_wrapper_frame.setStyleSheet("QFrame{background-color:#30373F;}")qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #dadbde, stop: 1 #f6f7fa)
        self.main_wrapper_frame.setStyleSheet("QFrame{background-color:qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,stop: 0 #30373F, stop: 1 #20292E);}")
        self.central_layout.addWidget(self.main_wrapper_frame)
        self.main_wrapper_layout.setContentsMargins(0,0,0,0)
        self.main_wrapper_layout.setSpacing(0)

        self.header_frame = QtWidgets.QFrame()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_frame.setLayout(self.header_layout)
        self.main_wrapper_layout.addWidget(self.header_frame)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(0)
#         self.header_frame.setMinimumHeight(50)
        self.header_frame.setStyleSheet("QFrame{background-color:transparent;}")

        self.left_header_layout = QtWidgets.QVBoxLayout()
        self.header_layout.addLayout(self.left_header_layout)
        self.left_header_layout.setContentsMargins(0, 0, 0, 0)
        self.left_header_layout.setSpacing(0)

        self.header_layout.addStretch()

        self.right_header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.addLayout(self.right_header_layout)
        self.right_header_layout.setContentsMargins(0, 0, 0, 0)
        self.right_header_layout.setSpacing(25)



        self.extract_button_widget = ExtractButtonWidget(self)
        self.right_header_layout.addWidget(self.extract_button_widget)

        self.build_button_widget = BuildButtonWidget(self)
        self.right_header_layout.addWidget(self.build_button_widget)


        self.tab_widget = tab_widget.TabWidget()
        self.main_wrapper_layout.addWidget(self.tab_widget)

        self.tab_widget.currentChanged.connect(self.changed_workspace)

        self.tab_widget_style_sheet = """


        QWidget{
            color:#ffffff;
            font: 18px "Courier New";
            outline:none;
            background-color:#363F46;
            border-style: solid;
            border-width: 0;
            border-radius:2;

        }
        QFrame#tab_background{
            color:#ffffff;
            font: 18px "Courier New";
            outline:none;
            background-color:363F46;
            border-style: solid;
            border-width: 0;

        }

        QFrame#tab{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:#273238;
            border-top-left-radius:10;
            border-top-right-radius:10;
            border-bottom-left-radius:0;
            border-bottom-right-radius:0;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:10;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;

        }


        QFrame#current_tab{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:#363F46;
            border-top-left-radius:10;
            border-top-right-radius:10;
            border-bottom-left-radius:0;
            border-bottom-right-radius:0;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:10;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;

        }

        QPushButton#close_button{
            font: bold 15px "Courier New";
            outline:none;
            color:white;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/round_delete_icon&16.png");
            background-repeat:None;
            background-position: centre;


        }

        QPushButton{
            font: 12px "Courier New";
            outline:none;
            color:white;
            background-color:transparent;

        }

        QPushButton:hover{
            color:#4AC5B3;
            background-color:transparent;

        }

        QPushButton:pressed{
            color:#273238;
            background-color:transparent;

        }

        QPushButton#add_button{
            font: 20px "Courier New";
            outline:none;
            color:white;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/round_plus_icon&16.png");
            background-repeat:None;
            background-position: bottom centre;
            border-top-right-radius:10;
            border-top-left-radius:10;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            margin-bottom:7;

        }

        QPushButton#add_button:hover{
            color:#4AC5B3;
            background-color:transparent;

        }

        QPushButton#add_button:pressed{
            color:#273238;
            background-color:transparent;

        }
        """

        self.tab_widget.setStyleSheet(self.tab_widget_style_sheet)
        self.tab_widget.tab_layout.setContentsMargins(30, 0, 0, 0)

        self.workspace_widget = WorkspaceWidget(self,
"rig_barbie_default_A")
        self.tab_widget.add_tab(self.workspace_widget,
self.workspace_widget.name)

        self.workspace_widget = WorkspaceWidget(self,
"rig_barbie_default_B")
        self.tab_widget.add_tab(self.workspace_widget,
self.workspace_widget.name)

        self.extract_button_widget.print_to_console.connect(self.extract_current)
        self.build_button_widget.print_to_console.connect(self.build_current)

        self.progress_bar_widget = ProgressBarWidget(self)
        self.main_wrapper_layout.addWidget(self.progress_bar_widget)

        self.main_wrapper_layout.setStretch(1,1)

    def changed_workspace(self, *args):
        if self.current_workspace:
            self.current_workspace.asset_widget.hide()

        self.current_workspace = self.tab_widget.currentWidget
        if not self.current_workspace.asset_widget in self.left_header_layout.children():
            self.left_header_layout.addWidget(self.current_workspace.asset_widget)

        self.current_workspace.asset_widget.show()


    def extract_current(self, *args):
        self.current_workspace.console_widget.print_to_console(*args)

    def build_current(self, *args):
        self.current_workspace.console_widget.print_to_console(*args)

class WorkspaceWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent, name):
        super(WorkspaceWidget, self).__init__(parent)
        self.name = name

        self.main_wrapper_layout = QtWidgets.QVBoxLayout()
        self.main_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.main_wrapper_layout.setSpacing(0)
        self.setLayout(self.main_wrapper_layout)

        self.body_layout = QtWidgets.QHBoxLayout()
        self.body_frame = QtWidgets.QFrame()
        self.body_frame.setLayout(self.body_layout)
#         self.body_frame.setStyleSheet("QFrame{background-color:#363F46;border-radius:10;}")
        self.body_frame.setStyleSheet("QFrame{background-color:transparent;}")

        self.main_wrapper_layout.addWidget(self.body_frame)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(5)

        self.main_wrapper_layout.setStretch(1,1)

        self.body_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.body_layout.addWidget(self.body_splitter)
        self.body_splitter.setHandleWidth(10)
        self.body_splitter.setStyleSheet("QSplitter::handle{background-color:#363F46;}")

        self.left_body_frame = QtWidgets.QFrame()
        self.left_body_layout = QtWidgets.QVBoxLayout()
        self.left_body_frame.setLayout(self.left_body_layout)
        self.body_splitter.addWidget(self.left_body_frame)
        self.left_body_layout.setContentsMargins(0, 0, 0, 0)
        self.left_body_layout.setSpacing(5)

        self.center_body_frame = QtWidgets.QFrame()
        self.center_body_frame.setStyleSheet("QFrame{background-color:transparent;}")

        self.center_body_layout = QtWidgets.QVBoxLayout()
        self.center_body_frame.setLayout(self.center_body_layout)
        self.body_splitter.addWidget(self.center_body_frame)
        self.center_body_layout.setContentsMargins(0, 10, 0, 10)
        self.center_body_layout.setSpacing(5)

        self.right_body_frame = QtWidgets.QFrame()
        self.right_body_layout = QtWidgets.QVBoxLayout()
        self.right_body_frame.setLayout(self.right_body_layout)
        self.body_splitter.addWidget(self.right_body_frame)
        self.right_body_layout.setContentsMargins(0, 10, 10, 10)
        self.right_body_layout.setSpacing(0)

        self.body_splitter.setSizes([300,300,300])


        self.right_body_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.right_body_layout.addWidget(self.right_body_splitter)
        self.right_body_splitter.setHandleWidth(10)
        self.right_body_splitter.setStyleSheet("QSplitter::handle{background-color:#363F46;}")

        self.center_body_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.center_body_layout.addWidget(self.center_body_splitter)
        self.center_body_splitter.setHandleWidth(10)
        self.center_body_splitter.setStyleSheet("QSplitter::handle{background-color:#363F46;}")





        self.attribute_frame = QtWidgets.QFrame()
        self.attribute_layout = QtWidgets.QVBoxLayout()
        self.attribute_frame.setLayout(self.attribute_layout)
        self.center_body_splitter.addWidget(self.attribute_frame)
        self.attribute_layout.setContentsMargins(0, 0, 0, 0)
        self.attribute_layout.setSpacing(5)
        self.attribute_frame.setStyleSheet("QFrame{background-color:#273238;border-radius:2;}")


        self.console_frame = QtWidgets.QFrame()
        self.console_layout = QtWidgets.QVBoxLayout()
        self.console_frame.setLayout(self.console_layout)
        self.center_body_splitter.addWidget(self.console_frame)
        self.console_layout.setContentsMargins(0, 0, 0, 0)
        self.console_layout.setSpacing(5)
        self.console_frame.setStyleSheet("QFrame{background-color:#273238;border-radius:2;}")


        self.center_body_splitter.setSizes([400,500])

        self.asset_manager_frame = QtWidgets.QFrame()
        self.asset_manager_layout = QtWidgets.QVBoxLayout()
        self.asset_manager_frame.setLayout(self.asset_manager_layout)
        self.right_body_splitter.addWidget(self.asset_manager_frame)
        self.asset_manager_layout.setContentsMargins(0, 0, 0, 0)
        self.asset_manager_layout.setSpacing(5)
        self.asset_manager_frame.setStyleSheet("QFrame{background-color:#273238;border-radius:2;}")

        self.right_body_splitter.setSizes([400,500])

        self.tree_widget = TreeWidget(self)
        self.left_body_layout.addWidget(self.tree_widget)



        self.console_widget = ConsoleWidget(self)
        self.console_layout.addWidget(self.console_widget)

        self.tree_widget.print_to_console.connect(self.console_widget.print_to_console)



        self.attribute_editor_widget = AttributeEditorWidget(self,
console=self.console_widget)
        self.attribute_layout.addWidget(self.attribute_editor_widget)

        self.asset_manager_widget = AssetManagerWidget(self)
        self.asset_manager_widget.update_asset.connect(self.console_widget.print_to_console)
        self.asset_manager_widget.refresh_asset_info.connect(partial(self.console_widget.print_to_console,
"Refreshing asset info"))
        self.asset_manager_layout.addWidget(self.asset_manager_widget)


        self.asset_widget = AssetWidget(self, self.name)
        self.asset_widget.print_to_console.connect(self.console_widget.print_to_console)



    def event(self, event):

        if (event.type()==QtCore.QEvent.KeyPress): # and (event.key()==QtCore.Qt.Key_Tab):
            print (event.key())
            return True

        return True#QtWidgets.QFrame.event(self, event)

class GenericWidget(QtWidgets.QFrame):

    def __init__(self, parent, label=None, color="#ff0000"):
        super(GenericWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.setStyleSheet("QFrame{{background-color:{};}}".format(color))

        if label:
            self.label = QtWidgets.QLabel(str(label))
            self.main_layout.addWidget(self.label)

class AssetManagerWidget(QtWidgets.QFrame):
    update_asset = QtCore.pyqtSignal(str)
    refresh_asset_info = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(AssetManagerWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.style_sheet = """
        QFrame{
            color:#ffffff;
            font: 18px "Courier New";
            outline:none;
            background-color:transparent;
            border-radius:2;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:0;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;
        }
        QPushButton#update_all_button{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/arrow_top_icon&16.png");
            background-repeat:None;
            background-position: right;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:0;
            padding-right:22;
            padding-bottom:0;
            margin-bottom:0;
        }
        QPushButton#refresh_button{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/refresh_icon&16.png");
            background-repeat:None;
            background-position: right;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:0;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;
        }
        QFrame#asset_list_group_frame{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:#273238;
            border-radius:2;
        }

        QFrame#asset_list_group_header_frame{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            border-top-left-radius:2;
            border-top-right-radius:2;
            border-bottom-left-radius:0;
            border-bottom-right-radius:0;

        }
        QLabel{
            font: 15px "Courier New";
            background-color:transparent;
        }
        """

        self.setStyleSheet(self.style_sheet)


        self.tools_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.tools_layout)
        self.tools_layout.setContentsMargins(0, 10, 15, 0)

        self.refresh_button = QtWidgets.QPushButton()
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.pressed.connect(self.refresh_asset_info)

        self.refresh_button.setFixedHeight(16)
        self.tools_layout.addWidget(self.refresh_button)
        self.tools_layout.addStretch()
        self.update_all_button = QtWidgets.QPushButton("Update All")
        self.update_all_button.pressed.connect(partial(self.update_asset.emit,
"*"))
        self.update_all_button.setObjectName("update_all_button")
        self.update_all_button.setFixedHeight(16)
        self.tools_layout.addWidget(self.update_all_button)


        self.asset_list_frame = QtWidgets.QFrame()
        self.asset_list_layout = QtWidgets.QVBoxLayout()
        self.asset_list_frame.setLayout(self.asset_list_layout)
        self.main_layout.addWidget(self.asset_list_frame)
        self.asset_list_layout.setSpacing(0)

        #Models
        self.model_list_widget = AssetListGroupWidget(self, "Models",
prefix="model")
        self.model_list_widget.update_asset.connect(self.update_asset)
        self.asset_list_layout.addWidget(self.model_list_widget)

        #examples
        self.asset_example = AssetItemWidget(self, "body_geo",
"model_barbie_default_A")
        self.asset_example.update_asset.connect(self.update_asset)
        self.model_list_widget.model_list_layout.insertWidget(0,
self.asset_example)

        self.asset_example = AssetItemWidget(self, "dress_geo",
"model_dress_default_A", status="approved")
        self.asset_example.update_asset.connect(self.update_asset)
        self.model_list_widget.model_list_layout.insertWidget(0,
self.asset_example)

        self.asset_example = AssetItemWidget(self, "jetpack_geo",
"model_jetPack_default_A", status="attention")
        self.asset_example.update_asset.connect(self.update_asset)
        self.model_list_widget.model_list_layout.insertWidget(0,
self.asset_example)


        #Rigs
        self.rig_list_widget = AssetListGroupWidget(self, "Rigs", prefix="rig")
        self.rig_list_widget.update_asset.connect(self.update_asset)
        self.asset_list_layout.addWidget(self.rig_list_widget)

        #Examples
        self.asset_example = AssetItemWidget(self, "body_rig",
"rig_barbie_default_A", status="approved")
        self.asset_example.update_asset.connect(self.update_asset)
        self.rig_list_widget.model_list_layout.insertWidget(0,
self.asset_example)

        self.asset_example = AssetItemWidget(self, "face_rig",
"rigFace_barbie_default_A")
        self.asset_example.update_asset.connect(self.update_asset)
        self.rig_list_widget.model_list_layout.insertWidget(0,
self.asset_example)

        #Texture
        self.texture_list_widget = AssetListGroupWidget(self,
"Textures", prefix="texture")
        self.texture_list_widget.update_asset.connect(self.update_asset)
        self.asset_list_layout.addWidget(self.texture_list_widget)

        #Examples
        self.asset_example = AssetItemWidget(self, "apply_textures", "diffuse_barbie_default_A", status="approved")
        self.asset_example.update_asset.connect(self.update_asset)
        self.texture_list_widget.model_list_layout.insertWidget(0, self.asset_example)

        #Animation
        self.animation_list_widget = AssetListGroupWidget(self, "Animation", prefix="anim")
        self.animation_list_widget.update_asset.connect(self.update_asset)
        self.asset_list_layout.addWidget(self.animation_list_widget)

        #Examples
        self.asset_example = AssetItemWidget(self, "load_anim", "joints_bodyRom_barbie")
        self.asset_example.update_asset.connect(self.update_asset)
        self.animation_list_widget.model_list_layout.insertWidget(0,
self.asset_example)


        self.asset_list_layout.addStretch()



class AssetListGroupWidget(QtWidgets.QFrame):
    update_asset = QtCore.pyqtSignal(str)

    def __init__(self, parent, name, prefix=None):
        super(AssetListGroupWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        if prefix:
            self.prefix = prefix
        else:
            self.prefix = name


        self.style_sheet = """
        QPushButton#update_button{
            color:#ffffff;
            font: 10px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/arrow_top_icon&16.png");
            background-repeat:None;
            background-position: right;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:0;
            padding-right:22;
            padding-bottom:0;
            margin-bottom:0;
        }



        QPushButton#collapse_button{
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/br_up_icon&16.png");
            background-repeat:None;
            background-position: left;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:25;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;
        }
        QPushButton#expand_button{
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/br_down_icon&16.png");
            background-repeat:None;
            background-position: left;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:25;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;
        }
        """

        self.setStyleSheet(self.style_sheet)



        #model
        self.model_frame = QtWidgets.QFrame()
        self.model_layout = QtWidgets.QVBoxLayout()
        self.model_layout.setContentsMargins(0, 0, 0, 0)
        self.model_frame.setObjectName("asset_list_group_frame")

        self.model_frame.setLayout(self.model_layout)
        self.main_layout.addWidget(self.model_frame)

        self.model_header_frame = QtWidgets.QFrame()
        self.model_header_frame.setObjectName("asset_list_group_header_frame")

        self.header_layout = QtWidgets.QHBoxLayout()
        self.model_header_frame.setLayout(self.header_layout)
        self.model_layout.addWidget(self.model_header_frame)
        self.header_layout.setContentsMargins(0, 15, 6, 10)
        self.header_layout.setSpacing(0)

        self.model_list_layout = QtWidgets.QVBoxLayout()
        self.model_list_frame = QtWidgets.QFrame()
        self.model_list_frame.setLayout(self.model_list_layout)
        self.model_layout.addWidget(self.model_list_frame)
        self.model_list_layout.setContentsMargins(0, 0, 0, 0)
        self.model_list_layout.setSpacing(3)

        self.collapse_button = QtWidgets.QPushButton(name)
        self.collapse_button.pressed.connect(self.toggle_collapse)
        self.header_layout.addWidget(self.collapse_button)
        self.collapse_button.setObjectName("collapse_button")

#         self.model_label = QtWidgets.QLabel(name)
#         self.header_layout.addWidget(self.model_label)

        self.header_layout.addStretch()

        self.update_button = QtWidgets.QPushButton("Update All {}".format(name))
        self.update_button.pressed.connect(partial(self.update_asset.emit,
"{}*_*".format(prefix)))
        self.update_button.setObjectName("update_button")
        self.update_button.setFixedHeight(16)
        self.header_layout.addWidget(self.update_button)


    def toggle_collapse(self):

        if self.model_list_frame.isHidden():
            self.model_list_frame.show()
            self.collapse_button.setObjectName("collapse_button")
            self.setStyleSheet(self.styleSheet())

        else:
            self.model_list_frame.hide()
            self.collapse_button.setObjectName("expand_button")
            self.setStyleSheet(self.styleSheet())



class AssetItemWidget(QtWidgets.QFrame):
    update_asset = QtCore.pyqtSignal(str)

    def __init__(self, parent, operator, name, status=None):
        super(AssetItemWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 3, 0, 0)
        self.main_layout.setSpacing(5)

        self.setFixedHeight(30)
        self.setLayout(self.main_layout)
        self.style_sheet = """
        QFrame{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:#363F46;
            border-radius:2;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:0;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:0;
        }

        QPushButton#update_button{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/arrow_top_icon&16.png");
            background-repeat:None;
            background-position: centre;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:5;
            padding-left:0;
            padding-right:0;
            padding-bottom:0;
            margin-bottom:1;
        }

        QLabel#approved_label{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/cert_icon&16.png");
            background-repeat:None;
            background-position: centre;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:5;
            padding-left:10;
            padding-right:5;
            padding-bottom:0;
            margin-bottom:0;
        }

        QLabel#attention_label{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/attention_icon&16.png");
            background-repeat:None;
            background-position: centre;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:5;
            padding-left:10;
            padding-right:5;
            padding-bottom:0;
            margin-bottom:0;
        }
        QLabel#operator_label{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:0;
            padding-left:0;
            padding-right:20;
            padding-bottom:0;
            margin-bottom:0;
        }
        """

        self.setStyleSheet(self.style_sheet)
        self.asset_info_layout = QtWidgets.QHBoxLayout()

        self.main_layout.addLayout(self.asset_info_layout)



        self.operator_label = QtWidgets.QLabel(operator)
        self.operator_label.setObjectName("operator_label")
        self.asset_info_layout.addWidget(self.operator_label)
        self.asset_info_layout.addStretch()

        self.name_label = QtWidgets.QLabel(name)
        self.asset_info_layout.addWidget(self.name_label)

        self.asset_info_layout.addStretch()

        self.status_label = QtWidgets.QLabel()
        self.asset_info_layout.addWidget(self.status_label)

        if status == "approved":
            self.status_label.setObjectName("approved_label")
            self.status_label.setToolTip("Approved")

        elif status == "attention":
            self.status_label.setObjectName("attention_label")
            self.status_label.setToolTip("Attention")


        self.version_label = QtWidgets.QLabel("v1/1")
        self.asset_info_layout.addWidget(self.version_label)

        self.update_button = QtWidgets.QPushButton()
        self.update_button.setObjectName("update_button")
        self.update_button.pressed.connect(partial(self.update_asset.emit,
name))
        self.asset_info_layout.addWidget(self.update_button)


class BuildButtonWidget(QtWidgets.QWidget):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(BuildButtonWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 10, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
#         self.setFixedSize(90,70)

        self.build_button = QtWidgets.QPushButton("Build")
        self.build_button.setFixedHeight(60)
        self.build_button.setFixedWidth(60)

        self.build_button.clicked.connect(self.build_pressed)

        self.main_layout.addWidget(self.build_button)

        self.style_sheet = """
        QPushButton{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/playback_play_icon&24.png");
            background-repeat:None;
            background-position: top;
            border-radius:3;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:30;
            padding-left:5;
            padding-right:5;
            text-align:centre;
            margin-top:15;
        }

        QPushButton:hover{
            background-color:#4B5761;

        }

        QPushButton:pressed{
            font: 11px "Courier New";
            outline:none;
            background-color:#273238;
            border-color:#363F46;

        }
        """

        self.setStyleSheet(self.style_sheet)

    def build_pressed(self):
        self.print_to_console.emit("Building...", "#66ff66")



class ExtractButtonWidget(QtWidgets.QWidget):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(ExtractButtonWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 10, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
#         self.setFixedSize(90,70)

        self.build_button = QtWidgets.QPushButton("Extract")
        self.build_button.setFixedHeight(60)
        self.build_button.setFixedWidth(60)

        self.build_button.clicked.connect(self.extract_pressed)

        self.main_layout.addWidget(self.build_button)

        self.style_sheet = """
        QPushButton{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/download_icon&24.png");
            background-repeat:None;
            background-position: top;
            border-radius:3;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:30;
            padding-left:5;
            padding-right:5;
            text-align:centre;
            margin-top:15;
        }

        QPushButton:hover{
            background-color:#4B5761;

        }

        QPushButton:pressed{
            font: 11px "Courier New";
            outline:none;
            background-color:#273238;
            border-color:#363F46;

        }
        """

        self.setStyleSheet(self.style_sheet)

    def extract_pressed(self):
        self.print_to_console.emit("Extracting...", "#aaaaff")



class AssetWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)
    def __init__(self, parent, name):
        super(AssetWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 0, 0, 10)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
#         self.setFixedHeight(60)

        self.asset_name_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.asset_name_layout)
        self.asset_name_label = AssetNameWidget(self, name)
        self.asset_name_label.print_to_console.connect(self.print_to_console)
        self.asset_name_layout.addWidget(self.asset_name_label)
        self.asset_name_label.setObjectName("asset_name_label")
        self.asset_name_label.setFixedHeight(35)
#         self.asset_name_layout.addStretch()

        self.asset_info_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.asset_info_layout)



        self.asset_path_label = QtWidgets.QLabel('jobs/show/assets/barbie/rig')
        self.asset_info_layout.addWidget(self.asset_path_label)
        self.asset_path_label.setObjectName("asset_path_label")
#
#         self.asset_version_label = QtWidgets.QLabel('Version 27/30')
#         self.asset_info_layout.addWidget(self.asset_version_label)
#         self.asset_version_label.setObjectName("asset_version_label")


        self.asset_version_widget = AssetVersionWidget(self)
        self.asset_name_layout.addWidget(self.asset_version_widget)
        self.asset_version_widget.setObjectName("asset_version_widget")
        self.asset_version_widget.setFixedHeight(35)
#         self.asset_name_layout.addStretch()

#         self.main_layout.addStretch()

        self.style_sheet = """

        QLabel#asset_path_label, QLabel#asset_version_label{
            color:#4AC5B3;
            font: bold 14px "Courier New";
            outline:none;
            background-color:transparent;
            border-bottom-right-radius:15;
            border-bottom-left-radius:15;
            padding-left:5;
            padding-right:5;

        }

        """

        self.setStyleSheet(self.style_sheet)

class AssetNameWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent, name=None):
        super(AssetNameWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


        self.asset_name_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.asset_name_layout)
        self.asset_name_button = QtWidgets.QPushButton()
        self.asset_name_button.clicked.connect(self.pick_asset)
        self.asset_name_layout.addWidget(self.asset_name_button)
        self.asset_name_button.setObjectName("asset_name_button")
#         self.asset_name_button.setFixedHeight(30)

        if name:
            self.set_text(name)

        self.style_sheet = """
        QPushButton#asset_name_button{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            border-top-right-radius:15;
            border-top-left-radius:3;
            border-bottom-right-radius:15;
            border-bottom-left-radius:15;
            padding-left:8;
            padding-right:5;
            padding-top:10;
        }

        QPushButton#asset_name_button:hover{
            color:#4AC5B3;
        }

        QPushButton#asset_name_button:pressed{
            color:#273238;
        }

        """
        self.setStyleSheet(self.style_sheet)

    def set_text(self, text):
        self.asset_name_button.setText(text)

    def pick_asset(self):
        self.print_to_console.emit("Pick asset", "#ff6666")


class AssetVersionWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(AssetVersionWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


        self.asset_version_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.asset_version_layout)
        self.asset_version_combo = QtWidgets.QComboBox()
#         self.asset_version_combo.clicked.connect(self.pick_asset)
        self.asset_version_layout.addWidget(self.asset_version_combo)
        self.asset_version_combo.setObjectName("asset_version_combo")
#         self.asset_name_button.setFixedHeight(30)

        self.style_sheet = """
        QComboBox#asset_version_combo{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            border-top-right-radius:15;
            border-top-left-radius:3;
            border-bottom-right-radius:15;
            border-bottom-left-radius:15;
            padding-left:8;
            padding-right:5;
            padding-top:10;
        }

        QComboBox:hover{
            background-color:#4AC5B3;
        }

        QComboBox:pressed{
            color:#273238;
        }


        QComboBox:on {
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 4px;
            background-color:#151515;
            selection-background-color: green;
        }


        QComboBox QAbstractItemView {
            background-color:#171E21;
            color:white;
            border-radius: 0px;
            border-width: 0px;
            selection-background-color: #273238;
            outline:None;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            background-color:transparent;
        }

        QComboBox::down-arrow {
            background-color:transparent;
            padding-right:0;
        }


        QComboBox::down-arrow:on,
        QComboBox::down-arrow:hover,
        QComboBox::down-arrow:focus {
             background-color:transparent;
        }


         QScrollBar:vertical {
             border: 0px solid grey;
             background: #171E21;
             margin: 20px 0px 20px 0;
         }
         QScrollBar::handle:vertical {
             background: #273238;
             min-height: 10px;
             margin-top:2px;
             margin-bottom:2px;

         }
         QScrollBar::add-line:vertical {
             border: 0px solid grey;
             border-bottom-right-radius:2;
             border-bottom-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: bottom;
             subcontrol-origin: margin;
         }

         QScrollBar::sub-line:vertical {
             border: 0px solid grey;
             border-top-right-radius:2;
             border-top-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: top;
             subcontrol-origin: margin;
         }
         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
             border: 0px solid grey;
             width: 3px;
             height: 3px;
             background: transparent;
         }

         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
             background: none;

         }


        """
        self.setStyleSheet(self.style_sheet)

        self.populate()

    def populate(self):

        for i in range(1,27):

            tool_tip_string = """Version {}
Added arm twist joints,
adjusted weights and updated textures.""".format(i)

            self.asset_version_combo.addItem(str(i))
            self.asset_version_combo.setItemData(i-1,
tool_tip_string,QtCore.Qt.ToolTipRole);

        self.asset_version_combo.setCurrentIndex(24)



class PickerWidget(QtWidgets.QFrame):

    def __init__(self, parent):
        super(PickerWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        self.setMinimumHeight(50)

        self.style_sheet = """
        QFrame{
            background-color:#273238;
            margin-left:10;
            border-radius:5;

        }

        QLabel{
            color:#ffffff;
            font: 14px "Courier New";
            outline:none;
            background-color:transparent;
        }
        """

        self.setStyleSheet(self.style_sheet)

        self.label = QtWidgets.QLabel("Picker")
        self.main_layout.addWidget(self.label)
        self.hide()

    def toggle_visibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()


class TreeWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(TreeWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.style_sheet = """
        QTreeWidget, QTreeWidget:focus{
            color:#ffffff;
            alternate-background-color: #273238;
            font: 15px "Courier New";
            outline:none;
        }

        QTreeWidget::item{
            background-color:transparent;
            border-style:none;
            border-width:0px;
            outline:none;
            padding-top:0;
            height:22;
            }

        QTreeWidget::item:selected{
            background-color:#171E21;
            border-style:none;
            border-width:0px;
            outline:none;
            }

        QTreeWidget::item:disabled{
            background-color:transparent;
            color:#777;
            border-style:none;
            border-width:0px;
            outline:none;
            }

        /*
        QTreeView::branch {
                background-color: transparent;
                border-color:blue;
        }
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings{
            border-image: none;
            image: none;
        }

        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings  {
            border-image: none;
            image: none;
        }
        */

        QPushButton, QPushButton:focus{
            background-color:transparent;
            color:#ffffff;
            font: 30px;
            border-style: none;
            border-width: 0px;
            outline: none;
        }

        QPushButton:pressed{
            background-color:transparent;
            color:#aaaaaa;
            font: 30px;
            border-style: none;
            border-width: 0px;
            outline: none;
        }


         QScrollBar:vertical {
             border: 0px solid grey;
             background: #171E21;
             margin: 20px 0px 20px 0;
         }
         QScrollBar::handle:vertical {
             background: #273238;
             min-height: 20px;
             margin-top:2px;
             margin-bottom:2px;

         }
         QScrollBar::add-line:vertical {
             border: 0px solid grey;
             border-bottom-right-radius:2;
             border-bottom-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: bottom;
             subcontrol-origin: margin;
         }

         QScrollBar::sub-line:vertical {
             border: 0px solid grey;
             border-top-right-radius:2;
             border-top-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: top;
             subcontrol-origin: margin;
         }
         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
             border: 0px solid grey;
             width: 3px;
             height: 3px;
             background: transparent;
         }

         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
             background: none;

         }

         QCheckBox{
             border:0px None white;
             background-color:transparent;
         }

         QCheckBox:indicator{
            width:16;
            height:16;
            background-color:transparent;
         }


         QCheckBox:indicator:checked{
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/invisible_light_icon&16.png");
            background-repeat:None;
            background-position: centre;
         }

         QCheckBox:indicator:unchecked{
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/eye_icon&16.png");
            background-repeat:None;
            background-position: centre;
         }

        QLabel#blank{
            background-color:transparent;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }
        QLabel#finished{
            background-color:transparent;
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/checkmark_icon&16.png");
            background-repeat:None;
            background-position: bottom;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }
        QLabel#warning{
            background-color:transparent;
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/attention_icon&16.png");
            background-repeat:None;
            background-position: bottom;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }
        QLabel#errored{
            background-color:transparent;
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/delete_icon&16.png");
            background-repeat:None;
            background-position: bottom;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }

        """

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(5, 5, 0, 0)
        self.main_layout.addLayout(self.header_layout)

#         self.picker_button = QtWidgets.QPushButton("+")
#         self.picker_button.setFixedSize(30,30)
#         self.header_layout.addWidget(self.picker_button)
#         self.header_layout.addStretch()
#
#         self.picker_widget = PickerWidget(self)
#         self.main_layout.addWidget(self.picker_widget)
#         self.picker_button.clicked.connect(self.picker_widget.toggle_visibility)

        self.tree_layout = QtWidgets.QVBoxLayout()
        self.tree_layout.setContentsMargins(10, 10, 0, 0)
        self.tree_layout.setSpacing(0)

        self.main_layout.addLayout(self.tree_layout)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.itemClicked.connect(self.item_selected)

        self.tree_layout.addWidget(self.tree)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.header().hide()
        self.tree.setUniformRowHeights(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tree.setColumnWidth(1, 25)
        self.tree.setColumnWidth(2, 25)

        self.setStyleSheet(self.style_sheet)

        self.debug_populate()



    def item_selected(self, item):
        self.print_to_console.emit("{} selected".format(item.text(0)),
"#4AC5B3")
        self.print_to_console.emit("self.select(\"{}\")".format(item.text(0)),
"#ffffff")



    def debug_populate(self):

        items = []

        setup = TreeItem(self.tree, ["setup"])
        skeleton = TreeItem(setup, ["skeleton"])
        geometry = TreeItem(setup, ["geometry"])
        anim = TreeItem(geometry, ["anim"])
        render = TreeItem(geometry, ["render"])
        tech = TreeItem(geometry, ["tech"])
        kinematics = TreeItem(setup, ["kinematics"])
        head = TreeItem(kinematics, ["head"])
        spine = TreeItem(kinematics, ["spine"])
        limbs = TreeItem(kinematics, ["limbs"])
        legs = TreeItem(limbs, ["legs"])
        left_leg = TreeItem(legs, ["left"])
        right_leg = TreeItem(legs, ["right"])
        arms = TreeItem(limbs, ["arms"])
        left_arm = TreeItem(arms, ["left"])
        right_arm = TreeItem(arms, ["right"])
        spaces = TreeItem(setup, ["spaces"])
        deformation = TreeItem(setup, ["deformation"])
        skincluster = TreeItem(deformation, ["skincluster"])
        checks = TreeItem(setup, ["checks"])
        publish = TreeItem(setup, ["publish"])

        items.extend([setup, skeleton, geometry, anim,
                      render, tech, kinematics, head,
                      spine, limbs, legs, left_leg,
                      right_leg, arms, left_arm,
                      right_arm, spaces, deformation, skincluster,
                      checks, publish])


        setup.setExpanded(True)
        geometry.setExpanded(True)
        kinematics.setExpanded(True)
        limbs.setExpanded(True)
        legs.setExpanded(True)
        arms.setExpanded(True)
        deformation.setExpanded(True)


        setup.status_label.setObjectName("finished")
        setup.status_label.setToolTip("Finished in 00:03:00")

        skeleton.status_label.setObjectName("finished")
        skeleton.status_label.setToolTip("Finished in 00:03:00")

        geometry.status_label.setObjectName("finished")
        geometry.status_label.setToolTip("Finished in 00:03:00")

        anim.status_label.setObjectName("warning")
        anim.status_label.setToolTip("Finished in 00:03:00\nWarning: There is a problem with the flux capacitor")

        render.status_label.setObjectName("finished")
        render.status_label.setToolTip("Finished in 00:03:00")

        tech.status_label.setObjectName("finished")
        tech.status_label.setToolTip("Finished in 00:03:00")

        kinematics.status_label.setObjectName("finished")
        kinematics.status_label.setToolTip("Finished in 00:03:00")

        head.status_label.setObjectName("errored")
        head.status_label.setToolTip("Errored")

        for item in items:
            item.visibility_checkbox.stateChanged.connect(partial(self.disable_tree,
item, item.visibility_checkbox.isChecked()))

    def disable_tree(self, parent, state):
        if parent.isDisabled():
            parent.setDisabled(False)
        else:
            parent.setDisabled(True)



class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args):
        #self.element = kwargs.pop('element', None)
        super(TreeItem, self).__init__(*args)



        self.setText(0, args[1][0])
        self.setToolTip(0, "{0}\nC:/dev/dir/{0}".format(args[1][0]))
        icon = QtWidgets.QIcon("/jobs/generic/dev/chris-g/dev/cc/white/png/shapes_icon&16.png")
        self.setIcon(0, icon)

        self.visibility_checkbox = QtWidgets.QCheckBox() # button...
        self.treeWidget().setItemWidget(self, 1,
self.visibility_checkbox) # ...goes to the third column


        self.status_label = QtWidgets.QLabel() # button...
        self.status_label.setObjectName("blank")
        self.treeWidget().setItemWidget(self, 2, self.status_label) # ...goes to the third column
#         self.setDisabled(True)


    def event(self, event):
        print ("Test")
        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Tab):
            print ("tafsdasd")
            return True
        return True



class ConsoleWidget(QtWidgets.QFrame):
    INPUT_HISTORY=[]
    HISTORY=[]
    CURRENT_SEARCH_INDEX = 0
    def __init__(self, parent):
        super(ConsoleWidget, self).__init__(parent)



        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.toolbar_layout = QtWidgets.QHBoxLayout()
        self.toolbar_layout.setContentsMargins(5, 5, 5, 5)
        self.toolbar_layout.setSpacing(0)
        self.main_layout.addLayout(self.toolbar_layout)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.toolbar_layout.addWidget(self.clear_button)

        self.toolbar_layout.addStretch()


        self.return_text = QtWidgets.QTextEdit()
        self.return_text.setReadOnly(True)
        self.main_layout.addWidget(self.return_text)

        self.input_text = QtWidgets.QLineEdit("console input")
        self.main_layout.addWidget(self.input_text)
        self.input_text.returnPressed.connect(self.run_input)

        self.clear_button.pressed.connect(self.return_text.clear)



        self.style_sheet = """
        QPushButton{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/playback_play_icon&24.png");
            background-repeat:None;
            background-position: top;
            border-radius:3;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:30;
            padding-left:5;
            padding-right:5;
            text-align:centre;
            margin-top:15;
        }

        QPushButton:hover{
            background-color:#4B5761;

        }

        QPushButton:pressed{
            font: 11px "Courier New";
            outline:none;
            background-color:#273238;
            border-color:#363F46;

        }
        """

        self.setStyleSheet(self.style_sheet)

    def build_pressed(self):
        self.print_to_console.emit("Building...", "#66ff66")



class ExtractButtonWidget(QtWidgets.QWidget):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(ExtractButtonWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 10, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
#         self.setFixedSize(90,70)

        self.build_button = QtWidgets.QPushButton("Extract")
        self.build_button.setFixedHeight(60)
        self.build_button.setFixedWidth(60)

        self.build_button.clicked.connect(self.extract_pressed)

        self.main_layout.addWidget(self.build_button)

        self.style_sheet = """
        QPushButton{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/download_icon&24.png");
            background-repeat:None;
            background-position: top;
            border-radius:3;
            border-color:#ffffff;
            border-style: solid;
            border-width: 0;
            padding-top:30;
            padding-left:5;
            padding-right:5;
            text-align:centre;
            margin-top:15;
        }

        QPushButton:hover{
            background-color:#4B5761;

        }

        QPushButton:pressed{
            font: 11px "Courier New";
            outline:none;
            background-color:#273238;
            border-color:#363F46;

        }
        """

        self.setStyleSheet(self.style_sheet)

    def extract_pressed(self):
        self.print_to_console.emit("Extracting...", "#aaaaff")



class AssetWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)
    def __init__(self, parent, name):
        super(AssetWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 0, 0, 10)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
#         self.setFixedHeight(60)

        self.asset_name_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.asset_name_layout)
        self.asset_name_label = AssetNameWidget(self, name)
        self.asset_name_label.print_to_console.connect(self.print_to_console)
        self.asset_name_layout.addWidget(self.asset_name_label)
        self.asset_name_label.setObjectName("asset_name_label")
        self.asset_name_label.setFixedHeight(35)
#         self.asset_name_layout.addStretch()

        self.asset_info_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.asset_info_layout)



        self.asset_path_label = QtWidgets.QLabel('jobs/show/assets/barbie/rig')
        self.asset_info_layout.addWidget(self.asset_path_label)
        self.asset_path_label.setObjectName("asset_path_label")
#
#         self.asset_version_label = QtWidgets.QLabel('Version 27/30')
#         self.asset_info_layout.addWidget(self.asset_version_label)
#         self.asset_version_label.setObjectName("asset_version_label")


        self.asset_version_widget = AssetVersionWidget(self)
        self.asset_name_layout.addWidget(self.asset_version_widget)
        self.asset_version_widget.setObjectName("asset_version_widget")
        self.asset_version_widget.setFixedHeight(35)
#         self.asset_name_layout.addStretch()

#         self.main_layout.addStretch()

        self.style_sheet = """

        QLabel#asset_path_label, QLabel#asset_version_label{
            color:#4AC5B3;
            font: bold 14px "Courier New";
            outline:none;
            background-color:transparent;
            border-bottom-right-radius:15;
            border-bottom-left-radius:15;
            padding-left:5;
            padding-right:5;

        }

        """

        self.setStyleSheet(self.style_sheet)

class AssetNameWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent, name=None):
        super(AssetNameWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


        self.asset_name_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.asset_name_layout)
        self.asset_name_button = QtWidgets.QPushButton()
        self.asset_name_button.clicked.connect(self.pick_asset)
        self.asset_name_layout.addWidget(self.asset_name_button)
        self.asset_name_button.setObjectName("asset_name_button")
#         self.asset_name_button.setFixedHeight(30)

        if name:
            self.set_text(name)

        self.style_sheet = """
        QPushButton#asset_name_button{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            border-top-right-radius:15;
            border-top-left-radius:3;
            border-bottom-right-radius:15;
            border-bottom-left-radius:15;
            padding-left:8;
            padding-right:5;
            padding-top:10;
        }

        QPushButton#asset_name_button:hover{
            color:#4AC5B3;
        }

        QPushButton#asset_name_button:pressed{
            color:#273238;
        }

        """
        self.setStyleSheet(self.style_sheet)

    def set_text(self, text):
        self.asset_name_button.setText(text)

    def pick_asset(self):
        self.print_to_console.emit("Pick asset", "#ff6666")


class AssetVersionWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(AssetVersionWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


        self.asset_version_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.asset_version_layout)
        self.asset_version_combo = QtWidgets.QComboBox()
#         self.asset_version_combo.clicked.connect(self.pick_asset)
        self.asset_version_layout.addWidget(self.asset_version_combo)
        self.asset_version_combo.setObjectName("asset_version_combo")
#         self.asset_name_button.setFixedHeight(30)

        self.style_sheet = """
        QComboBox#asset_version_combo{
            color:#ffffff;
            font: 15px "Courier New";
            outline:none;
            background-color:transparent;
            border-top-right-radius:15;
            border-top-left-radius:3;
            border-bottom-right-radius:15;
            border-bottom-left-radius:15;
            padding-left:8;
            padding-right:5;
            padding-top:10;
        }

        QComboBox:hover{
            background-color:#4AC5B3;
        }

        QComboBox:pressed{
            color:#273238;
        }


        QComboBox:on {
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 4px;
            background-color:#151515;
            selection-background-color: green;
        }


        QComboBox QAbstractItemView {
            background-color:#171E21;
            color:white;
            border-radius: 0px;
            border-width: 0px;
            selection-background-color: #273238;
            outline:None;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            background-color:transparent;
        }

        QComboBox::down-arrow {
            background-color:transparent;
            padding-right:0;
        }


        QComboBox::down-arrow:on,
        QComboBox::down-arrow:hover,
        QComboBox::down-arrow:focus {
             background-color:transparent;
        }


         QScrollBar:vertical {
             border: 0px solid grey;
             background: #171E21;
             margin: 20px 0px 20px 0;
         }
         QScrollBar::handle:vertical {
             background: #273238;
             min-height: 10px;
             margin-top:2px;
             margin-bottom:2px;

         }
         QScrollBar::add-line:vertical {
             border: 0px solid grey;
             border-bottom-right-radius:2;
             border-bottom-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: bottom;
             subcontrol-origin: margin;
         }

         QScrollBar::sub-line:vertical {
             border: 0px solid grey;
             border-top-right-radius:2;
             border-top-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: top;
             subcontrol-origin: margin;
         }
         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
             border: 0px solid grey;
             width: 3px;
             height: 3px;
             background: transparent;
         }

         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
             background: none;

         }


        """
        self.setStyleSheet(self.style_sheet)

        self.populate()

    def populate(self):

        for i in range(1,27):

            tool_tip_string = """Version {}
Added arm twist joints,
adjusted weights and updated textures.""".format(i)

            self.asset_version_combo.addItem(str(i))
            self.asset_version_combo.setItemData(i-1,
tool_tip_string,QtCore.Qt.ToolTipRole);

        self.asset_version_combo.setCurrentIndex(24)



class PickerWidget(QtWidgets.QFrame):

    def __init__(self, parent):
        super(PickerWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        self.setMinimumHeight(50)

        self.style_sheet = """
        QFrame{
            background-color:#273238;
            margin-left:10;
            border-radius:5;

        }

        QLabel{
            color:#ffffff;
            font: 14px "Courier New";
            outline:none;
            background-color:transparent;
        }
        """

        self.setStyleSheet(self.style_sheet)

        self.label = QtWidgets.QLabel("Picker")
        self.main_layout.addWidget(self.label)
        self.hide()

    def toggle_visibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()


class TreeWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super(TreeWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.style_sheet = """
        QTreeWidget, QTreeWidget:focus{
            color:#ffffff;
            alternate-background-color: #273238;
            font: 15px "Courier New";
            outline:none;
        }

        QTreeWidget::item{
            background-color:transparent;
            border-style:none;
            border-width:0px;
            outline:none;
            padding-top:0;
            height:22;
            }

        QTreeWidget::item:selected{
            background-color:#171E21;
            border-style:none;
            border-width:0px;
            outline:none;
            }

        QTreeWidget::item:disabled{
            background-color:transparent;
            color:#777;
            border-style:none;
            border-width:0px;
            outline:none;
            }

        /*
        QTreeView::branch {
                background-color: transparent;
                border-color:blue;
        }
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings{
            border-image: none;
            image: none;
        }

        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings  {
            border-image: none;
            image: none;
        }
        */

        QPushButton, QPushButton:focus{
            background-color:transparent;
            color:#ffffff;
            font: 30px;
            border-style: none;
            border-width: 0px;
            outline: none;
        }

        QPushButton:pressed{
            background-color:transparent;
            color:#aaaaaa;
            font: 30px;
            border-style: none;
            border-width: 0px;
            outline: none;
        }


         QScrollBar:vertical {
             border: 0px solid grey;
             background: #171E21;
             margin: 20px 0px 20px 0;
         }
         QScrollBar::handle:vertical {
             background: #273238;
             min-height: 20px;
             margin-top:2px;
             margin-bottom:2px;

         }
         QScrollBar::add-line:vertical {
             border: 0px solid grey;
             border-bottom-right-radius:2;
             border-bottom-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: bottom;
             subcontrol-origin: margin;
         }

         QScrollBar::sub-line:vertical {
             border: 0px solid grey;
             border-top-right-radius:2;
             border-top-left-radius:2;
             background: #273238;
             height: 20px;
             subcontrol-position: top;
             subcontrol-origin: margin;
         }
         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
             border: 0px solid grey;
             width: 3px;
             height: 3px;
             background: transparent;
         }

         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
             background: none;

         }

         QCheckBox{
             border:0px None white;
             background-color:transparent;
         }

         QCheckBox:indicator{
            width:16;
            height:16;
            background-color:transparent;
         }


         QCheckBox:indicator:checked{
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/invisible_light_icon&16.png");
            background-repeat:None;
            background-position: centre;
         }

         QCheckBox:indicator:unchecked{
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/eye_icon&16.png");
            background-repeat:None;
            background-position: centre;
         }

        QLabel#blank{
            background-color:transparent;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }
        QLabel#finished{
            background-color:transparent;
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/checkmark_icon&16.png");
            background-repeat:None;
            background-position: bottom;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }
        QLabel#warning{
            background-color:transparent;
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/attention_icon&16.png");
            background-repeat:None;
            background-position: bottom;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }
        QLabel#errored{
            background-color:transparent;
            background-image:url("/jobs/generic/dev/chris-g/dev/cc/white/png/delete_icon&16.png");
            background-repeat:None;
            background-position: bottom;
            width:16;
            height:16;
            padding-top:5;
            margin-bottom:5;
        }

        """

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(5, 5, 0, 0)
        self.main_layout.addLayout(self.header_layout)

#         self.picker_button = QtWidgets.QPushButton("+")
#         self.picker_button.setFixedSize(30,30)
#         self.header_layout.addWidget(self.picker_button)
#         self.header_layout.addStretch()
#
#         self.picker_widget = PickerWidget(self)
#         self.main_layout.addWidget(self.picker_widget)
#         self.picker_button.clicked.connect(self.picker_widget.toggle_visibility)

        self.tree_layout = QtWidgets.QVBoxLayout()
        self.tree_layout.setContentsMargins(10, 10, 0, 0)
        self.tree_layout.setSpacing(0)

        self.main_layout.addLayout(self.tree_layout)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.itemClicked.connect(self.item_selected)

        self.tree_layout.addWidget(self.tree)
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree.header().hide()
        self.tree.setUniformRowHeights(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setStretchLastSection(False)
        self.tree.header().setResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tree.setColumnWidth(1, 25)
        self.tree.setColumnWidth(2, 25)

        self.setStyleSheet(self.style_sheet)

        self.debug_populate()



    def item_selected(self, item):
        self.print_to_console.emit("{} selected".format(item.text(0)),
"#4AC5B3")
        self.print_to_console.emit("self.select(\"{}\")".format(item.text(0)),
"#ffffff")



    def debug_populate(self):

        items = []

        setup = TreeItem(self.tree, ["setup"])
        skeleton = TreeItem(setup, ["skeleton"])
        geometry = TreeItem(setup, ["geometry"])
        anim = TreeItem(geometry, ["anim"])
        render = TreeItem(geometry, ["render"])
        tech = TreeItem(geometry, ["tech"])
        kinematics = TreeItem(setup, ["kinematics"])
        head = TreeItem(kinematics, ["head"])
        spine = TreeItem(kinematics, ["spine"])
        limbs = TreeItem(kinematics, ["limbs"])
        legs = TreeItem(limbs, ["legs"])
        left_leg = TreeItem(legs, ["left"])
        right_leg = TreeItem(legs, ["right"])
        arms = TreeItem(limbs, ["arms"])
        left_arm = TreeItem(arms, ["left"])
        right_arm = TreeItem(arms, ["right"])
        spaces = TreeItem(setup, ["spaces"])
        deformation = TreeItem(setup, ["deformation"])
        skincluster = TreeItem(deformation, ["skincluster"])
        checks = TreeItem(setup, ["checks"])
        publish = TreeItem(setup, ["publish"])

        items.extend([setup, skeleton, geometry, anim,
                      render, tech, kinematics, head,
                      spine, limbs, legs, left_leg,
                      right_leg, arms, left_arm,
                      right_arm, spaces, deformation, skincluster,
                      checks, publish])


        setup.setExpanded(True)
        geometry.setExpanded(True)
        kinematics.setExpanded(True)
        limbs.setExpanded(True)
        legs.setExpanded(True)
        arms.setExpanded(True)
        deformation.setExpanded(True)


        setup.status_label.setObjectName("finished")
        setup.status_label.setToolTip("Finished in 00:03:00")

        skeleton.status_label.setObjectName("finished")
        skeleton.status_label.setToolTip("Finished in 00:03:00")

        geometry.status_label.setObjectName("finished")
        geometry.status_label.setToolTip("Finished in 00:03:00")

        anim.status_label.setObjectName("warning")
        anim.status_label.setToolTip("Finished in 00:03:00\nWarning: There is a problem with the flux capacitor")

        render.status_label.setObjectName("finished")
        render.status_label.setToolTip("Finished in 00:03:00")

        tech.status_label.setObjectName("finished")
        tech.status_label.setToolTip("Finished in 00:03:00")

        kinematics.status_label.setObjectName("finished")
        kinematics.status_label.setToolTip("Finished in 00:03:00")

        head.status_label.setObjectName("errored")
        head.status_label.setToolTip("Errored")

        for item in items:
            item.visibility_checkbox.stateChanged.connect(partial(self.disable_tree,
item, item.visibility_checkbox.isChecked()))

    def disable_tree(self, parent, state):
        if parent.isDisabled():
            parent.setDisabled(False)
        else:
            parent.setDisabled(True)



class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args):
        #self.element = kwargs.pop('element', None)
        super(TreeItem, self).__init__(*args)



        self.setText(0, args[1][0])
        self.setToolTip(0, "{0}\nC:/dev/dir/{0}".format(args[1][0]))
        icon = QtWidgets.QIcon("/jobs/generic/dev/chris-g/dev/cc/white/png/shapes_icon&16.png")
        self.setIcon(0, icon)

        self.visibility_checkbox = QtWidgets.QCheckBox() # button...
        self.treeWidget().setItemWidget(self, 1,
self.visibility_checkbox) # ...goes to the third column


        self.status_label = QtWidgets.QLabel() # button...
        self.status_label.setObjectName("blank")
        self.treeWidget().setItemWidget(self, 2, self.status_label) # ...goes to the third column
#         self.setDisabled(True)


    def event(self, event):
        print ("Test")
        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Tab):
            print ("tafsdasd")
            return True
        return True



class ConsoleWidget(QtWidgets.QFrame):
    INPUT_HISTORY=[]
    HISTORY=[]
    CURRENT_SEARCH_INDEX = 0
    def __init__(self, parent):
        super(ConsoleWidget, self).__init__(parent)



        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.toolbar_layout = QtWidgets.QHBoxLayout()
        self.toolbar_layout.setContentsMargins(5, 5, 5, 5)
        self.toolbar_layout.setSpacing(0)
        self.main_layout.addLayout(self.toolbar_layout)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.toolbar_layout.addWidget(self.clear_button)

        self.toolbar_layout.addStretch()


        self.return_text = QtWidgets.QTextEdit()
        self.return_text.setReadOnly(True)
        self.main_layout.addWidget(self.return_text)

        self.input_text = QtWidgets.QLineEdit("console input")
        self.main_layout.addWidget(self.input_text)
        self.input_text.returnPressed.connect(self.run_input)

        self.clear_button.pressed.connect(self.return_text.clear)



        self.style_sheet = """
        QLineEdit{
            color:#ffffff;
            font: 14px "Courier New";
            outline:none;
            background-color:#171E21;
            border-top-right-radius:0;
            border-top-left-radius:0;
            border-bottom-right-radius:2;
            border-bottom-left-radius:2;
            padding:5;

        }

        QTextEdit{
            color:#ffffff;
            font: 14px "Courier New";
            outline:none;
            background-color:black;
            border-top-right-radius:2;
            border-top-left-radius:2;
            padding:5;

        }

        QPushButton{
            color:#ffffff;
            font: 11px "Courier New";
            outline:none;
            background-color:transparent;
            background-image:
url("/jobs/generic/dev/chris-g/dev/cc/white/png/app_window_shell&16.png");
            background-repeat:None;
            background-position: left;
            padding-left:20;
            padding-top:5;

        }

         QScrollBar:vertical {
             border: 0px solid grey;
             background: #171E21;
             margin: 20px 0px 20px 0;
         }
         QScrollBar::handle:vertical {
             background: #363F46;
             min-height: 20px;
             margin-top:2px;
             margin-bottom:2px;
         }
         QScrollBar::add-line:vertical {
             border: 0px solid grey;
             border-bottom-right-radius:7;
             border-bottom-left-radius:7;
             background: #363F46;
             height: 20px;
             subcontrol-position: bottom;
             subcontrol-origin: margin;
         }

         QScrollBar::sub-line:vertical {
             border: 0px solid grey;
             border-top-right-radius:7;
             border-top-left-radius:7;
             background: #363F46;
             height: 20px;
             subcontrol-position: top;
             subcontrol-origin: margin;
         }
         QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
             border: 0px solid grey;
             width: 3px;
             height: 3px;
             background: transparent;
         }

         QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
             background: none;

         }
        """

        self.setStyleSheet(self.style_sheet)

    def print_to_console(self, text, color=None, icon=None):
        if color:
            text = "<span style=\"color:"+color+";\" >" + text + "</span>"
        self.return_text.append(str(text))
        self.HISTORY.append(text)

    def run_input(self, *args):
        text = str(self.input_text.text())

        if not text:
            return
        try:
            return_text = str(eval(str(text)))
        except Exception as ex:
            return_text = str(ex)

        self.print_to_console(return_text , color="#4AC5B3")
        self.INPUT_HISTORY.append(text)
        self.input_text.clear()
        self.CURRENT_SEARCH_INDEX = 0

    def clear(self):
        self.return_text.clear()

    def keyPressEvent(self, event):
        key = event.key()

        if self.INPUT_HISTORY:
            if key == QtCore.Qt.Key_Up:
                self.CURRENT_SEARCH_INDEX -= 1
                self.input_text.setText(self.INPUT_HISTORY[self.CURRENT_SEARCH_INDEX%len(self.INPUT_HISTORY)])
            elif key == QtCore.Qt.Key_Down:
                self.CURRENT_SEARCH_INDEX += 1

self.input_text.setText(self.INPUT_HISTORY[self.CURRENT_SEARCH_INDEX%len(self.INPUT_HISTORY)])


class AttributeEditorWidget(QtWidgets.QFrame):
    def __init__(self, parent, console):
        super(AttributeEditorWidget, self).__init__(parent)
        self.console = console
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        attr0 = AttributeProxyWidget(self, "location", value="C:/path/path/path/file.abc")
        self.main_layout.addWidget(attr0)
        attr1 = AttributeProxyWidget(self, "parent", value="setup.geometry")
        self.main_layout.addWidget(attr1)
        attr2 = AttributeProxyWidget(self, "namespace", value="")
        self.main_layout.addWidget(attr2)


        self.main_layout.addStretch()

        attr0.print_to_console.connect(self.console.print_to_console)
        attr1.print_to_console.connect(self.console.print_to_console)
        attr2.print_to_console.connect(self.console.print_to_console)




class AttributeProxyWidget(QtWidgets.QFrame):
    print_to_console = QtCore.pyqtSignal(str, str)
    def __init__(self, parent, name, value=0):
        super(AttributeProxyWidget, self).__init__(parent)
        self.name = name
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 0, 0)
        self.main_layout.setSpacing(2)
        self.setLayout(self.main_layout)

        self.name_label = QtWidgets.QLabel(name[0].upper()+name[1:])
        self.main_layout.addWidget(self.name_label)
        self.name_label.setObjectName("name_label")

        self.value_line_edit = QtWidgets.QLineEdit(str(value))
        self.main_layout.addWidget(self.value_line_edit)
        self.value_line_edit.setObjectName("value_line_edit")
        self.value_line_edit.setMinimumHeight(26)

        self.style_sheet = """
        QLabel#name_label{
            color:#4AC5B3;
            font: bold 14px "Courier New";
            outline:none;
            background-color:transparent;
        }

        QLineEdit#value_line_edit{
            color:#ffffff;
            font: 14px "Courier New";
            outline:none;
            background-color:#171E21;
            margin-left:30;
            margin-right:10;
            border-style:none;
            border-width:0px;
            border-top-right-radius:2;
            border-top-left-radius:2;
            border-bottom-right-radius:2;
            border-bottom-left-radius:2;
            padding-left:5;
            padding-right:5;
            padding-top:0;

        }
        """
        self.setStyleSheet(self.style_sheet)

        self.value_line_edit.editingFinished.connect(self.return_pressed)

    def return_pressed(self):
        text = self.value_line_edit.text()
        self.print_to_console.emit("node.{} set to{}".format(self.name, text), "#4AC5B3")
        self.print_to_console.emit("self.setAttr(\"node.{}\",\"{}\")".format(self.name, text), "#ffffff")


class ProgressBarWidget(QtWidgets.QFrame):
    def __init__(self, parent):
        super(ProgressBarWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        self.setFixedHeight(16)

        self.bar_layout = QtWidgets.QHBoxLayout()
        self.bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bar_layout.setSpacing(0)
        self.main_layout.addLayout(self.bar_layout)
        self.style_sheet = """
        QFrame{
        background-color:#171E21;
        border-radius:2;
        }

        QLabel#bar{
            color:#000000;
            font: bold 14px "Courier New";
            outline:none;
            background-color:lightgreen;
            qproperty-alignment: AlignCenter;
            border-top-left-radius:2;
            border-bottom-left-radius:2;
            margin:0;
        }
        """


        self.bar = QtWidgets.QLabel()
        self.bar.setObjectName("bar")
        self.bar_layout.addWidget(self.bar)

        self.spacer = QtWidgets.QLabel()
        self.spacer.setObjectName("spacer")
        self.bar_layout.addWidget(self.spacer)

        self.setStyleSheet(self.style_sheet)

        self.set_percent(20)

    def set_percent(self, percent):

        self.bar_layout.setStretch(0,percent)
        self.bar_layout.setStretch(1,100-percent)

        self.bar.setText("{}%".format(percent))




def Main():
    app = QtWidgets.QApplication(sys.argv)
    main = UI()
    main.show()

    sys.exit(close_all(app, main))


def close_all(app, ui):
    app.exec_()


if __name__ == "__main__":
    Main()