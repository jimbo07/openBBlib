#include "simpleBlendshape.hpp"

MObject simpleBlendshape::aBlendMesh;
//MObject simpleBlendshape::aBlendWeight;

// constructor and deconstructor function for the main class simpleBlendshape
simpleBlendshape::simpleBlendshape() {};
simpleBlendshape::~simpleBlendshape() {};

// creator method for retrieving the instance of the object simpleBlendshape
extern "C" void* simpleBlendshape::creator()
{
	return new simpleBlendshape();
}

// initialize method for al the attribute fo the node
extern "C" MStatus simpleBlendshape::initialize()
{
	MStatus status;
	
	MFnTypedAttribute tAttr;
	//MFnNumericAttribute nAttr;
	
	aBlendMesh = tAttr.create("blendMesh", "bldMsh", MFnData::kMesh);
	addAttribute(aBlendMesh);
	attributeAffects(aBlendMesh, outputGeom);
	/*
	aBlendWeight = nAttr.create("blendValue", "bldVal", MFnNumericData::kFloat);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);
	nAttr.setMax(1.0);
	addAttribute(aBlendWeight);
	attributeAffects(aBlendWeight, outputGeom);
	*/
	return MS::kSuccess;
}

// deform method where the deformation is actually computed
extern "C" MStatus simpleBlendshape::deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex)
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
	/*
	// get the weightPoints from the input mesh
	MDataHandle blendWeightData = data.inputValue(aBlendWeight, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	float blendWeight = blendWeightData.asFloat();
	*/
	// set the variable where we can store the vertex position of the input geometry
	MPoint point;

	// this is the part of the code which is dedicted to the algorithm logic and the deformation
	for ( ; !itGeo.isDone(); itGeo.next())
	{
		point = itGeo.position();

		point += (blendPoints[itGeo.index()] - point) /** blendWeight*/ * env;

		itGeo.setPosition(point);
	}


	return MS::kSuccess;
}