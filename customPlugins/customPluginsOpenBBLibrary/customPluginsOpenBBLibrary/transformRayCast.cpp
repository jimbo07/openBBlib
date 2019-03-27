#include "transformRayCast.hpp"
#include <iostream>

// ---------- DECLARATION OF NODE VARIABLES/ATTRIBUTES -------- //
MObject transformRayCast::aInputTransformWorldMatrix;
MObject transformRayCast::aInputTargetMesh;
MObject transformRayCast::aOutputTransformMatrix;
MObject transformRayCast::outTranslate;
MObject transformRayCast::outTranslateX;
MObject transformRayCast::outTranslateY;
MObject transformRayCast::outTranslateZ;

// ---------- CONSTRUCTOR/DECOSTRUCTOR ---------- //
transformRayCast::transformRayCast() {};
transformRayCast::~transformRayCast() {};

// ---------- CREATOR METHOD ----------//
extern "C" void* transformRayCast::creator()
{
	return new transformRayCast();
}

// ---------- INITIALIZE INPUTS AND OUTPUTS ----------//
extern "C" MStatus transformRayCast::initialize()
{
	MStatus status;

	MFnTypedAttribute tAttr;
	MFnMatrixAttribute mAttr;
	MFnNumericAttribute nAttr;

	aInputTransformWorldMatrix = mAttr.create("sourceTrasformWorldMatrix", "iSTWM");
	mAttr.setConnectable(true);
	addAttribute(aInputTransformWorldMatrix);

	aInputTargetMesh = tAttr.create("targetMesh", "iTM", MFnData::kMesh);
	tAttr.setArray(true);
	tAttr.setUsesArrayDataBuilder(true);
	addAttribute(aInputTargetMesh);

	aOutputTransformMatrix = mAttr.create("outputTrasformWorldMatrix", "oTWM");
	addAttribute(aOutputTransformMatrix);

	outTranslateX = nAttr.create("translateX", "otX", MFnNumericData::kDouble, 0.0);
	outTranslateY = nAttr.create("translateY", "otY", MFnNumericData::kDouble, 0.0);
	outTranslateZ = nAttr.create("translateZ", "otZ", MFnNumericData::kDouble, 0.0);
	outTranslate = nAttr.create("translate", "ot", outTranslateX, outTranslateY, outTranslateZ);
	addAttribute(outTranslate);

	attributeAffects(aInputTransformWorldMatrix, aOutputTransformMatrix);
	attributeAffects(aInputTargetMesh, aOutputTransformMatrix);
	attributeAffects(aInputTransformWorldMatrix, outTranslate);
	attributeAffects(aInputTargetMesh, outTranslate);


	return MS::kSuccess;
}

MStatus transformRayCast::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	if (plug == aOutputTransformMatrix)
	{
		MDataHandle hInputWorldMatrix = data.inputValue(aInputTransformWorldMatrix, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		MMatrix oInputWorldMatrix = hInputWorldMatrix.asMatrix();
		CHECK_MSTATUS_AND_RETURN_IT(status);

		//if ((hInputWorldMatrix.type() == MFnData::kMatrix) && (hInputTargetMesh.type() == MFnData::kMesh))
		//{

		MArrayDataHandle hGeosArray = data.inputArrayValue(aInputTargetMesh, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MFloatPoint raySource;
		MTransformationMatrix mTransformMatrixInputWorldMatrix = oInputWorldMatrix;
		raySource = mTransformMatrixInputWorldMatrix.getTranslation(MSpace::kWorld);

		MVector vTransformPos = mTransformMatrixInputWorldMatrix.getTranslation(MSpace::kWorld);

		MMatrix rotationMatrix = mTransformMatrixInputWorldMatrix.asRotateMatrix();

		double dRotation[3] = { 0.0, 0.0, 0.0 };

		MFloatVector fVecRayDirection;

		MVector rayDirection = rayDirection.xAxis;

		rayDirection = (rayDirection * rotationMatrix);

		unsigned int numTargetGeos = hGeosArray.elementCount();

		bool hitCheck;

		MTransformationMatrix outputTransformMatrix;
		MMatrix outMatrix;
		MFloatPoint hitPoint;
		MPoint resultPointTmp;

		for (unsigned int i = 0; i < numTargetGeos; i++)
		{
			hGeosArray.jumpToArrayElement(i);
			MDataHandle hGeoArrayElement = hGeosArray.inputValue();
			MFnMesh mFnTargetMesh = hGeoArrayElement.asMesh();

			hitCheck = mFnTargetMesh.closestIntersection(
				raySource,
				rayDirection,
				nullptr,
				nullptr,
				false,
				MSpace::kWorld,
				99999999,
				false,
				nullptr,
				hitPoint,
				nullptr,
				nullptr,
				nullptr,
				NULL,
				NULL
			);

			std::cout << "hitCheck : " << hitCheck << endl;
			std::cout << "hitPoint : " << "[ " << hitPoint.x << ", " << hitPoint.y << ", " << hitPoint.z << " ]" << endl;

			if (hitCheck == true)
			{
				resultPointTmp.x = hitPoint.x;
				resultPointTmp.y = hitPoint.y;
				resultPointTmp.z = hitPoint.z;

				outputTransformMatrix.setTranslation(resultPointTmp, MSpace::kWorld);
				outMatrix = outputTransformMatrix.asMatrix();
			}
		}
		MDataHandle hOutputMatrix = data.outputValue(aOutputTransformMatrix);
		hOutputMatrix.set(outMatrix);
		hOutputMatrix.setClean();

		MDataHandle hOutTranslateX = data.outputValue(outTranslateX);
		hOutTranslateX.set(resultPointTmp.x);
		hOutTranslateX.setClean();

		MDataHandle hOutTranslateY = data.outputValue(outTranslateY);
		hOutTranslateY.set(resultPointTmp.y);
		hOutTranslateY.setClean();

		MDataHandle hOutTranslateZ = data.outputValue(outTranslateZ);
		hOutTranslateZ.set(resultPointTmp.z);
		hOutTranslateZ.setClean();
		//}
		//else
		//{
			//return MS::kInvalidParameter;
		//}
	}
	else
	{
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}