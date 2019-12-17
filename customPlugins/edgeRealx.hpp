#ifndef _EDGERELAX
#define _EDGERELAX

#include <string.h>
#include <math.h>
#include <float.h>
#include <vector>
#include <iostream>
#include <algorithm>

#include <maya/MFnMesh.h>
#include <maya/MVector.h>
#include <maya/MIntArray.h>
#include <maya/MFloatArray.h>
#include <maya/MPointArray.h>
#include <maya/MItMeshVertex.h>

// THREADING
#include "tbb/tbb.h"
using namespace tbb;

class EdgeRelaxData
{
	public:
		unsigned int					m_vertcount;
		unsigned int					m_cachedcount;
		unsigned int					m_iterations;
		MPointArray						m_points;
		MPointArray						m_relaxpoints;
		std::vector<std::vector<int>>	m_conids;
		MFloatArray						m_weights;
};

class EdgeRelax
{
	public:
				EdgeRelax();
		virtual	~EdgeRelax();
		void relax(MObject&, unsigned int);
		void relax(MObject&, unsigned int, MFloatArray &weights);
		void relax(MObject&, unsigned int, MPointArray&);
		void relax(MObject&, unsigned int, MPointArray&, MFloatArray &weights);
	private:
		EdgeRelaxData *m_relaxData;
		void	buildTopology(MObject &mesh);
		void	doRelax();
		struct ThreadedDeform
		{
			EdgeRelaxData *data;
			void operator()( const blocked_range<int>& range ) const {
				unsigned int idz;
				unsigned int numcons;
				for ( int idx = range.begin(); idx!=range.end(); ++idx )
				{
					numcons = data->m_conids[idx].size();
					data->m_relaxpoints[idx] = MPoint();
					for (unsigned int idy=0; idy < numcons; idy++)
					{
						idz = data->m_conids[idx][idy];
						data->m_relaxpoints[idx] += data->m_points[idz];
					}
					data->m_relaxpoints[idx] = data->m_points[idx] + ((data->m_relaxpoints[idx] / float(numcons)) - data->m_points[idx]) * data->m_weights[idx];
				}
			}
		};
};

#endif
