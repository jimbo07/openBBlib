import maya.cmds as cmds


class Tag():
    """Adds or removes tags to specified target.
    
    Example:
        Adding:
            from jm_maya.rig.util import tag
            reload(tag)
            
            test = tag.Tag()
            test.target = "joint1"
            test.tagType = ["test"]
            test.add()
        Removing:
            from jm_maya.rig.util import tag
            reload(tag)
            
            test = tag.Tag()
            test.target = "joint1"
            test.tagType = ["test"]
            test.remove()
    
    Attributes:
        tagType (list, optional): List of items to be added to the tag
        target (str): Target node for the operation. This must have a value.
        tagName (str, optional): The master tag name. 
        
    """
    
    def __init__(self, tagType=[""], target=None, tagName="default"):
        """Initialize default values
        
        Note:
            All global attributes should be specified here for an easy overview.
        
        """
        self.tagType = tagType
        self.target = target
        self.tagName = tagName
        
    def add(self, replace=0, unique=0):
        """Add tags
        
        Args:
            replace (bool): If True, the current data on the target attribute (if exists) will be replaced.
            unique (bool): Filters the tagType list and removes any duplicates. Uses set so order is not kept.
        
        """
        if self.target:
            if cmds.objExists(self.target):
                if cmds.attributeQuery(self.tagName, node=self.target, ex=1):
                    if replace:
                        data = self.tagType 
                        if unique:
                            data = list(set(data))
                            
                        dataString = None
                        for i in data:
                            if dataString:
                                dataString = "{0},{1}".format(dataString, i)
                            else:
                                dataString = i
                                    
                        self._setStrAttr(self.target, self.tagName, dataString)
                    else:
                        data = self._read(self.target, self.tagName)         
                        for tag in self.tagType:
                            data = "{0},{1}".format(data, tag)
            
                        data = data.split(",")
                        if unique: data = list(set(data))
                        
                        dataString = None
                        for i in data:
                            if dataString:
                                dataString = "{0},{1}".format(dataString, i)
                            else:
                                dataString = i       
                            
                        self._setStrAttr(self.target, self.tagName, dataString)
            
                else:
                    self._addStrAttr(self.target, self.tagName)
                    
                    dataString = None
                    for i in self.tagType:
                        if dataString:
                            dataString = "{0},{1}".format(dataString, i)
                        else:
                            dataString = i
                    
                    self._setStrAttr(self.target, self.tagName, dataString)
            else:
                print "Failed to tag {0}, target does not exist!\n".format(self.target)
        else:
            raise ValueError("No target specified for tagging. Aborting...")
        
    def remove(self, delAttr=0):
        """Remove tags
        
        Args:
            delAttr (bool): Defines whether or not to remove the attribute entirely
            
        """
        if self.target:
            if allTags:
                if cmds.attributeQuery(self.tagName, node=self.target, ex=1):
                    cmds.setAttr("{0}.{1}".format(self.target, self.tagName), l=0)
                    cmds.deleteAttr(self.target, at=self.tagName)
            
            else:
                data = self._read(self.target, self.tagName)
                
                data = data.split(",")
                data = [x for x in data if x not in self.tagType]
                
                dataString = None
                for i in data:
                    if dataString:
                        dataString = "{0},{1}".format(dataString, i)
                    else:
                        dataString = i
                if not dataString:
                    dataString = ""
                    
                self._setStrAttr(self.target, self.tagName, dataString)
        else:
            raise ValueError("No target specified for tagging. Aborting...")  
    
    def _read(self, node, name, prnt=0):
        """Read and return tags
        
        Args:
            node (str): The target node the attribute should be added to.
            name (str): The attribute name
            prnt (bool): Toggle printing the attributes to console
        
        Returns:
            data (str): This will be a string read from specified string attribute
            
        """
        data = ""
        if cmds.attributeQuery(name, node=node, ex=1):
            data = cmds.getAttr("{0}.{1}".format(node, name))
        
        if prnt:
            self._print(node, name, data)
        
        return data
    
    def _print(self, node, name, data):
        """Prints whatever data you input
        
        Args:
            node (str): The node name
            name (str): The attribute name
            data (str): This is what gets printed
            
        """
        if data:
            data = data.split(",")
            if len(data):
                print "==\nData for {0}:\nTag = {1}:\n".format(node, name)
                for i in data:
                    print "{0}".format(i)
                print "=="
            else:
                print "==\nData for {0}:\nTag {1}:\n{2}\n==".format(node, name, data)
                
    def _returnDict(self, name, node="", topNode=""):
        """Creates a dictionary
        
        Args:
            name (str): The tagname to look for
            node (str, optional): If specified, only generate dict for this target. Overwrites topNode
            topNode (str, optional): If specified, generates a dict using structure specified in note
        
        Note:
            Uses the structure as follows:
            {
            key (topNode):
                {
                keyValue1A (node):
                    {
                    keyValue2A (attribute):
                        {
                        value1A (string value),
                        value1B (string value)
                        }
                    }
                keyValue1B (node):
                    {
                    keyValue2B (attribute):
                        {
                        value2A (string value),
                        value2B (string value)
                        }
                    }                
                }
            }
            Where string value is a string seperated by commas (,)
            
        """
        if name:
            if node:
                data = self._read(node, name)
                data = data.split(",")
                
                topDict = {
                    node:
                        {
                        name:data
                        }    
                    }
                        
                return topDict
            
            elif topNode:
                lvl1Dict = {
                    topNode:{}
                    }
                data = self._getList(name, topNode)
                
                dataSplit = []
                for i in data:
                    dataString = self._read(i, name)
                    dataSplit = dataString.split(',')
                
                    if type(dataSplit) == list:
                        lvl2Dict = {
                            name:dataSplit
                            }
                    else:
                        lvl2Dict = {
                            name:[dataString]}
                    lvl1Dict[topNode][i] = lvl2Dict
                    
                return lvl1Dict               

    def _addStrAttr(self, node, name):
        """Create new string attribute
        
        Args:
            node (str): The target node the attribute should be added to.
            name (str): The attribute name
            
        """
        attrType = "string"

        if attrType == "string":
            cmds.addAttr(node, dt=attrType, ln=name)
            cmds.setAttr("{0}.{1}".format(node, name), l=1)
    
    def _setStrAttr(self, node, name, data):
        """Set string data
        
        Note:
            The data arg should always be supplied as a string, ie. "1,2,3,4".
        
        Args:
            node (str): The target node the attribute should be set on
            name (str): The attribute name
            data (str): The string to be added to the attribute
            
        """
        attrType = "string"
        if cmds.attributeQuery(name, node=node, ex=1):
            cmds.setAttr("{0}.{1}".format(node, name), l=0)
            cmds.setAttr("{0}.{1}".format(node, name), data, type=attrType)
            cmds.setAttr("{0}.{1}".format(node, name), l=1)

    def _getList(self, tagName, topNode=""):
        """Generate a list of objects with specified tagName (under topNode if specified)
        
        Attrs:
            tagName (str): Attribute to look for, ie. "connectID".
            topNode (str, optional): If specified, return value will only be items under
                the topNodes hierarchy.
                
        """
        if tagName:
            if topNode: data = [topNode] + cmds.listRelatives(topNode, ad=1, typ="transform")
            else: data = cmds.ls("*")

            filteredData = []
            for i in data:
                if cmds.attributeQuery(tagName, node=i, ex=1):
                    filteredData = filteredData + [i]
            
            return filteredData
        else:
            raise ValueError("No tag name specified!")
            
    def _batchAdd(self):
        """
        """
        print "something"
    
    def _batchRemove(self):
        """
        """
        print "something"

    
def depthDict(d):
    """Returns the depth of a nested dictionary
    
    Note:
        This is a recursive function, use with care
    
    Args:
        d (dict): Returns the depth of the dictionary specified as d
        
    """
    if isinstance(d, dict):
        return 1 + (max(map(depthDict, d.values())) if d else 0)
    return 0
    

def printDict(d, lvl=0):
    """Prints every key and value in supplied dictionary
    
    Args:
        d (dict): Prints this dictionary
        lvl (int): Defines the current level of depth, used for indentation
        
    """
    for k, v in d.iteritems():
        print '{0}{1}'.format(lvl * '\t', k)
        if type(v) == dict:
            printDict(v, lvl + 1)
        elif type(v) == list:
            for i in v:
                print "{0}{1}".format((lvl * '\t') + '\t', i)


def compareDict(d1, d2, ns=0, d1ns=None, d2ns=None):
    """Compare dictionary A (d1) with dictionary B (d2)
    
    Args:
        d1 (dict): First dictionary
        d2 (dict): Second dictionary
        ns (bool): Account for namespaces
        d1ns (str, optional): Only replace this namespace in dictionary 1
        d2ns (str, optional): Only replace this namespace in dictionary 2
    
    Returns:
        added (set): These keys were not present in d1, but was in d2
        removed (set): These keys were present in d1, but not in d2
        modified (set): These keys were present in both, but the values were different
        same (set): These keys and their values are the same in both dictionaries
        
    """
    if ns:
        # Finds and replaces all keys that contains namespaces
        if d1ns: d1 = {x.replace(d1ns, ""): d1[x] for x in d1.keys()}
        else: d1 = {x.split(":")[-1]: d1[x] for x in d1.keys()}
        if d2ns: d2 = {x.replace(d2ns, ""): d2[x] for x in d2.keys()}
        else: d2 = {x.split(":")[-1]: d2[x] for x in d2.keys()}
    
    d1Keys = set(d1.keys())
    d2Keys = set(d2.keys())

    intersectKeys = d1Keys.intersection(d2Keys)
    added = d1Keys - d2Keys
    removed = d2Keys - d1Keys
    modified = {o : (d1[o], d2[o]) for o in intersectKeys if d1[o] != d2[o]}
    same = set(o for o in intersectKeys if d1[o] == d2[o])
    return added, removed, modified, same


def mergeDict(x, y):
    """Combines dictioniary x and y
    
    Args:
        x (dict): Dictionary X
        y (dict): Dictionary Y
        
    Return:
        z (dict): Updated dictionary
    """
    z = x.copy()
    z.update(y)
    return z


def removeKeyDict(k, d):
    """Removes key (k) from dictionary (d) if key exists in dictionary
    
    Args:
        k (str): Key to look for
        d (dict): Dictionary to look in
        
    Return:
        x (dict): New dictionary with key removed
        d (dict): Old dictionary, untouched
        
    """
    x = d.copy()
    # if second arg is not given, this will return KeyError if the key isn't found)
    x.pop(k, None)
    
    return x, d

