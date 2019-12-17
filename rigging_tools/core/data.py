'''
Created on 28 Sep 2018

@author: lasse-r
'''
import maya.cmds as cmds

import os.path
import cPickle

class Data( object ):
    ''' Base Data Object Class
        Contains functions to save and load standard rig data.
    '''
    
    def __init__(self):
        ''' Data Object Class Initializer
        '''
        # Initialize Data
        self._data = {}
        
        # Initialize Data Type
        self.dataType = 'Data'
        
        # File Filter
        self.fileFilter = "All Files (*.*)"
    
    def save(self, filePath, force=False):
        ''' Save data object to file.
        :param filePath str: Target file path.
        :param force bool: Force save if file already exists. (Overwrite).
        '''
        # Check Directory Path
        dirpath = os.path.dirname(filePath)
        if not os.path.isdir(dirpath): os.makedirs(dirpath)
        
        # Check File Path
        if os.path.isfile(filePath) and not force:
            raise Exception('File {0} already exists! Use "force=True" to overwrite the existing file.'.format(filePath))
        
        # Save File
        fileOut = open(filePath, 'wb')
        cPickle.dump(self, fileOut)
        fileOut.close()
        
        # Print Message
        print("Saved {0}: {1}".format(self.__class__.__name__, filePath))
        
        # Return Result
        return filePath
    
    def saveAs(self):
        ''' Save data object to file.
            Opens a file dialog, to allow the user to specify a file path. 
        '''
        # Specify File Path
        filePath = cmds.fileDialog2(fileFilter=self.fileFilter,
                                    dialogStyle=2,
                                    fileMode=0,
                                    caption='Save As')
        
        # Check Path
        if not filePath: return
        filePath = filePath[0]
        
        # Save Data File
        filePath = self.save(filePath,force=True)
        
        # Return Result
        return filePath
    
    def load(self, filePath=''):
        ''' Load data object from file.
        :param filePath str: Target file path
        '''
        # Check File Path
        if not filePath:
            filePath = cmds.fileDialog2(fileFilter=self.fileFilter,
                                        dialogStyle=2,
                                        fileMode=1,
                                        caption='Load Data File',
                                        okCaption='Load')
            
            if not filePath: return None
            filePath = filePath[0]
            
        else:
            if not os.path.isfile(filePath):
                raise Exception('File "'+filePath+'" does not exist!')
        
        # Open File
        fileIn = open(filePath, 'rb')
        dataIn = cPickle.load(fileIn)
        
        # Print Message
        dataType = dataIn.__class__.__name__
        print("Loaded {0}: {1}".format(dataType, filePath))
        
        # Return Result
        return dataIn
    
    def reset(self):
        '''
        Reset data object
        '''
        self.__init__()
        
        
