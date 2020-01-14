#ifndef _normalPush
#define _normalPush

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
#include <maya/MFloatArray.h>
#include "edgeRelax.h"

// THREADING
#include "tbb/tbb.h"
using namespace tbb;

class NormalPushData
{
	public:
		unsigned int		m_numverts;
		unsigned int		m_smooth;
		float				m_env;
		float				m_strength;
		MPointArray			m_points;
		MFloatVectorArray	m_normals;
		MFloatArray			m_weights;
};

class normalPush : public MPxDeformerNode
{
	public:
								normalPush();
		virtual					~normalPush();

		virtual MStatus			compute(const MPlug& plug, MDataBlock& data);
		static  void*			creator();
		static  MStatus			initialize();

	public:
		static  MObject			aStrength;
		static  MObject			aNormalSmooth;

		static const MTypeId	typeId;
		static const MString	typeName;

	private:
			EdgeRelax m_relax;
			NormalPushData *m_data;
			struct ThreadedDeform
			{
				NormalPushData *data;
				void operator()( const blocked_range<int>& range ) const {
					for ( int idx = range.begin(); idx!=range.end(); ++idx )
					{
						data->m_points[idx] += data->m_normals[idx] * data->m_weights[idx];
					}
				}
			};
};

#endif
