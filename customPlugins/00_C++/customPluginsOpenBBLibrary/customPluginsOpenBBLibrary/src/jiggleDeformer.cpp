#include "jiggleDeformer.hpp"

// MTypeId jiggleDeformer::id;
MObject jiggleDeformer::aTime;
MObject jiggleDeformer::aDirectionBias;
MObject jiggleDeformer::aNormalStrength;
MObject jiggleDeformer::aScale;
MObject jiggleDeformer::aMaxVelocity;
MObject jiggleDeformer::aStartFrame;
MObject jiggleDeformer::aDampingMagnitude;
MObject jiggleDeformer::aStiffnessMagnitude;
MObject jiggleDeformer::aJiggleMap;
MObject jiggleDeformer::aStiffnessMap;
MObject jiggleDeformer::aDampingMap;
// MObject jiggleDeformer::aPerGeometry;
MObject jiggleDeformer::aInBaseMesh;
MObject jiggleDeformer::aWorldMatrix;

// constructor and deconstructor function for the main class basicBlendshape
jiggleDeformer::jiggleDeformer() {};
jiggleDeformer::~jiggleDeformer() {};

// creator method for retrieving the instance of the object basicBlendshape
extern "C" void* jiggleDeformer::creator()
{
	return new jiggleDeformer();
}

// deform method where the deformation is actually computed
extern "C" MStatus jiggleDeformer::deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex)
{
	MStatus status;

	MTime currentTime = data.inputValue(aTime).asTime();
	MPointArray points;
	itGeo.allPositions(points);
	float env = data.inputValue(envelope).asFloat();
	float dampingMagnitude = data.inputValue(aDampingMagnitude).asFloat();
	float stiffnessMagnitude = data.inputValue(aStiffnessMagnitude).asFloat();
	float scale = data.inputValue(aScale).asFloat();
	float maxVelocity = data.inputValue(aMaxVelocity).asFloat() * scale;
	MMatrix worldToLocalMatrix = localToWorldMatrix.inverse();
	int startFrame = data.inputValue(aStartFrame).asInt();

	MPointArray currentPoints = jiggleDeformer::currentPoints_;
	MPointArray previousPoints = jiggleDeformer::previousPoints_;
	MTime previousTime = jiggleDeformer::previousTime_;

	// Initialize the point states
	if (!initialized_)
	{
		previousTime = currentTime;
		initialized_ = true;
		currentPoints.setLength(itGeo.count());
		previousPoints.setLength(itGeo.count());
		for (unsigned int i = 0; i < points.length(); i++)
		{
			currentPoints[i] = points[i] * localToWorldMatrix;
			previousPoints[i] = currentPoints[i];
		}
	}

	// Check if the timestep is just 1 frame since we want a stable simulation
	double timeDifference = currentTime.value() - previousTime.value();
	if (timeDifference > 1.0f || timeDifference < 0.0f || currentTime.value() <= startFrame)
	{
		initialized_ = false;
		previousTime = currentTime;
		return MS::kSuccess;
	}

	// get the geometry from the output one
	MDataHandle hGeo = data.inputValue(outputGeom);
	MMatrix matrixGeo = hGeo.child(aWorldMatrix).asMatrix();

	// store the paint maps into local variable (passing reference)
	MFloatArray weights = jiggleDeformer::weights_;
	MFloatArray jiggleMap = jiggleDeformer::jiggleMap_;
	MFloatArray stiffnessMap = jiggleDeformer::stiffnessMap_;
	MFloatArray dampingMap = jiggleDeformer::dampingMap_;
	// MIntArray& membership = membership_;

	// Get the actual values from paint maps
	jiggleMap.setLength(itGeo.count());
	stiffnessMap.setLength(itGeo.count());
	dampingMap.setLength(itGeo.count());
	weights.setLength(itGeo.count());
	// membership.setLength(itGeo.count());

	// get data handle from maps
	MDataHandle hJiggleMap = data.inputValue(aJiggleMap);
	MDataHandle hStiffnessMap = data.inputValue(aStiffnessMap);
	MDataHandle hDampingMap = data.inputValue(aDampingMap);
	jiggleMap = hJiggleMap.asFloat();
	stiffnessMap = hStiffnessMap.asFloat();
	dampingMap = hDampingMap.asFloat();

	// get real value from maps data handle
	for (; !itGeo.isDone(); itGeo.next())
	{
		weights = weightValue(data, geomIndex, itGeo.index());
	}

	MPoint goal, newPos;
	MVector velocity, goalForce, displacement;
	float damping, stiffness;
	double normalDot;

	for (int i = 0; i < (int)points.length(); ++i) {
		// Calculate goal position
		goal = points[i] * localToWorldMatrix;

		// Calculate damping coefficient
		damping = dampingMagnitude * dampingMap[i];

		// Calculate stiffness coefficient
		stiffness = stiffnessMagnitude * stiffnessMap[i];

		// Offset the point by the velocity
		velocity = (currentPoints[i] - previousPoints[i]) * (1.0f - damping);
		newPos = currentPoints[i] + velocity;
		// Attract the point back to the goal
		goalForce = (goal - newPos) * stiffness;
		newPos += goalForce;

		// Clamp to the max displacement 
		displacement = newPos - goal;
		if (displacement.length() > maxVelocity) {
			displacement = displacement.normal() * maxVelocity;
			newPos = goal + displacement;
		}

		// Store the previous points
		previousPoints[i] = currentPoints[i];
		currentPoints[i] = newPos;

		// Multiply by weight map and envelope
		points[i] += ((newPos * worldToLocalMatrix) - points[i]) * weights[i] * env * jiggleMap[i];
	}

	itGeo.setAllPositions(points);
	previousTime = currentTime;

	return MS::kSuccess;
}

// initialize method for al the attribute fo the node
extern "C" MStatus jiggleDeformer::initialize()
{
	MStatus status;
	MFnMatrixAttribute mAttr;
	MFnNumericAttribute nAttr;
	MFnUnitAttribute uAttr;
	// MFnCompoundAttribute cAttr;
	MFnTypedAttribute tAttr;

	aTime = uAttr.create("time", "time", MFnUnitAttribute::kTime, 0.0);
	addAttribute(aTime);
	attributeAffects(aTime, outputGeom);

	aStartFrame = nAttr.create("startFrame", "startFrame", MFnNumericData::kInt, 0, &status);
	nAttr.setKeyable(true);
	addAttribute(aStartFrame);
	attributeAffects(aStartFrame, outputGeom);

	aScale = nAttr.create("scale", "scale", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setKeyable(true);
	addAttribute(aScale);
	attributeAffects(aScale, outputGeom);

	aDirectionBias = nAttr.create("directionBias", "directionBias", MFnNumericData::kFloat, 0.0, &status);
	nAttr.setMin(-1.0);
	nAttr.setMax(1.0);
	nAttr.setKeyable(true);
	addAttribute(aDirectionBias);
	attributeAffects(aDirectionBias, outputGeom);

	aNormalStrength = nAttr.create("normalStrength", "normalStrength", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setKeyable(true);
	addAttribute(aNormalStrength);
	attributeAffects(aNormalStrength, outputGeom);

	aMaxVelocity = nAttr.create("maxVelocity", "maxVelocity", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setKeyable(true);
	addAttribute(aMaxVelocity);
	attributeAffects(aMaxVelocity, outputGeom);

	aStiffnessMagnitude = nAttr.create("stiffness", "stiffness", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setKeyable(true);
	addAttribute(aStiffnessMagnitude);
	attributeAffects(aStiffnessMagnitude, outputGeom);

	aDampingMagnitude = nAttr.create("damping", "damping", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setKeyable(true);
	addAttribute(aDampingMagnitude);
	attributeAffects(aDampingMagnitude, outputGeom);

	aWorldMatrix = mAttr.create("worldMatrix", "worldMatrix");

	aJiggleMap = nAttr.create("jiggleMap", "jiggleMap", MFnNumericData::kFloat, 0.0, &status);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder(true);

	aStiffnessMap = nAttr.create("stiffnessMap", "stiffnessMap", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder(true);

	aDampingMap = nAttr.create("dampingMap", "dampingMap", MFnNumericData::kFloat, 1.0, &status);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	nAttr.setArray(true);
	nAttr.setUsesArrayDataBuilder(true);

	/*
	aPerGeometry = cAttr.create("perGeometry", "perGeometry", &status);
	cAttr.setArray(true);
	cAttr.addChild(aWorldMatrix);
	cAttr.addChild(aJiggleMap);
	cAttr.addChild(aDampingMap);
	cAttr.addChild(aStiffnessMap);
	cAttr.setUsesArrayDataBuilder(true);
	addAttribute(aPerGeometry);
	attributeAffects(aWorldMatrix, outputGeom);
	attributeAffects(aJiggleMap, outputGeom);
	attributeAffects(aStiffnessMap, outputGeom);
	attributeAffects(aDampingMap, outputGeom);
	*/
	//MFnNumericAttribute nAttr;

	aInBaseMesh = tAttr.create("inBaseMesh", "inBaseMesh", MFnData::kMesh);
	addAttribute(aInBaseMesh);
	attributeAffects(aInBaseMesh, outputGeom);

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer weights");
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer jiggleMap");
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer stiffnessMap");
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer dampingMap");
	
	return MS::kSuccess;
}