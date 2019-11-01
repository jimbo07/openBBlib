#include "reflectionLocator.h"

MObject     ReflectionLocator::aPlaneMatrix;
MObject     ReflectionLocator::aPoint;
MObject     ReflectionLocator::aReflectedPoint;
MObject     ReflectionLocator::aReflectedParentInverse;
MObject     ReflectionLocator::aScale;


ReflectionLocator::ReflectionLocator()
{
}


void ReflectionLocator::postConstructor()
{
    MObject oThis = thisMObject();
    MFnDependencyNode fnNode( oThis );
    fnNode.setName( "reflectionShape#" );
}


ReflectionLocator::~ReflectionLocator() 
{
}


void* ReflectionLocator::creator() 
{
    return new ReflectionLocator();
}


MStatus ReflectionLocator::compute( const MPlug& plug, MDataBlock& data )

{
	MStatus status;
 
	if ( plug != aReflectedPoint && plug.parent() != aReflectedPoint )
    {
        return MS::kInvalidParameter;
    }
    MMatrix planeMatrix = data.inputValue( aPlaneMatrix ).asMatrix();
    MVector planePos = MTransformationMatrix( planeMatrix ).getTranslation( MSpace::kPostTransform );
    MMatrix reflectedParentInverse = data.inputValue( aReflectedParentInverse ).asMatrix();
    MMatrix inputMatrix = data.inputValue( aPoint ).asMatrix();
    MVector inputPoint = MTransformationMatrix( inputMatrix ).getTranslation( MSpace::kPostTransform );
    double scale = data.inputValue( aScale ).asDouble();

    MVector normal( 0.0, 1.0, 0.0 );
    normal *= planeMatrix;
    normal.normalize();

    // Get the vector to reflect
    MVector L = inputPoint - planePos;

    // Reflect the vector
    MVector reflectedVector = 2 * ((normal * L) * normal) - L;
    reflectedVector.normalize();
    reflectedVector *= scale;

    // Calculate the reflected point position
    m_destPoint = planePos + reflectedVector;

    // Put into local space
    m_destPoint *= reflectedParentInverse;

    // Set output
    MDataHandle hOutput = data.outputValue( aReflectedPoint );
    hOutput.set3Float( (float)m_destPoint.x, (float)m_destPoint.y, (float)m_destPoint.z );
    hOutput.setClean();
    data.setClean( plug );

    // Take transform out of points to draw them properly
    MMatrix planeMatrixInverse = planeMatrix.inverse();
    m_srcPoint = MPoint( inputPoint ) * planeMatrixInverse;
    m_planePoint = MPoint( planePos ) * planeMatrixInverse;
    m_destPoint *= planeMatrixInverse;

    return MS::kSuccess;
}


void ReflectionLocator::draw( M3dView& view,
						  const MDagPath& DGpath,
						  M3dView::DisplayStyle style,
						  M3dView::DisplayStatus status )
{
    view.beginGL();
	glPushAttrib( GL_CURRENT_BIT );
    glEnable( GL_BLEND );
    glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );
    glDepthMask( GL_FALSE );

	MColor solidColor, wireColor;
    if ( status == M3dView::kActive )
    {
        solidColor = MColor( 1.0f, 1.0f, 1.0f, 0.1f );
        wireColor = MColor( 1.0f, 1.0f, 1.0f, 1.0f );
    }
    else if ( status == M3dView::kLead )
    {
        solidColor = MColor( .26f, 1.0f, .64f, 0.1f );
        wireColor = MColor( .26f, 1.0f, .64f, 1.0f );
    }
    else
    {
        solidColor = MColor( 1.0f, 1.0f, 0.0f, 0.1f );
        wireColor = MColor( 1.0f, 1.0f, 0.0f, 1.0f );
    }
    
    // Draw solid
    glColor4f( solidColor.r, solidColor.g, solidColor.b, solidColor.a );
    drawDisc( 1.0f, 32, true );

    // Draw wireframe
    glColor4f( wireColor.r, wireColor.g, wireColor.b, wireColor.a );
    drawReflection( m_srcPoint, m_destPoint );
    drawDisc( 1.0f, 32, false );
  
	glDepthMask( GL_TRUE );
	glDisable( GL_BLEND );
	glPopAttrib();
    view.endGL();
}


void ReflectionLocator::drawDisc( float radius, int divisions, bool filled )
{
    int renderState = filled ? GL_POLYGON : GL_LINE_LOOP;
    float degreesPerDiv = 360.0f / divisions;
    float radiansPerDiv = degreesPerDiv * 0.01745327778f;
	MFloatPointArray points( divisions );
    for ( int i = 0; i < divisions; i++ )
    {
        float angle = i * radiansPerDiv;
        float x = cos( angle ) * radius;
        float z = sin( angle ) * radius;
        points[i].x = x;
        points[i].z = z;
    }

    glBegin( renderState );
    for ( int i = 0; i < divisions; i++ )
    {
        glVertex3f( points[i].x, 0.0f, points[i].z );
    }
    glEnd();
}


void ReflectionLocator::drawReflection( const MPoint& src, const MPoint& dest )
{
    glBegin( GL_LINES );
    glVertex3f( (float)src.x, (float)src.y, (float)src.z );
    glVertex3f( 0.0f, 0.0f, 0.0f );
    glVertex3f( 0.0f, 0.0f, 0.0f );
    glVertex3f( (float)dest.x, (float)dest.y, (float)dest.z );
    glEnd();
}


bool ReflectionLocator::isBounded() const
{ 
	return true;
}


bool ReflectionLocator::isTransparent() const
{ 
	return true;
}


MBoundingBox ReflectionLocator::boundingBox() const
{
	MBoundingBox bbox;
    bbox.expand( m_srcPoint );
    bbox.expand( m_destPoint );
    bbox.expand( m_planePoint );
    bbox.expand( m_planePoint + MVector( 1.0, 0.0, 0.0 ) );
    bbox.expand( m_planePoint + MVector( -1.0, 0.0, 0.0 ) );
    bbox.expand( m_planePoint + MVector( 0.0, 0.0, 1.0 ) );
    bbox.expand( m_planePoint + MVector( 0.0, 0.0, -1.0 ) );
	return bbox;
}


MStatus ReflectionLocator::initialize()
{
	MFnMatrixAttribute mAttr;
    MFnNumericAttribute nAttr;


    aReflectedPoint = nAttr.createPoint( "reflectedPoint", "reflectedPoint" );
    nAttr.setWritable( false );
    nAttr.setStorable( false );
    addAttribute( aReflectedPoint );

    aPlaneMatrix = mAttr.create( "planeMatrix", "planeMatrix" );
    addAttribute( aPlaneMatrix );
    attributeAffects( aPlaneMatrix, aReflectedPoint );

    aPoint = mAttr.create( "point", "point" );
    addAttribute( aPoint );
    attributeAffects( aPoint, aReflectedPoint );

    aReflectedParentInverse = mAttr.create( "reflectedParentInverse", "reflectedParentInverse" );
    mAttr.setDefault( MMatrix::identity );
    addAttribute( aReflectedParentInverse );
    attributeAffects( aReflectedParentInverse, aReflectedPoint );

    aScale = nAttr.create( "scale", "scale", MFnNumericData::kDouble, 1.0 );
    nAttr.setKeyable( true );
    addAttribute( aScale );
    attributeAffects( aScale, aReflectedPoint );

	return MS::kSuccess;
}
