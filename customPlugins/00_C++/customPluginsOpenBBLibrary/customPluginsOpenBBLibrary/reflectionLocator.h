#ifndef REFLECTIONLOCATOR_H
#define REFLECTIONLOCATOR_H

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
 
class ReflectionLocator : public MPxLocatorNode
{
public:
						ReflectionLocator();
	virtual void        postConstructor();
	virtual				~ReflectionLocator(); 

	virtual MStatus		compute( const MPlug& plug, MDataBlock& data );

    virtual void		draw( M3dView&, const MDagPath&, M3dView::DisplayStyle, M3dView::DisplayStatus );
	virtual bool        isBounded() const;
	virtual bool        isTransparent() const;
	virtual MBoundingBox boundingBox() const;

    void drawDisc( float radius, int divisions, bool filled );
    void drawReflection( const MPoint& src, const MPoint& dest );

	static  void*		creator();
	static  MStatus		initialize();

	static MObject      aPlaneMatrix;
	static MObject      aPoint;
    static MObject      aReflectedPoint;
    static MObject      aReflectedParentInverse;
    static MObject      aScale;

private:
    MPoint m_srcPoint, m_destPoint, m_planePoint;
};

#endif
