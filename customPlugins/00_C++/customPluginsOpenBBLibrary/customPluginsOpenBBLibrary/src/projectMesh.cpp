#include "projectMesh.hpp"
#include <iostream>

// declaration of variables/attributes
MObject projectMesh::aInputSourceMesh;
MObject projectMesh::aInputTargetMesh;
MObject projectMesh::aOutputMesh;

// constructor and decostructor
projectMesh::projectMesh() {};
projectMesh::~projectMesh() {};

// creator method for retrieving the instance of the object simpleBlendshape
extern "C" void* projectMesh::creator()
{
	return new projectMesh();
}

// initialize method for al the attribute fo the node
extern "C" MStatus projectMesh::initialize()
{
	MStatus status;

	MFnTypedAttribute tAttr;

	aInputSourceMesh = tAttr.create("sourceMesh", "sM", MFnData::kMesh);
	addAttribute(aInputSourceMesh);

	aInputTargetMesh = tAttr.create("targetMesh", "tM", MFnData::kMesh);
	addAttribute(aInputTargetMesh);

	aOutputMesh = tAttr.create("outputMesh", "oM", MFnData::kMesh);
	addAttribute(aOutputMesh);

	attributeAffects(aInputSourceMesh, aOutputMesh);
	attributeAffects(aInputTargetMesh, aOutputMesh);

	return MS::kSuccess;
}

MStatus projectMesh::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	if (plug == aOutputMesh)
	{

		MDataHandle hInputSourceMesh = data.inputValue(aInputSourceMesh, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MDataHandle hInputTargetMesh = data.inputValue(aInputTargetMesh, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		if ((hInputSourceMesh.type() == MFnData::kMesh) && (hInputTargetMesh.type() == MFnData::kMesh))
		{

			MObject oInputSourceMesh = hInputSourceMesh.asMesh();
			MObject oInputTargetMesh = hInputTargetMesh.asMesh();

			// get the MFnMesh form the two geos pluged in the input
			MFnMesh mFnSourceMesh(oInputSourceMesh, &status);
			CHECK_MSTATUS_AND_RETURN_IT(status);
			MFnMesh mFnTargetMesh(oInputTargetMesh, &status);
			CHECK_MSTATUS_AND_RETURN_IT(status);

			// create and get all the points from the source mesh
			MPointArray mPArrOutMesh;
			mFnSourceMesh.getPoints(mPArrOutMesh);

			// get MDagPath of the MMesh to get the matrix and multiply vertex to it. If I don't do that, all combined mesh will go to the origin
			MDagPath inMeshSrcMDagPath = mFnSourceMesh.dagPath();
			MMatrix inMeshSrcInclusiveMMatrix = inMeshSrcMDagPath.inclusiveMatrix();

			MPoint inMeshMPointTmp;
			MFloatPoint raySource;
			MVector rayDirection;
			MFloatVector fVecRayDirection;
			MFloatPoint hitPoint;
			bool hitCheck;

			// go trhough each vertex and modified it
			for (unsigned int i = 0; i < mPArrOutMesh.length(); i++)
			{
				// the MPoint of the meshSrc in the worldspace
				inMeshMPointTmp = mPArrOutMesh[i] * inMeshSrcInclusiveMMatrix;

				// storing the point in worldSpace found above
				raySource.x = inMeshMPointTmp.x;
				raySource.y = inMeshMPointTmp.y;
				raySource.z = inMeshMPointTmp.z;

				// get the direction of the ray from the src mesh
				mFnSourceMesh.getVertexNormal(i, rayDirection, MSpace::kWorld);

				// calculating the rayDirection
				rayDirection *= inMeshSrcInclusiveMMatrix;

				// store it in a MFloatVector (kind of conversion, maybe there is something more elegant than this)
				fVecRayDirection.x = rayDirection.x;
				fVecRayDirection.y = rayDirection.y;
				fVecRayDirection.z = rayDirection.z;

				std::cout << "fVecRayDirection: " << endl;

				// calculating the hit point on the target mesh ---> it will return a bool (if it is "hit" something or not)
				/*
				bool closestIntersection(
										const MFloatPoint&		raySource,
										const MFloatVector& 	rayDirection,
										const MIntArray* 		faceIds,
										const MIntArray* 		triIds,
										bool 					idsSorted,
										MSpace::Space 			space,
										float 					maxParam,
										bool 					testBothDirections,
										MMeshIsectAccelParams*  accelParams,
										MFloatPoint& 			hitPoint,
										float*	 				hitRayParam,
										int* 					hitFace,
										int* 					hitTriangle,
										float*	 				hitBary1,
										float*	 				hitBary2,
										float 					tolerance = 1e-6,
										MStatus*			 	ReturnStatus = NULL
										)

				in our case we can set some variable of them like this:

						idsSorted = False
						testBothDirections = False
						faceIds = None
						triIds = None
						accelParams = None
						hitRayParam = None
						hitTriangle = None
						hitBary1 = None
						hitBary2 = None
						maxParamPtr = 99999999
				*/

				hitCheck = mFnTargetMesh.closestIntersection(	raySource,
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

				if (hitCheck == true)
				{
					// could be even *** inMeshMPointTmp = hitPoint ***
					inMeshMPointTmp.x = hitPoint.x;
					inMeshMPointTmp.y = hitPoint.y;
					inMeshMPointTmp.z = hitPoint.z;

					mPArrOutMesh.set(inMeshMPointTmp, i);

				}
			}

			MFnMeshData newDataCreator;
			MObject newOutputData = newDataCreator.create();

			int outMeshNumVtx = mFnSourceMesh.numVertices();
			int outMeshNumPolygons = mFnSourceMesh.numPolygons();

			MIntArray outMeshPolygonCountArray;
			MIntArray outMeshVtxArray;
			mFnSourceMesh.getVertices(outMeshPolygonCountArray, outMeshVtxArray);

			MFnMesh meshFS;
			meshFS.create(outMeshNumVtx, outMeshNumPolygons, mPArrOutMesh, outMeshPolygonCountArray, outMeshVtxArray, newOutputData);

			MDataHandle outputMeshHandle = data.outputValue(aOutputMesh, &status);
			outputMeshHandle.setMObject(newOutputData);

			data.setClean(plug);
			
		}
		else
		{
			return MS::kInvalidParameter;
		}
	}
	else
	{
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}