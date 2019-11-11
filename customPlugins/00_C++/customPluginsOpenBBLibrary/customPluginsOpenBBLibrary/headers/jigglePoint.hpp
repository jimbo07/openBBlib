#pragma once

#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MTime.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MPxNode.h>
#include <maya/MMatrix.h>
#include <maya/MFloatVector.h>

class jigglePoint : public MPxNode
{
	public:

		// constructor and deconstructor
							jigglePoint();
		virtual				~jigglePoint();

		// deform function where in it there will be all the "core" of the node
		virtual MStatus		compute(
										const MPlug& plug, 
										MDataBlock& data
									);

		// methods for creating the instance of the node, and initialize all the attributes of the node itself
		static void*		creator();
		static MStatus		initialize();

		// node attributes
		static MObject			aOutput;
		static MObject			aJiggleAmount;
		static MObject			aGoal;
		static MObject			aDamping;
		static MObject			aStiffness;
		static MObject			aTime;
		static MObject			aParentInverse;

	private:
		bool DEBUG_MODE = true;
		MPoint currentPosition;
		MPoint previousPosition;
		MTime previousTime;
		bool inputInitialize = false;
};