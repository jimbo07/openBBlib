#include "jiggleDeformer.hpp"

// class attributes

// constructor and deconstructor function for the main class jiggleDeformer
jiggleDeformer::jiggleDeformer() {};
jiggleDeformer::~jiggleDeformer() {};

// creator method for retrieving the instance of the object jiggleDeformer
extern "C" void* jiggleDeformer::creator()
{
	return new jiggleDeformer();
}

// initialize method for al the attribute fo the node
extern "C" MStatus jiggleDeformer::initialize()
{
	MStatus status;

	return MS::kSuccess;
}

// deform method where the deformation is actually computed
extern "C" MStatus jiggleDeformer::deform(MDataBlock& data, MItGeometry& itGeo, const MMatrix& localToWorldMatrix, unsigned int geomIndex)
{
	MStatus status;

	return MS::kSuccess;
}