#pragma once

#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MTime.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnPlugin.h>
#include <maya/MPxNode.h>
#include <maya/MMatrix.h>
#include <maya/MFloatVector.h>
#include <maya/MPxDeformerNode.h>

class jiggleDeformer : public MPxDeformerNode
{
public:

	// constructor and deconstructor
						jiggleDeformer();
	virtual				~jiggleDeformer();

	// deform function where in it there will be all the "core" of the node
	virtual MStatus		deform(MDataBlock& data,
		MItGeometry& itGeo,
		const MMatrix& localToWorldMatrix,
		unsigned int geomIndex);

	// methods for creating the instance of the node, and initialize all the attributes of the node itself
	static void*		creator();
	static MStatus		initialize();

	// node attributes
	
	//static MObject		aBlendWeight;
};