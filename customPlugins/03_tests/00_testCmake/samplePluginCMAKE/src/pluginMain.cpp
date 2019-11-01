#include "sampleCmd.h"

#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )
{
    MStatus status;

    MFnPlugin fnPlugin( obj, "Fabio openBBLib", "1.0", "Any" );

    status = fnPlugin.registerCommand( "sampleCommand", SampleCmd::creator );
    CHECK_MSTATUS_AND_RETURN_IT( status );

    return MS::kSuccess;
}


MStatus uninitializePlugin( MObject obj )
{
    MStatus status;

    MFnPlugin fnPlugin( obj );

    status = fnPlugin.deregisterCommand( "sampleCommand" );
    CHECK_MSTATUS_AND_RETURN_IT( status );

    return MS::kSuccess;
}