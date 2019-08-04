#pragma once

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFloatPointArray.h>
#include <maya/MGlobal.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MTypeId.h> 
#include <maya/MVector.h> 
#include <maya/MPoint.h> 
#include <maya/MMatrix.h> 
#include <maya/MDataBlock.h> 

#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnMatrixAttribute.h>

class arrowLocator : public MPxLocatorNode
{
	public:
								arrowLocator();
		virtual void			postConstructor();
		virtual					~arrowLocator();

		virtual MStatus			compute(const MPlug& plug, MDataBlock& data);

		virtual void			draw(M3dView&, const MDagPath&, M3dView::DisplayStyle, M3dView::DisplayStatus);
		virtual bool			isBounded() const;
		virtual bool			isTransparent() const;
		virtual MBoundingBox	boundingBox() const;

		void drawArrow(bool filled);

		static  void*			creator();
		static  MStatus			initialize();

		/*
		static MObject			aPlaneMatrix;
		static MObject			aPoint;
		static MObject			aReflectedPoint;
		static MObject			aReflectedParentInverse;
		static MObject			aScale;
		*/
};