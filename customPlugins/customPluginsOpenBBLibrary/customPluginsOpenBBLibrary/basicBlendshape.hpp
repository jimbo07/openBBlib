#pragma once

#include <maya/MItGeometry.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPxDeformerNode.h>
#include <maya/MFnMesh.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MObject.h>

class basicBlendshape : public MPxDeformerNode
{
public:

	// constructor and deconstructor
	basicBlendshape();
	virtual				~basicBlendshape();

	// deform function where in it there will be all the "core" of the node
	virtual MStatus		deform(MDataBlock& data,
		MItGeometry& itGeo,
		const MMatrix& localToWorldMatrix,
		unsigned int geomIndex);

	// methods for creating the instance of the node, and initialize all the attributes of the node itself
	static void*		creator();
	static MStatus		initialize();

	// node attributes
	static MObject		aBlendMesh;
	//static MObject		aBlendWeight;
};