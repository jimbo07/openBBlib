#pragma once

#include <gl/GL.h>
#include <maya/MGL.h>
#include <maya/MPxLocatorNode.h>

/*
void drawArrow(bool filled) MPxLocatorNode::draw()
{
	int renderState = filled ? GL_POLYGON : GL_LINES;

	float degreesPerDiv = 360.0f / divisions;
	float radiansPerDiv = degreesPerDiv * 0.01745327778f;
	MFloatPointArray points(divisions);
	for (int i = 0; i < divisions; i++)
	{
		float angle = i * radiansPerDiv;
		float x = cos(angle) * radius;
		float z = sin(angle) * radius;
		points[i].x = x;
		points[i].z = z;
	}
	
	glBegin(renderState);
	for (int i = 0; i < divisions; i++)
	{
		glVertex3f(points[i].x, 0.0f, points[i].z);
	}
	glEnd();
}
*/