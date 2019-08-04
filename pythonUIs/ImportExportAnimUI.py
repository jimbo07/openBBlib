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
        
    def run(self):
        
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