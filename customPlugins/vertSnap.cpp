#include <vertSnap.h>

MTypeId 		VertSnap::typeId ( 0x89001 );
const MString 	VertSnap::typeName( "vertSnap" );

MObject 		VertSnap::aDriverMesh;
MObject 		VertSnap::aSearchDistance;
MObject 		VertSnap::aCutoffDistance;
MObject 		VertSnap::aInitialize;
MObject 		VertSnap::aVertexMap;

VertSnap::VertSnap()
{
	m_vertSnapData = new VertSnapData;
}
VertSnap::~VertSnap()
{
	delete m_vertSnapData;
}
void* VertSnap::creator(){ return new VertSnap(); }

MStatus VertSnap::initialize()
{
	MFnTypedAttribute 		tAttr;
	MFnEnumAttribute 		eAttr;
	MFnNumericAttribute 	nAttr;

	aDriverMesh = tAttr.create( "driverMesh", "drv", MFnData::kMesh );
	tAttr.setStorable(false);
	tAttr.setConnectable(true);
	addAttribute( aDriverMesh );

	aSearchDistance = nAttr.create( "SearchDistance", "sd", MFnNumericData::kFloat, 0.01);
	nAttr.setStorable(true);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);
	addAttribute(aSearchDistance);

	aCutoffDistance = nAttr.create( "Cutoff", "cof", MFnNumericData::kFloat, 0.0);
	nAttr.setStorable(true);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setKeyable(true);
	nAttr.setMin(0.0);
	addAttribute(aCutoffDistance);

	aInitialize = eAttr.create( "initialize", "inl" );
	eAttr.addField(	"Off", 0);
	eAttr.addField(	"Re-Set Bind", 1);
	eAttr.addField(	"Bound", 2);
	eAttr.setKeyable(true);
	eAttr.setStorable(true);
	eAttr.setReadable(true);
	eAttr.setWritable(true);
	eAttr.setDefault(0);
	addAttribute( aInitialize );

	aVertexMap = nAttr.create( "vtxIndexMap", "vtximp", MFnNumericData::kLong, -9999 );
	nAttr.setKeyable(false);
	nAttr.setArray(true);
	nAttr.setStorable(true);
	nAttr.setReadable(true);
	nAttr.setWritable(true);
	nAttr.setUsesArrayDataBuilder(true);
	addAttribute( aVertexMap );

	attributeAffects(VertSnap::aDriverMesh, 	VertSnap::outputGeom);
	attributeAffects(VertSnap::aSearchDistance,	VertSnap::outputGeom);
	attributeAffects(VertSnap::aCutoffDistance,	VertSnap::outputGeom);
	attributeAffects(VertSnap::aInitialize, 	VertSnap::outputGeom);
	attributeAffects(VertSnap::aVertexMap,		VertSnap::outputGeom);

	MGlobal::executeCommand( "makePaintable -attrType \"multiFloat\" -sm \"deformer\" \"vertSnap\" \"weights\";" );

	return MStatus::kSuccess;
}

MStatus VertSnap::deform( MDataBlock& data, MItGeometry& iter, const MMatrix& localToWorldMatrix, unsigned int mIndex)
{
	MStatus status;
	short initialized_mapping = data.inputValue( aInitialize ).asShort();

	if( initialized_mapping == 1 )
	{
		status = initializeMapping(data, iter, localToWorldMatrix);
		initialized_mapping = data.inputValue( aInitialize ).asShort();
	}
	if( initialized_mapping == 2 )
	{
		float env = data.inputValue(envelope).asFloat();
		MArrayDataHandle vertMapArrayData  = data.inputArrayValue( aVertexMap );

		MDataHandle meshAttrHandle = data.inputValue( aDriverMesh, &status );
		MItGeometry drvIter( meshAttrHandle );

		drvIter.allPositions(m_vertSnapData->m_drvpoints, MSpace::kWorld);
		iter.allPositions(m_vertSnapData->m_defpoints);
		m_vertSnapData->m_mapping.setLength(m_vertSnapData->m_defpoints.length());
		m_vertSnapData->m_weights.setLength(m_vertSnapData->m_defpoints.length());
		m_vertSnapData->m_localToWorldMatrix = localToWorldMatrix;

		for ( unsigned int idx = 0; idx < m_vertSnapData->m_defpoints.length(); idx++ )
		{
			vertMapArrayData.jumpToElement(idx);
			m_vertSnapData->m_mapping[idx] = vertMapArrayData.inputValue().asInt();
			m_vertSnapData->m_weights[idx] = weightValue( data, mIndex, idx ) * env;
		}

		ThreadedDeform td;
		td.data = m_vertSnapData;
		parallel_for( blocked_range<int>( 0, m_vertSnapData->m_defpoints.length() ), td );

		iter.setAllPositions(m_vertSnapData->m_defpoints);
	}
	return status;
}



MStatus VertSnap::initializeMapping( MDataBlock& data, MItGeometry& iter, const MMatrix& localToWorldMatrix)
{
	MStatus status;

	MDataHandle cutoffDistanceHnd = data.inputValue(aCutoffDistance, &status);
	m_vertSnapData->m_cutoffDistance = cutoffDistanceHnd.asFloat();

	MDataHandle searchDistanceHnd = data.inputValue(aSearchDistance, &status);
	m_vertSnapData->m_searchDistance = searchDistanceHnd.asFloat();

	MDataHandle meshAttrHandle = data.inputValue( aDriverMesh, &status );
	MItGeometry drvIter( meshAttrHandle );

	drvIter.allPositions(m_vertSnapData->m_drvpoints, MSpace::kWorld);
	iter.allPositions(m_vertSnapData->m_defpoints);
	m_vertSnapData->m_mapping.setLength(m_vertSnapData->m_defpoints.length());
	m_vertSnapData->m_localToWorldMatrix = localToWorldMatrix;

	ThreadedInitialize ti;
	ti.data = m_vertSnapData;
	parallel_for( blocked_range<int>( 0, m_vertSnapData->m_defpoints.length() ), ti );
	
	MArrayDataHandle vertMapOutArrayHandle  =  data.outputArrayValue( aVertexMap, &status );
	CHECK_MSTATUS(status);
	MArrayDataBuilder vertMapOutArrayBuilder = vertMapOutArrayHandle.builder(&status);
	CHECK_MSTATUS(status);

	for ( unsigned int idx = 0; idx < m_vertSnapData->m_defpoints.length(); idx++ )
	{
		MDataHandle initIndexData = vertMapOutArrayBuilder.addElement( idx, &status );
		CHECK_MSTATUS(status);
		initIndexData.setInt(m_vertSnapData->m_mapping[idx]);
		initIndexData.setClean();
	}

	vertMapOutArrayHandle.set( vertMapOutArrayBuilder );

	MObject tObj  =  thisMObject();
	MPlug setInitMode( tObj, aInitialize );
	setInitMode.setValue( 2 ); 

	data.setClean(aVertexMap);
	return status;
}

MObject& VertSnap::accessoryAttribute() const
{
	return VertSnap::aDriverMesh ;
}
