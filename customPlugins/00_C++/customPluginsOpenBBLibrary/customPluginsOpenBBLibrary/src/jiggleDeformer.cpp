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
MObject jiggleDeformer::aPerGeometry;
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

	return MS::kSuccess;
}

// initialize method for al the attribute fo the node
extern "C" MStatus jiggleDeformer::initialize()
{
	MStatus status;
	MFnMatrixAttribute mAttr;
	MFnNumericAttribute nAttr;
	MFnUnitAttribute uAttr;
	MFnCompoundAttribute cAttr;
	
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

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer weights");
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer jiggleMap");
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer stiffnessMap");
	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer jiggleDeformer dampingMap");
	
	return MS::kSuccess;
}