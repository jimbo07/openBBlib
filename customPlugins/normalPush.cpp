#include <normalPush.h>

const MTypeId normalPush::typeId( 0x89003 );
const MString normalPush::typeName( "normalPush" );

MObject     normalPush::aStrength;
MObject     normalPush::aNormalSmooth;

normalPush::normalPush()
{
	m_data = new NormalPushData;
}

normalPush::~normalPush()
{
	delete m_data;
}

void* normalPush::creator()
{
	return new normalPush();
}


MStatus normalPush::initialize()
{
	MFnNumericAttribute  nAttr;

	aStrength = nAttr.create( "strength", "str", MFnNumericData::kFloat );
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	nAttr.setWritable(true);
	nAttr.setConnectable(true);
	addAttribute( aStrength );

	aNormalSmooth = nAttr.create( "normalSmooth", "ns", MFnNumericData::kInt );
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	nAttr.setWritable(true);
	nAttr.setConnectable(true);
	nAttr.setMin(0);
	addAttribute( aNormalSmooth );

	attributeAffects( normalPush::aStrength, normalPush::outputGeom );
	attributeAffects( normalPush::aNormalSmooth, normalPush::outputGeom );

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer normalPush weights");

	return MStatus::kSuccess;
}

MStatus normalPush::compute(const MPlug& plug, MDataBlock& data)
{

	MStatus status;
	m_data->m_env = data.inputValue(envelope).asFloat();
	m_data->m_strength = data.inputValue(aStrength).asFloat();
	m_data->m_smooth = data.inputValue(aNormalSmooth).asInt();

	if (plug.attribute() == outputGeom)
	{
		unsigned int index = plug.logicalIndex();
		MObject thisNode = this->thisMObject();
		MPlug inPlug(thisNode,input);
		inPlug.selectAncestorLogicalIndex(index,input);
		MDataHandle hInput = data.inputValue(inPlug, &status );
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MDataHandle hGeom = hInput.child(inputGeom);
		MMatrix m = hGeom.geometryTransformMatrix();
		MDataHandle hOutput = data.outputValue(plug);
		hOutput.copy(hGeom);
		MObject inMesh = hGeom.asMesh();
		MFnMesh meshFn(inMesh, &status);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		meshFn.getPoints(m_data->m_points, MSpace::kObject);
		m_data->m_numverts = meshFn.numVertices();

		if(m_data->m_env != 0.00 && m_data->m_strength != 0.00)
		{
			m_data->m_weights.setLength(m_data->m_numverts);
			for (unsigned int idx=0; idx < m_data->m_numverts; idx++)
			{
				m_data->m_weights[idx] = weightValue(data,index,idx) * m_data->m_env * m_data->m_strength;
			}
			if (m_data->m_smooth > 0)
			{
				MObject relaxMesh(inMesh);
				m_relax.relax(relaxMesh, m_data->m_smooth);
				MFnMesh relaxFn(relaxMesh, &status);
				CHECK_MSTATUS_AND_RETURN_IT(status);

				relaxFn.getVertexNormals(false, m_data->m_normals, MSpace::kObject);
			}
			else
			{
				meshFn.getVertexNormals(false, m_data->m_normals, MSpace::kObject);
			}
			
			// THREADED DEFORMATION
			ThreadedDeform td;
			td.data = m_data;
			parallel_for( blocked_range<int>( 0, m_data->m_numverts ), td );
		}
		meshFn.setPoints(m_data->m_points, MSpace::kObject);
	}
	data.setClean(plug);
	return MS::kSuccess;
}
