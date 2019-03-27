#pragma once

#include <maya/MPxNode.h>
#include <maya/MObject.h>
#include <maya/MMatrix.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MVector.h>
#include <maya/MFloatMatrix.h>
#include <math.h>
#include <iostream>

class simpleParentConstraint : public MPxNode
{
public:
						simpleParentConstraint();
	virtual				~simpleParentConstraint();

	static void*		creator();
	static  MStatus		initialize();
	virtual MStatus     compute(const MPlug& plug, MDataBlock& data);

	static MObject		aMantainOffset;

	static	MObject		aInParentWorldMatrix;
	static	MObject		aInParentWorldInverseMatrix;
	static	MObject		aInTargetWorldMatrix;
	static	MObject		aInTargetWorldInverseMatrix;

	static	MObject		aOutTranslate;
	static	MObject		aOutTranslateX;
	static	MObject		aOutTranslateY;
	static	MObject		aOutTranslateZ;

	static	MObject		aOutRotate;
	static	MObject		aOutRotateX;
	static	MObject		aOutRotateY;
	static	MObject		aOutRotateZ;

	static	MObject		aOutScale;
	static	MObject		aOutScaleX;
	static	MObject		aOutScaleY;
	static	MObject		aOutScaleZ;

};