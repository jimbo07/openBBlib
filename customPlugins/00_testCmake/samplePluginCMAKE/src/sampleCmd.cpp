#include "sampleCmd.h"


SampleCmd::SampleCmd()
{
}


void* SampleCmd::creator()
{
    return new SampleCmd;
}


MStatus SampleCmd::doIt( const MArgList& argList )
{
    MGlobal::displayInfo( "Hello there... All it's fine; CMake has compiled the code and the plugin is running without any problem!!!" );
    return MS::kSuccess;
}