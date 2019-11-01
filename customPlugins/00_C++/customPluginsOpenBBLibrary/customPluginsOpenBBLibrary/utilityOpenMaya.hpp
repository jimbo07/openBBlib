#pragma once

#include <tuple>
#include <maya/MFnMesh.h>
#include <maya/MFloatPoint.h>
#include <maya/MStatus.h>

inline std::tuple<MFloatPoint, float, int, int, MStatus> getClosestIntersection(int& times, int& index, MFloatPoint& raySource, MVector& rayDirection, MStatus& status)
{
	if (times == index)
	{

	}
}

/*
hitCheck = mFnTargetMesh.closestIntersection(
	raySource,
	rayDirection,
	nullptr,
	nullptr,
	false,
	MSpace::kWorld,
	99999999,
	false,
	nullptr,
	hitPoint,
	nullptr,
	nullptr,
	nullptr,
	NULL,
	NULL
);
*/