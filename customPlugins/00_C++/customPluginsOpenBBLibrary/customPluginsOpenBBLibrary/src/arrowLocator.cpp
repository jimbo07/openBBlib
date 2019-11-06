#include "arrowLocator.hpp"

arrowLocator::arrowLocator()
{
}


void arrowLocator::postConstructor()
{
	MObject oThis = thisMObject();
	MFnDependencyNode fnNode(oThis);
	fnNode.setName("arrowLocatorShape#");
}


arrowLocator::~arrowLocator()
{
}


void* arrowLocator::creator()
{
	return new arrowLocator();
}

MStatus arrowLocator::initialize()
{
	return MS::kSuccess;
}

MStatus arrowLocator::compute(const MPlug& plug, MDataBlock& data)

{
	MStatus status;
	/*
	if (plug != aReflectedPoint && plug.parent() != aReflectedPoint)
	{
		return MS::kInvalidParameter;
	}
	MMatrix planeMatrix = data.inputValue(aPlaneMatrix).asMatrix();
	MVector planePos = MTransformationMatrix(planeMatrix).getTranslation(MSpace::kPostTransform);
	MMatrix reflectedParentInverse = data.inputValue(aReflectedParentInverse).asMatrix();
	MMatrix inputMatrix = data.inputValue(aPoint).asMatrix();
	MVector inputPoint = MTransformationMatrix(inputMatrix).getTranslation(MSpace::kPostTransform);
	double scale = data.inputValue(aScale).asDouble();

	MVector normal(0.0, 1.0, 0.0);
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
	MDataHandle hOutput = data.outputValue(aReflectedPoint);
	hOutput.set3Float((float)m_destPoint.x, (float)m_destPoint.y, (float)m_destPoint.z);
	hOutput.setClean();
	data.setClean(plug);

	// Take transform out of points to draw them properly
	MMatrix planeMatrixInverse = planeMatrix.inverse();
	m_srcPoint = MPoint(inputPoint) * planeMatrixInverse;
	m_planePoint = MPoint(planePos) * planeMatrixInverse;
	m_destPoint *= planeMatrixInverse;
	*/
	return MS::kSuccess;
}


void arrowLocator::draw(M3dView& view, const MDagPath& DGpath, M3dView::DisplayStyle style, M3dView::DisplayStatus status)
{
	/*
	view.beginGL();
	glPushAttrib(GL_CURRENT_BIT);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glDepthMask(GL_FALSE);

	
	MColor solidColor, wireColor;
	if (status == M3dView::kActive)
	{
		solidColor = MColor(1.0f, 1.0f, 1.0f, 0.1f);
		wireColor = MColor(1.0f, 1.0f, 1.0f, 1.0f);
	}
	else if (status == M3dView::kLead)
	{
		solidColor = MColor(.26f, 1.0f, .64f, 0.1f);
		wireColor = MColor(.26f, 1.0f, .64f, 1.0f);
	}
	else
	{
		solidColor = MColor(1.0f, 1.0f, 0.0f, 0.1f);
		wireColor = MColor(1.0f, 1.0f, 0.0f, 1.0f);
	}

	// Draw solid
	glColor4f(solidColor.r, solidColor.g, solidColor.b, solidColor.a);
	drawArrow(true);

	// Draw wireframe
	glColor4f(wireColor.r, wireColor.g, wireColor.b, wireColor.a);
	drawArrow(true);

	glDepthMask(GL_TRUE);
	glDisable(GL_BLEND);
	glPopAttrib();
	view.endGL();
	*/
	view.beginGL();

	glPushAttrib(GL_CURRENT_BIT);
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
	glDepthMask(GL_FALSE);

	glBegin(GL_LINES);
	glVertex3f(0.0f, 0.0f, 0.0f);
	glVertex3f(5.0f, 0.0f, 0.0f);
	glEnd();

	view.endGL();

}


void arrowLocator::drawArrow(bool filled)
{

	glBegin(GL_LINES);
	glVertex3f(0.0f, 0.0f, 0.0f);
	glVertex3f(5.0f, 0.0f, 0.0f);
	glEnd();

	//int renderState = filled ? GL_POLYGON : GL_LINE_LOOP;
	/*
	MFloatPointArray points(8);
	points[0] = { 0.0f, 0.0f , 0.0f };
	points[1] = { 0.0f, 1.0f , 0.0f };
	points[2] = { 5.0f, 1.0f , 0.0f };
	points[3] = { 5.0f, 2.0f , 0.0f };
	points[4] = { 7.0f, 0.5f , 0.0f };
	points[5] = { 5.0f, -1.0f , 0.0f };
	points[6] = { 5.0f, 0.0f , 0.0f };
	points[7] = { 0.0f, 0.0f , 0.0f };

	glBegin(GL_LINE);
	for (unsigned int i = 0; i < points.length(); i++)
	{
		glVertex3f(points[i].x, points[i].y, points[i].z);
	}
	glEnd();
	*/
}


bool arrowLocator::isBounded() const
{
	return true;
}


bool arrowLocator::isTransparent() const
{
	return true;
}


MBoundingBox arrowLocator::boundingBox() const
{
	MBoundingBox bbox;
	bbox.expand(MVector(1.0, 1.0, 1.0));
	return bbox;
}



