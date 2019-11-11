#include "jigglePoint.hpp"

// class attributes
MObject	jigglePoint::aOutput;
MObject	jigglePoint::aJiggleAmount;
MObject	jigglePoint::aGoal;
MObject	jigglePoint::aDamping;
MObject	jigglePoint::aStiffness;
MObject	jigglePoint::aTime;
MObject	jigglePoint::aParentInverse;

// constructor and deconstructor function for the main class jigglePoint
jigglePoint::jigglePoint() {};
jigglePoint::~jigglePoint() {};

// creator method for retrieving the instance of the object jigglePoint
extern "C" void* jigglePoint::creator()
{
	return new jigglePoint();
}

// deform method where the deformation is actually computed
extern "C" MStatus jigglePoint::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	if (plug != aOutput)
	{
		return MS::kUnknownParameter;
	}
	else
	{
		float jiggleAmount = data.inputValue(aJiggleAmount).asFloat();
		MPoint goal = MPoint(data.inputValue(aGoal).asFloatVector());
		float damping = data.inputValue(aDamping).asFloat();
		float stiffness = data.inputValue(aStiffness).asFloat();
		MTime currentTime = data.inputValue(aTime).asTime();
		MMatrix parentInverseMatrix = data.inputValue(aParentInverse).asMatrix();

		if (!inputInitialize)
		{
			previousTime = currentTime;
			previousPosition = goal;
			currentPosition = goal;
			inputInitialize = true;

		}

		double timeDifference = currentTime.value() - previousTime.value();
		if (timeDifference > 1.0f || timeDifference < 0.0f)
		{
			inputInitialize = false;
			previousTime = currentTime;
			data.setClean(plug);
			return MS::kSuccess;
		}

		MVector velocity = (currentPosition - previousPosition) * (1.0 - damping);
		MPoint newPosition = currentPosition + velocity;
		if (DEBUG_MODE)
			std::cout << "New Position: [" << newPosition.x << ", " << newPosition.y << ", " << newPosition.z << "]" << std::endl;

		MPoint goalForce = (goal - newPosition) * stiffness;
		newPosition += goalForce;

		previousPosition = currentPosition;
		currentPosition = newPosition;
		previousTime = currentTime;

		newPosition = goal + ((newPosition - goal) * jiggleAmount);
		newPosition *= parentInverseMatrix;

		MDataHandle hOutput = data.outputValue(aOutput);
		MFloatVector outVector(newPosition.x, newPosition.y, newPosition.z);
		hOutput.setMFloatVector(outVector);
		hOutput.setClean();
		data.setClean(plug);

		return MS::kSuccess;
	}
}

// initialize method for al the attribute fo the node
extern "C" MStatus jigglePoint::initialize()
{
	MStatus status;

	// Types of attributes
	MFnNumericAttribute nAttr;
	MFnMatrixAttribute mAttr;
	MFnUnitAttribute uAttr;

	// add attributes to the actual node (creating the plugs)
	aOutput = nAttr.createPoint("output", "output");
	nAttr.setWritable(false);
	nAttr.setStorable(false);
	addAttribute(aOutput);

	aJiggleAmount = nAttr.create("jiggleAmount", "jiggleAmount", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0f);
	nAttr.setMax(1.0f);
	addAttribute(aJiggleAmount);
	attributeAffects(aJiggleAmount, aOutput);

	aGoal = nAttr.createPoint("goal", "goal");
	addAttribute(aGoal);
	attributeAffects(aGoal, aOutput);

	aDamping = nAttr.create("damping", "damping", MFnNumericData::kFloat, 0.5f);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0f);
	nAttr.setMax(1.0f);
	addAttribute(aDamping);
	attributeAffects(aDamping, aOutput);

	aStiffness = nAttr.create("stiffness", "stiffness", MFnNumericData::kFloat, 0.5f);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0f);
	nAttr.setMax(1.0f);
	addAttribute(aStiffness);
	attributeAffects(aStiffness, aOutput);

	aTime = uAttr.create("time", "time", MFnUnitAttribute::kTime, 0.0);
	addAttribute(aTime);
	attributeAffects(aTime, aOutput);

	aParentInverse = mAttr.create("parentInverseMatrix", "parentInverseMatrix");
	addAttribute(aParentInverse);
	attributeAffects(aParentInverse, aOutput);

	return MS::kSuccess;
}