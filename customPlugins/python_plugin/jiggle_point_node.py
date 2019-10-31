import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import math
VERSION = '1.0'
DEBUG_MODE = False

## @brief A node that triggers shapes from of an orientation
class JigglePoint(OpenMayaMPx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0x00001234)

    # attribte of the node
    aOutput = OpenMaya.MObject()
    aGoal = OpenMaya.MObject()
    aDamping = OpenMaya.MObject()
    aStiffness = OpenMaya.MObject()
    aTime = OpenMaya.MObject()
    aParentInverse = OpenMaya.MObject()
    aJiggleAmount = OpenMaya.MObject

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

        # creating an initialize flag variable which able us to check if the node it's been initialize yet, and if don't do it
        self._initialize = False

        # basic vaiable for computing te math
        self._current_position = OpenMaya.MPoint()
        self._previous_position = OpenMaya.MPoint()
        self._previous_time = OpenMaya.MTime()


    # the compute function get called once one or more attributes of the node have been changed 
    def compute(self, plug, data):
        if plug != JigglePoint.aOutput:
            return OpenMaya.kUnknownParameter

        # Get thi inputs
        damping = data.inputValue(self.aDamping).asFloat()
        stiffness = data.inputValue(self.aStiffness).asFloat()
        goal = OpenMaya.MPoint(data.inputValue(self.aGoal).asFloatVector())
        current_time = data.inputValue(self.aTime).asTime()
        parent_inverse = data.inputValue(self.aParentInverse).asMatrix()
        jiggle_amount = data.inputValue(self.aJiggleAmount).asFloat()

        # check for the inilize state of the comuting/node
        if not self._initialize:
            self._previous_time = current_time
            self._current_position = goal
            self._previous_position = goal
            self._initialize = True

        # calculating the time difference --- if the timestep is just 1 frame we want a stable simulation
        time_difference = current_time.value() - self._previous_time.value()
        if time_difference > 1.0 or time_difference < 0.0:
            self._initialize = False
            self._previous_time = current_time
            data.setClean(plug)
            return

        # calculating the velocity vector
        velocity = (self._current_position - self._previous_position) * (1.0 - damping)
        # calculating the new positio point
        new_position = self._current_position + velocity
        # updating the final result with the stuffness factor
        goal_force = (goal - new_position) * stiffness
        new_position += goal_force

        # store the state of the next computation
        self._previous_position = OpenMaya.MPoint(self._current_position)
        self._current_position = OpenMaya.MPoint(new_position)
        self._previous_time = OpenMaya.MTime(current_time)

        # involving the jiggle amount factor
        new_position = goal + ((new_position - goal) * jiggle_amount)

        if DEBUG_MODE:
            print new_position.x
            print new_position.y
            print new_position.z

        # caculatin the new position in the local space of the object which is affected
        new_position *= parent_inverse

        # give the final result to aOutput attribute that has been created before (output of our node)
        hOutput = data.outputValue(JigglePoint.aOutput)
        out_vector = OpenMaya.MFloatVector(new_position.x, new_position.y, new_position.z)
        hOutput.setMFloatVector(out_vector)
        hOutput.setClean()
        data.setClean(plug)


## @brief Creates the object for Maya.
def creator():
    return OpenMayaMPx.asMPxPtr(JigglePoint())


## @brief Creates the node attributes.
#
def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()

    # setting up the node attributes
    JigglePoint.aOutput = nAttr.createPoint('output', 'out')
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    JigglePoint.addAttribute(JigglePoint.aOutput)
    
    JigglePoint.aGoal = nAttr.createPoint('goal', 'goal')
    JigglePoint.addAttribute(JigglePoint.aGoal)
    JigglePoint.attributeAffects(JigglePoint.aGoal, JigglePoint.aOutput)

    JigglePoint.aJiggleAmount = nAttr.create('jiggleAmount', 'jiggleAmount', OpenMaya.MFnNumericData.kFloat, 0.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JigglePoint.addAttribute(JigglePoint.aJiggleAmount)
    JigglePoint.attributeAffects(JigglePoint.aJiggleAmount, JigglePoint.aOutput)

    JigglePoint.aDamping = nAttr.create('damping', 'damping', OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JigglePoint.addAttribute(JigglePoint.aDamping)
    JigglePoint.attributeAffects(JigglePoint.aDamping, JigglePoint.aOutput)

    JigglePoint.aStiffness = nAttr.create('stiffness', 'stiffness', OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JigglePoint.addAttribute(JigglePoint.aStiffness)
    JigglePoint.attributeAffects(JigglePoint.aStiffness, JigglePoint.aOutput)

    # creating the time attribute
    JigglePoint.aTime = uAttr.create('time', 'time',  OpenMaya.MFnUnitAttribute.kTime, 0.0)
    JigglePoint.addAttribute(JigglePoint.aTime)
    JigglePoint.attributeAffects(JigglePoint.aTime, JigglePoint.aOutput)

    # creating the matrix handle variable
    JigglePoint.aParentInverse = mAttr.create('parentInverse', 'parentInverse')
    JigglePoint.addAttribute(JigglePoint.aParentInverse)


## @brief Initializes the plug-in in Maya.
#
def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, 'fabio-f', VERSION, 'Any')
    plugin.registerNode('jigglePoint', JigglePoint.kPluginNodeId, creator, initialize)


## @brief Uninitializes the plug-in in Maya.
#
def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    plugin.deregisterNode(JigglePoint.kPluginNodeId)

