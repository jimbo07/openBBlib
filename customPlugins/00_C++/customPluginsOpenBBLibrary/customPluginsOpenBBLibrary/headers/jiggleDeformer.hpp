#pragma once

#include <maya/MArrayDataHandle.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MPlug.h> 
#include <maya/MPoint.h> 
#include <maya/MPointArray.h> 
#include <maya/MMatrix.h> 
#include <maya/MTypeId.h> 
#include <maya/MPlug.h>
#include <maya/MFloatArray.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MDoubleArray.h>
#include <maya/MIntArray.h>
#include <maya/MVector.h>
#include <maya/MVectorArray.h>
#include <maya/MMatrix.h>
#include <maya/MGlobal.h>
#include <maya/MTime.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MItGeometry.h>

#include <maya/MPxDeformerNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMesh.h>
#include <maya/MFnData.h>
#include <maya/MThreadPool.h>


#include <stdio.h>
#include <iostream>
#include <math.h>
#include <map>
#include <omp.h>

class jiggleDeformer : public MPxDeformerNode
{
	public:
		jiggleDeformer();
		virtual	~jiggleDeformer();

		virtual MStatus	deform(MDataBlock& data,
							   MItGeometry& iter,
							   const MMatrix& mat,
							   unsigned int mIndex);
		
		// virtual MStatus setDependentsDirty(const MPlug& plug, MPlugArray& plugArray);
		static void* creator();
		static MStatus initialize();

		// static  MTypeId id;
		static  MObject aTime;
		static  MObject aDirectionBias;
		static  MObject aNormalStrength;
		static  MObject aScale;
		static  MObject aMaxVelocity;
		static  MObject aStartFrame;
		static  MObject aDampingMagnitude;
		static  MObject aStiffnessMagnitude;
		static  MObject aJiggleMap;
		static  MObject aStiffnessMap;
		static  MObject aDampingMap;
		// static  MObject aPerGeometry;
		static  MObject aInBaseMesh;
		static  MObject aWorldMatrix;

	private:
		MStatus JumpToElement(MArrayDataHandle& hArray, unsigned int index);
		MStatus GetInputMesh(MDataBlock& data, unsigned int geomIndex, MObject* oInputMesh);


		// Store everything per input geometry
		MTime previousTime_;
		bool initialized_;
		bool dirtyMap_;
		MPointArray previousPoints_;
		MPointArray currentPoints_;
		MFloatArray weights_;
		MFloatArray jiggleMap_;
		MFloatArray stiffnessMap_;
		MFloatArray dampingMap_;
		MIntArray membership_;
};