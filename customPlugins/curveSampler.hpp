#ifndef CURVESAMPLER_H
#define CURVESAMPLER_H

#include <math.h>
#include <maya/MPxNode.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MQuaternion.h>
#include <maya/MIOStream.h>
#include <maya/MEulerRotation.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MArrayDataHandle.h>
#include <maya/MVector.h>

class curveSampler : public MPxNode
{
	public:
				curveSampler();
		virtual ~curveSampler();

		virtual MStatus 	compute(const MPlug& plug, MDataBlock& data);
		static  void* 		creator();
		static  MStatus 	initialize();

	public:
		static	MObject			aInCurve;
		static	MObject			aInUpCurve;
		static	MObject			aInNumSamples;
		static	MObject			aOutRotate;
		static	MObject			aOutRotateX;
		static	MObject			aOutRotateY;
		static	MObject			aOutRotateZ;
		static	MObject			aOutTranslate;
		static	MObject			aOutTranslateX;
		static	MObject			aOutTranslateY;
		static	MObject			aOutTranslateZ;

		static const MTypeId 	typeId;
		static const MString 	typeName;
};

#endif // CURVESAMPLER_H
