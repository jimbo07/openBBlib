#ifndef _meshRelax
#define _meshRelax

#include <maya/MPxDeformerNode.h>
#include <maya/MItGeometry.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MFnMesh.h>
#include <maya/MVector.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MGlobal.h>
#include <maya/MMatrix.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MIOStream.h>
#include <edgeRelax.h>


class meshRelax : public MPxDeformerNode
{
	public:
					meshRelax();
			virtual ~meshRelax();
		
			virtual MStatus 	compute(const MPlug& plug, MDataBlock& data);
			static  void* 		creator();
			static  MStatus 	initialize();
	
	public:
		static  MObject 		aIterations;
		static const MTypeId 	typeId;
		static const MString 	typeName;
	private:
		EdgeRelax m_relax;
};

#endif
