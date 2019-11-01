#include "transformRayCast.hpp"
#include <iostream>

// ---------- DECLARATION OF NODE VARIABLES/ATTRIBUTES -------- //
MObject transformRayCast::aInputTransformWorldMatrix;
MObject transformRayCast::aInputTargetMesh;
MObject transformRayCast::aInputTargetReflectionMesh;
MObject transformRayCast::aOutputTransformMatrix;
MObject transformRayCast::outTranslate;
MObject transformRayCast::outTranslateX;
MObject transformRayCast::outTranslateY;
MObject transformRayCast::outTranslateZ;
MObject transformRayCast::reflection;

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
	MFnEnumAttribute eAttr;

	aInputTransformWorldMatrix = mAttr.create("sourceTrasformWorldMatrix", "iSTWM");
	mAttr.setConnectable(true);
	addAttribute(aInputTransformWorldMatrix);

	aInputTargetMesh = tAttr.create("targetMesh", "iTM", MFnData::kMesh);
	tAttr.setArray(true);
	tAttr.setUsesArrayDataBuilder(true);
	addAttribute(aInputTargetMesh);

	aInputTargetReflectionMesh = tAttr.create("targetReflectionMesh", "iTRM", MFnData::kMesh);
	tAttr.setArray(true);
	tAttr.setUsesArrayDataBuilder(true);
	addAttribute(aInputTargetReflectionMesh);

	reflection = eAttr.create("reflection", "ref", 0);
	eAttr.setDefault(0);
	eAttr.addField("no", 0);
	eAttr.addField("yes", 1);
	eAttr.setKeyable(false);
	eAttr.setConnectable(true);
	addAttribute(reflection);

	aOutputTransformMatrix = mAttr.create("outputTransformMatrix", "oTM", MFnMatrixAttribute::kDouble);
	addAttribute(aOutputTransformMatrix);

	outTranslateX = nAttr.create("translateX", "otX", MFnNumericData::kDouble, 0.0);
	outTranslateY = nAttr.create("translateY", "otY", MFnNumericData::kDouble, 0.0);
	outTranslateZ = nAttr.create("translateZ", "otZ", MFnNumericData::kDouble, 0.0);
	outTranslate = nAttr.create("translate", "ot", outTranslateX, outTranslateY, outTranslateZ);
	addAttribute(outTranslate);

	attributeAffects(aInputTransformWorldMatrix, aOutputTransformMatrix);
	attributeAffects(aInputTargetMesh, aOutputTransformMatrix);
	attributeAffects(aInputTargetReflectionMesh, aOutputTransformMatrix);
	attributeAffects(aInputTransformWorldMatrix, outTranslate);
	attributeAffects(aInputTargetMesh, outTranslate);


	return MS::kSuccess;
}

MStatus transformRayCast::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	if (plug == aOutputTransformMatrix)
	{
		MDataHandle inReflectionHandle = data.inputValue(reflection, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		int reflectionCheck = inReflectionHandle.asInt();

		MDataHandle hInputWorldMatrix = data.inputValue(aInputTransformWorldMatrix, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);
		MMatrix oInputWorldMatrix = hInputWorldMatrix.asMatrix();
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MArrayDataHandle hGeosArray = data.inputArrayValue(aInputTargetMesh, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MArrayDataHandle hGeosReflectionArray = data.inputArrayValue(aInputTargetReflectionMesh, &status);
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

		unsigned int numTargetReflectionGeos = hGeosReflectionArray.elementCount();

		bool hitCheck;

		MTransformationMatrix outputTransformMatrix;
		MMatrix outMatrix;
		MFloatPoint hitPoint;
		MPoint resultPointTmp;
		MVector outTranslations;
		
		//int * faceIDHittedPtr;
		int faceIDHitted;
		//faceIDHittedPtr = &faceIDHitted;

		MFloatVectorArray faceNormals;

		//MPoint resulTReflectionPointTmp;

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
															&faceIDHitted,
															nullptr,
															NULL,
															NULL
														);

			std::cout << "FaceIDHitted : " << faceIDHitted << endl;

			status = mFnTargetMesh.getFaceVertexNormals(faceIDHitted, faceNormals, MSpace::kWorld);
			CHECK_MSTATUS_AND_RETURN_IT(status);

			if (hitCheck == true)
			{
				resultPointTmp.x = hitPoint.x;
				resultPointTmp.y = hitPoint.y;
				resultPointTmp.z = hitPoint.z;
			}
		}

		
		std::cout << "hitCheck : " << hitCheck << endl;
		std::cout << "hitPoint : " << "[ " << hitPoint.x << ", " << hitPoint.y << ", " << hitPoint.z << " ]" << endl;


		if (reflectionCheck == 1 && numTargetReflectionGeos != 0)
		{
			bool hitReflectionCheck;
			MFloatPoint hitReflectionPoint;
					
			MVector normal = faceNormals[0];
			normal.normalize();

			MVector L = (MPoint)raySource - resultPointTmp;

			MVector reflectedVector = 2 * ((normal * L) * normal) - L;
			reflectedVector.normalize();

			for (unsigned int i = 0; i < numTargetGeos; i++)
			{
				hGeosReflectionArray.jumpToArrayElement(i);
				MDataHandle hGeoReflectionArrayElement = hGeosReflectionArray.inputValue();
				MFnMesh mFnReflectionTargetMesh = hGeoReflectionArrayElement.asMesh();

				hitReflectionCheck = mFnReflectionTargetMesh.closestIntersection(
																					resultPointTmp,
																					reflectedVector,
																					nullptr,
																					nullptr,
																					false,
																					MSpace::kWorld,
																					99999999,
																					false,
																					nullptr,
																					hitReflectionPoint,
																					nullptr,
																					nullptr,
																					nullptr,
																					NULL,
																					NULL
																				);

				if (hitReflectionCheck == true)
				{
					resultPointTmp.x = hitReflectionPoint.x;
					resultPointTmp.y = hitReflectionPoint.y;
					resultPointTmp.z = hitReflectionPoint.z;
				}
			}
				
			std::cout << "hitReflectionCheck : " << hitReflectionCheck << endl;
			std::cout << "hitReflectionPoint : " << "[ " << hitReflectionPoint.x << ", " << hitReflectionPoint.y << ", " << hitReflectionPoint.z << " ]" << endl;

		}

		outputTransformMatrix.setTranslation(resultPointTmp, MSpace::kWorld);
		outMatrix = outputTransformMatrix.asMatrix();
		outTranslations = outputTransformMatrix.getTranslation(MSpace::kWorld, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MDataHandle hOutputMatrix = data.outputValue(aOutputTransformMatrix);
		hOutputMatrix.set(outMatrix);
		hOutputMatrix.setClean();

		MDataHandle hOutTranslateX = data.outputValue(outTranslateX);
		hOutTranslateX.set(outTranslations.x);
		hOutTranslateX.setClean();

		MDataHandle hOutTranslateY = data.outputValue(outTranslateY);
		hOutTranslateY.set(outTranslations.y);
		hOutTranslateY.setClean();

		MDataHandle hOutTranslateZ = data.outputValue(outTranslateZ);
		hOutTranslateZ.set(outTranslations.z);
		hOutTranslateZ.setClean();

	}
	else
	{
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}