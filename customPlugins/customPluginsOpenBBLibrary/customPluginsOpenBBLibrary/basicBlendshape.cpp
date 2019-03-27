#include "basicBlendshape.hpp"

MObject basicBlendshape::aBlendMesh;

// constructor and deconstructor function for the main class basicBlendshape
basicBlendshape::basicBlendshape() {};
basicBlendshape::~basicBlendshape() {};

// creator method for retrieving the instance of the object basicBlendshape
extern "C" void* basicBlendshape::creator()
{
	return new basicBlendshape();
}

// initialize method for al the attribute fo the node
extern "C" MStatus basicBlendshape::initialize()
{
	MStatus status;

	MFnTypedAttribute tAttr;
	//MFnNumericAttribute nAttr;

	aBlendMesh = tAttr.create("blendMesh", "bldMsh", MFnData::kMesh);
	addAttribute(aBlendMesh);
	attributeAffects(aBlendMesh, outputGeom);

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer basicBlendshape weights;");

	return MS::kSuccess;
}

// deform method where the deformation is actually computed
extern "C" MStatus basicBlendshape::deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex)
{
	MStatus status;

	// this pass it will retrieve the data from te dataBlock which it will be use after
	MDataHandle hBlendMesh = data.inputValue(aBlendMesh, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// it will use the mesh provide by the dataHandle above, and we will use it as a mesh retrieving the information as an MObject
	MObject oBlendMesh = hBlendMesh.asMesh();

	// this is the check if what we have passed to the node/attribute is actually a mesh and not something different
	if (oBlendMesh.isNull())
		return MS::kSuccess;

	// we will get the mesh taken previously and pass it to an MfnMesh which is the object that can able us to manipulate the mesh got before
	MFnMesh fnMesh(oBlendMesh, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// at this point we need to store the point position of our blendMesh
	MPointArray blendPoints;
	fnMesh.getPoints(blendPoints);

	// get the envelope attribute from the dataBlock
	MDataHandle envData = data.inputValue(envelope, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	float env = envData.asFloat();

	// set the variable where we can store the vertex position of the input geometry
	MPoint point;

	// set variable for weights
	float weights;

	// this is the part of the code which is dedicted to the algorithm logic and the deformation
	for (; !itGeo.isDone(); itGeo.next())
	{
		point = itGeo.position();
		// retrieving the weights information from both geometryIndex and dataBlock, and it will be iterate for each point
		weights = weightValue(data, geomIndex, itGeo.index());

		// calculation done for each point
		point += (blendPoints[itGeo.index()] - point) * weights * env;

		itGeo.setPosition(point);
	}


	return MS::kSuccess;
}