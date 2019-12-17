try:
    from maya import cmds, mel
except ImportError:
    import traceback
    traceback.print_exc()


class RigLoc():

    def __init__(self, name=None):
        self.name = name
        self.locator = None  
      
    def get_name(self):
        return self.name
        
    def set_name(self, name):
        self.name = name

    def get_locator(self):
        return self.locator
        
    def set_locator(self, loc_str):
        self.locator = loc_str
    
    def add_separator(self, name_sep='', by_name=False):
        if not by_name:
            cmds.addAttr(self.locator, longName=name_sep, attributeType='enum', enumName="------------:")
            cmds.setAttr(self.locator+"."+name_sep, channelBox=True, keyable=False)
        else:
            cmds.addAttr(self.name, longName=name_sep, attributeType='enum', enumName="------------:")
            cmds.setAttr(self.name+"."+name_sep, channelBox=True, keyable=False)

    def create_rigloc(self):
        loc = cmds.spaceLocator(name=self.name)
        self.locator = loc[0]
        for chb_attr in ['t', 'r', 's']:
            for axis in ['x', 'y', 'z']:
                cmds.setAttr(self.locator+"."+chb_attr+axis, lock=True, keyable=False, channelBox=False)

    # vector attr
    def add_vector_attr(self, name_attr, keyable=True, lock=False):
        if name_attr != None:
            # adding the attribute
            cmds.addAttr(self.locator, longName=name_attr, attributeType='double3')
            cmds.addAttr(self.locator, longName=name_attr+"X", attributeType='double', parent=name_attr)
            cmds.addAttr(self.locator, longName=name_attr+"Y", attributeType='double', parent=name_attr)
            cmds.addAttr(self.locator, longName=name_attr+"Z", attributeType='double', parent=name_attr)
            # set the attributes just added
            cmds.setAttr(self.locator+"."+name_attr+"X", keyable=keyable, lock=lock)
            cmds.setAttr(self.locator+"."+name_attr+"Y", keyable=keyable, lock=lock)
            cmds.setAttr(self.locator+"."+name_attr+"Z", keyable=keyable, lock=lock)
        else:
            cmds.warning("You should declare a #--- Name ---# for the attribute you want to add to the rig_loc")
    # integer attr   
    def add_integer_attr(self, name_attr, min_val=None, max_val=None, def_val=0, keyable=True, lock=False):
        if name_attr != None:
            if min_val != None and max_val != None:
                if min_val > def_val or max_val < def_val:
                    cmds.warning("MinumValue or MaximumValue are not compatible with DefaultValue which is set as default to 0, change them or give to the DefaultValue another number")
                else:
                    cmds.addAttr(self.locator, longName=name_attr, attributeType='long', minValue=min_val, maxValue=max_val, defaultValue=def_val)
                    cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
            else:
                cmds.addAttr(self.locator, longName=name_attr, attributeType='long', defaultValue=def_val)
                cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
        else:
            cmds.warning("You should declare a #--- Name ---# for the attribute you want to add to the rig_loc")        
    
    # string attr    
    def add_string_attr(self, name_attr, keyable=True, lock=False):
        if name_attr != None:
            cmds.addAttr(self.locator, longName=name_attr, attributeType='string')
            cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
        else:
            cmds.warning("You should declare a #--- Name ---# for the attribute you want to add to the rig_loc") 
                    
    # float attr    
    def add_float_attr(self, name_attr, min_val=None, max_val=None, def_val=0, keyable=True, lock=False):
        if name_attr != None:
            if min_val != None and max_val != None:
                if min_val > def_val or max_val < def_val:
                    cmds.warning("MinumValue or MaximumValue are not compatible with DefaultValue which is set as default to 0, change them or give to the DefaultValue another number")
                else:
                    cmds.addAttr(self.locator, longName=name_attr, attributeType='double', minValue=min_val, maxValue=max_val, defaultValue=def_val)
                    cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
            else:
                cmds.addAttr(self.locator, longName=name_attr, attributeType='double', defaultValue=def_val)
                cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
        else:
            cmds.warning("You should declare a #--- Name ---# for the attribute you want to add to the rig_loc") 

    # boolean attr   
    def add_boolean_attr(self, name_attr, keyable=True, lock=False):
        if name_attr != None:
            cmds.addAttr(self.locator, longName=name_attr, attributeType='bool')
            cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
        else:
            cmds.warning("You should declare a #--- Name ---# for the attribute you want to add to the rig_loc")
                
    # enum attr    
    def add_enum_attr(self, name_attr, enum_values, skeyable=True, lock=False):
        if name_attr != None:
            if enum_values != None or enum_values != '':
                cmds.addAttr(self.locator, longName=name_attr, attributeType='enum', enumName=enum_values)
                cmds.setAttr(self.locator+"."+name_attr, keyable=keyable, lock=lock)
            else:
                cmds.warning("You should declare the enum values you want to put inside the attribute")
        else:
            cmds.warning("You should declare a #--- Name ---# for the attribute you want to add to the rig_loc")
    
    def add_attribute(self, name, type, def_val=0, enum_val=None, min_val=None, max_val=None, keyable=True, lock=False):
        switcher =  {
                    'vector' : self.add_vector_attr(name, keyable, lock),
                    'integer' : self.add_integer_attr(name, def_val, min_val, max_val, keyable, lock),
                    'string' : self.add_string_attr(name, keyable, lock),
                    'float' : self.add_float_attr(name, def_val, min_val, max_val, keyable, lock),
                    'bool' : self.add_boolean_attr(name, keyable, lock),
                    'enum' : self.add_enum_attr(name, enum_val, keyable, lock)
                   }
        func = switcher.get(type, 'Invalid type of attribute')
        return func()

    def run(self):
        from maya import cmds
        
        if cmds.objExists(self.name):
            cmds.warning("rig_loc already exist! It'll add just the attribute separator")
            if cmds.attributeQuery("attributes", node=self.name, exists=True):
                cmds.warning("rig_loc already has the attributes separator")
            else:
                self.add_separator("attributes", True)
        else:
            self.create_rigloc()
            self.add_separator("attributes")
