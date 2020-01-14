#include "edgeRelax.h"

EdgeRelax::EdgeRelax()
{
	m_relaxData = new EdgeRelaxData;
	m_relaxData->m_cachedcount = 0;
}
EdgeRelax::~EdgeRelax() { }

void EdgeRelax::relax(MObject& mesh, unsigned int iterations)
{
	m_relaxData->m_iterations = iterations;

	buildTopology(mesh);

	doRelax();

	MFnMesh meshfn(mesh);
	meshfn.setPoints(m_relaxData->m_relaxpoints);
}

void EdgeRelax::relax(MObject& mesh, unsigned int iterations, MFloatArray &weights)
{
	m_relaxData->m_iterations = iterations;

	buildTopology(mesh);

	m_relaxData->m_weights = weights;

	doRelax();

	MFnMesh meshfn(mesh);
	meshfn.setPoints(m_relaxData->m_relaxpoints);
}

void EdgeRelax::relax(MObject& mesh, unsigned int iterations, MPointArray &output)
{
	m_relaxData->m_iterations = iterations;

	buildTopology(mesh);

	doRelax();

	output.setLength(m_relaxData->m_vertcount);
	output = m_relaxData->m_relaxpoints;
}

void EdgeRelax::relax(MObject& mesh, unsigned int iterations, MPointArray &output, MFloatArray &weights)
{
	m_relaxData->m_iterations = iterations;

	buildTopology(mesh);

	m_relaxData->m_weights = weights;

	doRelax();

	output.setLength(m_relaxData->m_vertcount);
	output = m_relaxData->m_relaxpoints;
}

void EdgeRelax::doRelax()
{
	for (unsigned int idx=0; idx < m_relaxData->m_iterations; ++idx)
	{
		ThreadedDeform td;
		td.data = m_relaxData;
		parallel_for( blocked_range<int>( 0, m_relaxData->m_vertcount ), td );
		m_relaxData->m_points = m_relaxData->m_relaxpoints;
	}
}

void EdgeRelax::buildTopology(MObject &mesh)
{
	MItMeshVertex 	iter(mesh);
	MFnMesh			meshfn(mesh);
	MIntArray 		conVerts;

	meshfn.getPoints(m_relaxData->m_points, MSpace::kObject);

	m_relaxData->m_vertcount = iter.count();
	m_relaxData->m_points.clear();
	m_relaxData->m_relaxpoints.clear();
	m_relaxData->m_weights.clear();
	m_relaxData->m_points.setLength(m_relaxData->m_vertcount);
	m_relaxData->m_relaxpoints.setLength(m_relaxData->m_vertcount);
	m_relaxData->m_weights.setLength(m_relaxData->m_vertcount);

	m_relaxData->m_weights = MFloatArray(m_relaxData->m_vertcount, 1.f);

	if (m_relaxData->m_vertcount  != m_relaxData->m_cachedcount)
	{
		m_relaxData->m_conids.clear();
		m_relaxData->m_conids.resize(m_relaxData->m_vertcount);
		for (unsigned int idx=0; !iter.isDone(); iter.next(),++idx)
		{
				iter.getConnectedVertices(conVerts);
				for (unsigned int idz=0;idz<conVerts.length();++idz)
				{
					m_relaxData->m_conids[idx].push_back(conVerts[idz]);
				}
		}
		iter.reset();
	}
	m_relaxData->m_cachedcount = m_relaxData->m_vertcount;
}
