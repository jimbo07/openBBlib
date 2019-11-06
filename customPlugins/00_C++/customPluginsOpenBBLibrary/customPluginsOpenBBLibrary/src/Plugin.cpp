#include <maya/MFnPlugin.h>
#include "Plugin.hpp"

MStatus initializePlugin(MObject obj)
{
	MStatus status;

	MFnPlugin fnPlugin(obj, "OpenBBLib", "1.0", "Any");

	// MPxNode nodes registration
	status = fnPlugin.registerNode("simpleParentConstraint", 0x00000003, simpleParentConstraint::creator, simpleParentConstraint::initialize);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.registerNode("projectMesh", 0x00000004, projectMesh::creator, projectMesh::initialize);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.registerNode("transformRayCast", 0x00000005, transformRayCast::creator, transformRayCast::initialize);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// MPxDeformerNode nodes registration
	status = fnPlugin.registerNode("simpleBlendshape", 0x00000001, simpleBlendshape::creator, simpleBlendshape::initialize, MPxNode::kDeformerNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.registerNode("basicBlendshape", 0x00000002, basicBlendshape::creator, basicBlendshape::initialize, MPxNode::kDeformerNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// MPxLocatorNode nodes registration
	status = fnPlugin.registerNode("arrowLocator", 0x00000006, arrowLocator::creator, arrowLocator::initialize, MPxNode::kLocatorNode);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	return MS::kSuccess;
}


MStatus uninitializePlugin(MObject obj)
{
	MStatus status;

	MFnPlugin fnPlugin(obj);

	// MPxNode nodes de-registration
	status = fnPlugin.deregisterNode(0x00000003);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.deregisterNode(0x00000004);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.deregisterNode(0x00000005);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// MPxDeformerNode nodes de-registration
	status = fnPlugin.deregisterNode(0x00000001);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	status = fnPlugin.deregisterNode(0x00000002);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	// MPxLocatorNode nodes de-registration
	status = fnPlugin.deregisterNode(0x00000006);
	CHECK_MSTATUS_AND_RETURN_IT(status);

	return MS::kSuccess;
}