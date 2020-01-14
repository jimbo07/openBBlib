#include <meshRelax.h>

const MTypeId	meshRelax::typeId( 0x89002 );
const MString	meshRelax::typeName( "meshRelax" );

MObject 		meshRelax::aIterations;

meshRelax::meshRelax(){}
meshRelax::~meshRelax(){}
void* meshRelax::creator(){ return new meshRelax(); }

MStatus meshRelax::initialize()
{
	MFnNumericAttribute  nAttr;

	aIterations = nAttr.create( "iterations", "it", MFnNumericData::kInt );
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	nAttr.setWritable(true);
	nAttr.setConnectable(true);
	nAttr.setMin(0);
	addAttribute( aIterations );

	attributeAffects( meshRelax::aIterations, meshRelax::outputGeom );

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer meshRelax weights");

	return MStatus::kSuccess;
}

MStatus meshRelax::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus stat;
	MPointArray pts;
	MPointArray rpts;
	float env = data.inputValue(envelope).asFloat();
	unsigned int iterations = data.inputValue(aIterations).asInt();
	unsigned int vertCount;

	if (plug.attribute() == outputGeom)
	{
		unsigned int index = plug.logicalIndex();
		MObject thisNode = this->thisMObject();
		MPlug inPlug(thisNode,input);
		inPlug.selectAncestorLogicalIndex(index,input);
		MDataHandle hInput = data.inputValue(inPlug, &stat );
		CHECK_MSTATUS_AND_RETURN_IT(stat)

		MDataHandle hGeom = hInput.child(inputGeom);
		MMatrix m = hGeom.geometryTransformMatrix();
		MDataHandle hOutput = data.outputValue(plug);
		hOutput.copy(hGeom);
		MObject outMesh = hGeom.asMesh();
		MFnMesh meshFn(outMesh);
		vertCount = meshFn.numVertices();
		meshFn.getPoints(pts, MSpace::kObject);
		CHECK_MSTATUS_AND_RETURN_IT(stat)

		MFloatArray w(vertCount);
		if(env != 0.00 && iterations != 0)
		{
			for (unsigned int idx=0; idx < vertCount; idx++)
			{
				w[idx] = weightValue(data,index,idx) * env;
			}
			MObject relaxMesh(outMesh);
			m_relax.relax(relaxMesh, iterations, rpts, w);
			meshFn.setPoints(rpts, MSpace::kObject);
		}
	}
	data.setClean(plug);
	return MS::kSuccess;
}
