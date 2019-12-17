#include <maya/MFnPlugin.h>
#include <vertSnap.h>
#include <meshRelax.h>
#include <normalPush.h>
#include <matrixSelector.h>
#include <curveSampler.h>
#include <collisionDeformer.h>
#include <stickySculpt.h>

extern "C" MStatus initializePlugin( MObject obj )
{
	MFnPlugin plugin( obj, PLUGIN_COMPANY, "1.0", "Any");   

	CHECK_MSTATUS ( plugin.registerNode( VertSnap::typeName, VertSnap::typeId,
					VertSnap::creator, VertSnap::initialize, MPxNode::kDeformerNode ) );
	
	CHECK_MSTATUS ( plugin.registerNode( meshRelax::typeName, meshRelax::typeId, 
					meshRelax::creator, meshRelax::initialize, MPxNode::kDeformerNode ) );

	CHECK_MSTATUS ( plugin.registerNode( normalPush::typeName, normalPush::typeId, 
					normalPush::creator, normalPush::initialize, MPxNode::kDeformerNode ) );

	CHECK_MSTATUS ( plugin.registerNode( collisionDeformer::typeName, collisionDeformer::typeId,
					collisionDeformer::creator, collisionDeformer::initialize, MPxNode::kDeformerNode ) );

	CHECK_MSTATUS ( plugin.registerNode( StickySculpt::typeName, StickySculpt::typeId,
					StickySculpt::creator, StickySculpt::initialize, MPxNode::kDeformerNode ) );

	CHECK_MSTATUS ( plugin.registerNode( matrixSelector::typeName, matrixSelector::typeId, 
					matrixSelector::creator, matrixSelector::initialize, MPxNode::kDependNode ) );

	CHECK_MSTATUS ( plugin.registerNode( curveSampler::typeName, curveSampler::typeId,
					curveSampler::creator, curveSampler::initialize, MPxNode::kDependNode ) );
	return MS::kSuccess;
}

extern "C" MStatus uninitializePlugin( MObject obj )
{
	MFnPlugin plugin( obj );

	CHECK_MSTATUS ( plugin.deregisterNode( VertSnap::typeId ) );
	
	CHECK_MSTATUS ( plugin.deregisterNode( meshRelax::typeId ) );
	
	CHECK_MSTATUS ( plugin.deregisterNode( normalPush::typeId ) );
	
	CHECK_MSTATUS ( plugin.deregisterNode( matrixSelector::typeId ) );

	CHECK_MSTATUS ( plugin.deregisterNode( curveSampler::typeId ) );

	CHECK_MSTATUS ( plugin.deregisterNode( collisionDeformer::typeId ) );

	CHECK_MSTATUS ( plugin.deregisterNode( StickySculpt::typeId ) );

	return MS::kSuccess;
}


// PLUGIN IDS:
// 0x89001 - VertSnap
// 0x89002 - MeshRelax
// 0x89003 - NormalPush
// 0x89004 - MatrixSelector
// 0x89005 - curveSampler
// 0x89006 - collisionDeformer
// 0x89007 - stickySculpt
