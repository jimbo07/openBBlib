from maya import cmds
import uuid

class ImportExportAnim():
    def __init__(self, name = "", environments_attrs = {}):
        self.name = name
        self.id = uuid.uuid1()
        self.environments_attrs =  environments_attrs
        
    def get_name_ui(self):
        print("UI class name: {}".format(self.name))
        return self.name

    def set_name_ui(self, new_name_ui):
        self.name = new_name_ui
        print("New UI class name: {}".format(self.name))
        return self.name

    def get_environments_attrs_ui(self):
        print("UI class environments vars: {}".format(self.environments_attrs))
        return self.environments_attrs

    def set_environments_attrs_ui(self, new_envs):
        self.environments_attrs = new_envs
        print("New UI class environments vars: {}".format(self.environments_attrs))
        return self.environments_attrs
        
    def get_id_ui(self):
        print("UI class id: {}".format(self.id))
        return self.id
        
    def run(self, title_ui):
        
        if cmds.window(self.name, exists=True):
            cmds.deleteUI(self.name)
        
        #create the main window
        main_window = cmds.window(self.name, title=title_ui, sizeable=True)
        
        # create first main buttons
        main_layout = cmds.rowColumnLayout(numberOfRows=2)
        main_buttons = cmds.rowColumnLayout(numberOfColumns=3, parent=main_layout)
        cmds.button(label='Check Directory', backgroundColor=[0.243, 0.8, 0.792], parent=main_buttons)
        cmds.button(label='Directory Path', backgroundColor=[0.235, 0.709, 0.188], parent=main_buttons)
        cmds.button(label='Create Directory', backgroundColor=[0.972, 0.478, 0.086], parent=main_buttons)
        cmds.setParent( '..' )
        
        #tab layout
        form = cmds.formLayout()
        tabs = cmds.tabLayout(innerMarginWidth=20, innerMarginHeight=20)
        cmds.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)), parent=main_layout )
        
        import_layout = cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(label='Import', parent=import_layout)
        cmds.setParent( '..' )
        
        export_layout = cmds.rowColumnLayout(numberOfRows=4)
        # type of export
        type_export_layout = cmds.rowColumnLayout(numberOfColumns=3, columnSpacing=((2, 10), (3, 20)))
        cmds.text(label='Type of Export:', align='right', parent=type_export_layout)
        cmds.radioCollection(parent=type_export_layout)
        cmds.radioButton(label='Latest')
        cmds.radioButton(label='Custom')
        cmds.setParent( '..' )
        
        # textfield for file
        file_export_layout = cmds.rowColumnLayout(numberOfColumns=2, columnSpacing=(2, 10))
        file_label = cmds.text(label='File:',  align='right', parent=file_export_layout)
        file_txt_field = cmds.textField(parent=file_export_layout)
        cmds.setParent( '..' )
        
        # type of selection
        type_sel_export_layout = cmds.rowColumnLayout(numberOfColumns=3, columnSpacing=(2, 10))
        cmds.text(label='Hierarchy:', align='right', parent=type_sel_export_layout)
        cmds.radioCollection(parent=type_sel_export_layout)
        cmds.radioButton(label='All')
        cmds.radioButton(label='Selected')
        cmds.setParent( '..' )
        
        # operation tab button
        button_export_layout = cmds.rowColumnLayout(numberOfColumns=1, columnSpacing=(2, 10))
        cmds.button(label='Export',  parent=button_export_layout)
        
        
        # build the tabs layout
        cmds.tabLayout( tabs, edit=True, tabLabel=((import_layout, 'import'), (export_layout, 'export')))
        
        #tabs import Export
        
        # Display the window
        cmds.showWindow()
        return 0
    
if __name__ == '__main__':
    envs = {
        "main_dir" : "something/something/",
        "file_name" : "something.anim"
    }
    main_ui = ImportExportAnim("MainUI", envs)
    name_ui = main_ui.get_name_ui()
    envs_ui = main_ui.get_environments_attrs_ui()
    id_ui = main_ui.get_id_ui()
    
    main_ui.run("Import Export Animation")