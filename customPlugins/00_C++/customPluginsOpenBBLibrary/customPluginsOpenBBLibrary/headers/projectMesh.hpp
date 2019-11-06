#pragma once

#include <maya/MItGeometry.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPxNode.h>
#include <maya/MFnMesh.h>
#include <maya/MPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MObject.h>
#include <maya/MFnData.h>
#include <maya/MDagPath.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MFloatPoint.h>
#include <maya/MVector.h>
#include <maya/MFloatVector.h>
#include <maya/MFnMeshData.h>
#include <maya/MIntArray.h>
#include <maya/MFnMesh.h>

class projectMesh : public MPxNode
{
public:

	// constructor and deconstructor
						projectMesh();
	virtual				~projectMesh();

	// compute function where in it there will be all the "core" of the node
	virtual MStatus     compute(const MPlug& plug, MDataBlock& data);

	// methods for creating the instance of the node, and initialize all the attributes of the node itself
	static void*		creator();
	static MStatus		initialize();

	// node attributes
	static MObject		aInputSourceMesh;
	static MObject		aInputTargetMesh;
	static MObject		aOutputMesh;

	//static MObject		aBlendWeight;
};