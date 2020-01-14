#include <collisionDeformer.h>

const MTypeId	collisionDeformer::typeId( 0x89006 );
const MString	collisionDeformer::typeName( "collisionDeformer" );

MObject 		collisionDeformer::aCollisionStrength;
MObject 		collisionDeformer::aCollisionMesh;
MObject 		collisionDeformer::aCollisionMeshName;
MObject 		collisionDeformer::aCollisionMeshList;
MObject 		collisionDeformer::aCollisionBulgeStrength;
MObject 		collisionDeformer::aCollisionBulgeDistance;
MObject 		collisionDeformer::aCollisionBulgeRamp;

collisionDeformer::collisionDeformer()
{
	m_collisionData = new CollisionData;
}
collisionDeformer::~collisionDeformer()
{
	delete m_collisionData;
}
void* collisionDeformer::creator(){ return new collisionDeformer(); }

MStatus collisionDeformer::initialize()
{
	MFnTypedAttribute		tAttr;
	MFnNumericAttribute		nAttr;
	MFnCompoundAttribute	cAttr;
	MRampAttribute			rAttr;
	MFnStringData			stringdata;

	aCollisionMesh = tAttr.create( "collisionMesh", "cm", MFnData::kMesh );
	tAttr.setStorable(false);
	tAttr.setConnectable(true);
	addAttribute( aCollisionMesh );

	aCollisionMeshName = tAttr.create( "collisionMeshName", "cmn", MFnData::kString, stringdata.create() );
	tAttr.setStorable(true);
	tAttr.setConnectable(true);
	tAttr.setKeyable(false);
	addAttribute( aCollisionMeshName );

	aCollisionStrength = nAttr.create( "collisionStrength", "cs", MFnNumericData::kFloat, 1.f );
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(0.f);
	nAttr.setMax(1.f);
	addAttribute( aCollisionStrength );

	aCollisionBulgeStrength = nAttr.create( "collisionBulgeStrength", "cbs", MFnNumericData::kFloat, 0.f );
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(0);
	addAttribute( aCollisionBulgeStrength );

	aCollisionBulgeDistance = nAttr.create( "collisionBulgeDistance", "cbd", MFnNumericData::kFloat, 0.f );
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(0);
	addAttribute( aCollisionBulgeDistance );

	aCollisionMeshList = cAttr.create("collisionMeshList", "cml");
	cAttr.setArray(true);
	cAttr.setUsesArrayDataBuilder(true);
	cAttr.addChild(aCollisionMeshName);
	cAttr.addChild(aCollisionStrength);
	cAttr.addChild(aCollisionBulgeStrength);
	cAttr.addChild(aCollisionBulgeDistance);
	cAttr.addChild(aCollisionMesh);
	cAttr.setStorable(true);
	cAttr.setReadable(true);
	cAttr.setConnectable(true);
	addAttribute(aCollisionMeshList);

	aCollisionBulgeRamp = rAttr.createCurveRamp("collisionBulgeRamp", "cbr");
	addAttribute(aCollisionBulgeRamp);

	attributeAffects( collisionDeformer::aCollisionStrength, collisionDeformer::outputGeom );
	attributeAffects( collisionDeformer::aCollisionMesh, collisionDeformer::outputGeom );
	attributeAffects( collisionDeformer::aCollisionMeshList, collisionDeformer::outputGeom );
	attributeAffects( collisionDeformer::aCollisionBulgeStrength, collisionDeformer::outputGeom );
	attributeAffects( collisionDeformer::aCollisionBulgeDistance, collisionDeformer::outputGeom );
	attributeAffects( collisionDeformer::aCollisionBulgeRamp, collisionDeformer::outputGeom );

	MGlobal::executeCommand("makePaintable -attrType multiFloat -sm deformer collisionDeformer weights");

	return MStatus::kSuccess;
}

MStatus collisionDeformer::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;
	MObject thisNode = this->thisMObject();

	if (plug.attribute() == outputGeom)
	{
		float env = data.inputValue(envelope).asFloat();

		m_collisionData->m_bulgeRampAttribute = MRampAttribute(thisNode, aCollisionBulgeRamp, &status);

		unsigned int index = plug.logicalIndex();
		MPlug inPlug(thisNode,input);
		inPlug.selectAncestorLogicalIndex(index,input);
		MDataHandle hInput = data.inputValue(inPlug, &status );
		CHECK_MSTATUS_AND_RETURN_IT(status);

		MDataHandle hGeom = hInput.child(inputGeom);
		MDataHandle hOutput = data.outputValue(plug);
		hOutput.copy(hGeom);
		MObject outMesh = hGeom.asMesh();
		MFnMesh meshFn(outMesh);

		status = meshFn.getPoints(m_collisionData->m_points, MSpace::kWorld);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		status = meshFn.getVertexNormals(false, m_collisionData->m_normals, MSpace::kWorld);
		CHECK_MSTATUS_AND_RETURN_IT(status);

		// RESIZE ALL ARRAYS
		m_collisionData->m_numpoints = m_collisionData->m_points.length();
		m_collisionData->m_weights.setLength(m_collisionData->m_numpoints);
		m_collisionData->m_collided.setLength(m_collisionData->m_numpoints);

		if(env > 0)
		{
			for (unsigned int idx=0; idx<m_collisionData->m_numpoints; idx++)
			{
				m_collisionData->m_boxin.expand(m_collisionData->m_points[idx]);
				m_collisionData->m_weights[idx] = weightValue(data,index,idx) * env;
			}

			MArrayDataHandle arrayHandle = data.inputArrayValue(aCollisionMeshList, &status);
			unsigned int count = arrayHandle.elementCount();
			for (unsigned int midx=0; midx < count; midx++)
			{
				ThreadedCollide tc;
				tc.data = m_collisionData;

				ThreadedBulge tb;
				tb.data = m_collisionData;

				arrayHandle.jumpToArrayElement(midx);
				MDataHandle collisionMeshHnd = arrayHandle.inputValue(&status).child(aCollisionMesh);
				CHECK_MSTATUS_AND_RETURN_IT(status);

				MDataHandle collisionBulgeStrengthHnd = arrayHandle.inputValue(&status).child(aCollisionBulgeStrength);
				CHECK_MSTATUS_AND_RETURN_IT(status);

				MDataHandle collisionBulgeDistanceHnd = arrayHandle.inputValue(&status).child(aCollisionBulgeDistance);
				CHECK_MSTATUS_AND_RETURN_IT(status);

				MDataHandle collisionStrengthHnd = arrayHandle.inputValue(&status).child(aCollisionStrength);
				CHECK_MSTATUS_AND_RETURN_IT(status);

				m_collisionData->m_collisionStrength = collisionStrengthHnd.asFloat();
				m_collisionData->m_bulgeStrength = collisionBulgeStrengthHnd.asFloat();
				m_collisionData->m_bulgeDistance = collisionBulgeDistanceHnd.asFloat();
				m_collisionData->m_defmax = 0.f;

				if ((m_collisionData->m_collisionStrength > 0.f) && !collisionMeshHnd.data().isNull())
				{
					MFloatPointArray pointsCol;
					MObject	colMesh = collisionMeshHnd.asMeshTransformed();
					tc.colFn = new MFnMesh(colMesh);

					status = tc.colFn->getPoints(pointsCol, MSpace::kWorld);
					CHECK_MSTATUS_AND_RETURN_IT(status);

					for (unsigned int idx=0; idx<pointsCol.length(); idx++)
					{
						m_collisionData->m_boxcol.expand(pointsCol[idx]);
					}

					m_collisionData->m_mmAccelParams = tc.colFn->autoUniformGridParams();
					m_collisionData->m_intersector.create(colMesh);

					if (m_collisionData->m_boxin.intersects(m_collisionData->m_boxcol))
					{
						parallel_for( blocked_range<int>( 0, m_collisionData->m_numpoints ), tc );
						parallel_for( blocked_range<int>( 0, m_collisionData->m_numpoints ), tb );
					}
				}
			}
		}
		meshFn.setPoints(m_collisionData->m_points, MSpace::kWorld);
	}
	data.setClean(plug);
	return MS::kSuccess;
}

void collisionDeformer::postConstructor()
{
	MStatus status;

	status = postConstructor_initialise_ramp_curve( aCollisionBulgeRamp, 0, 0.0f, 0.0f, 2 );
	CHECK_MSTATUS(status);
	status = postConstructor_initialise_ramp_curve( aCollisionBulgeRamp, 1, 0.3f, 0.8f, 2 );
	CHECK_MSTATUS(status);
	status = postConstructor_initialise_ramp_curve( aCollisionBulgeRamp, 2, 1.0f, 0.0f, 2 );
	CHECK_MSTATUS(status);
}

MStatus collisionDeformer::postConstructor_initialise_ramp_curve( MObject &rampObj, int index, float position, float value, int interpolation)
{
	MStatus status;

	MObject thisNode = this->thisMObject();

	MPlug rampPlug( thisNode, rampObj );
	MPlug elementPlug = rampPlug.elementByLogicalIndex( index, &status );

	MPlug positionPlug = elementPlug.child(0, &status);
	status = positionPlug.setFloat(position);

	MPlug valuePlug = elementPlug.child(1);
	status = valuePlug.setFloat(value);

	MPlug interpPlug = elementPlug.child(2);
	interpPlug.setInt(interpolation);

	return MS::kSuccess;
}
