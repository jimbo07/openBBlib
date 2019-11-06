#include "simpleParentConstraint.hpp"

// declaration of all attributes
MObject	simpleParentConstraint::aMantainOffset;

MObject	simpleParentConstraint::aInParentWorldMatrix;
MObject	simpleParentConstraint::aInParentWorldInverseMatrix;
MObject	simpleParentConstraint::aInTargetWorldMatrix;
MObject	simpleParentConstraint::aInTargetWorldInverseMatrix;

MObject	simpleParentConstraint::aOutTranslate;
MObject	simpleParentConstraint::aOutTranslateX;
MObject	simpleParentConstraint::aOutTranslateY;
MObject	simpleParentConstraint::aOutTranslateZ;

MObject	simpleParentConstraint::aOutRotate;
MObject	simpleParentConstraint::aOutRotateX;
MObject	simpleParentConstraint::aOutRotateY;
MObject	simpleParentConstraint::aOutRotateZ;

MObject	simpleParentConstraint::aOutScale;
MObject	simpleParentConstraint::aOutScaleX;
MObject	simpleParentConstraint::aOutScaleY;
MObject	simpleParentConstraint::aOutScaleZ;

// constructor and deconstructor function for the main class basicBlendshape
simpleParentConstraint::simpleParentConstraint() {};
simpleParentConstraint::~simpleParentConstraint() {};

// creator method for retrieving the instance of the object basicBlendshape
extern "C" void* simpleParentConstraint::creator()
{
	return new simpleParentConstraint();
}

// initialize method for al the attribute fo the node
extern "C" MStatus simpleParentConstraint::initialize()
{
	MStatus status;

	MFnNumericAttribute nAttr;
	MFnMatrixAttribute mAttr;
	MFnEnumAttribute eAttr;
	MFnUnitAttribute uAttr;

	aMantainOffset = eAttr.create("mantainOffset", "mo", 0);
	eAttr.setDefault(0);
	eAttr.addField("no", 0);
	eAttr.addField("yes", 1);
	eAttr.setKeyable(false);
	eAttr.setConnectable(true);
	addAttribute(aMantainOffset);

	/**************** NODE INPUTS ATTRIBUTES ****************/

	// parent world matrix input
	aInParentWorldMatrix = mAttr.create("parentWorldMatrix", "parentWorldMatrix");
	//mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(aInParentWorldMatrix);

	// parent world inverse matrix input
	aInParentWorldInverseMatrix = mAttr.create("parentWorldInverseMatrix", "parentWorldInverseMatrix");
	//mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(aInParentWorldInverseMatrix);

	// parent world matrix input
	aInTargetWorldMatrix = mAttr.create("targetWorldMatrix", "targetWorldMatrix");
	//mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(aInTargetWorldMatrix);

	// parent world matrix input
	aInTargetWorldInverseMatrix = mAttr.create("targetWorldInverseMatrix", "targetWorldInverseMatrix");
	//mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute(aInTargetWorldInverseMatrix);

	/**************** NODE OUTPUTS ATTRIBUTES ****************/

	// translate attributes output
	aOutTranslateX = nAttr.create("outTranslateX", "outTranslateX", MFnNumericData::kDouble, 0.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutTranslateX);
	
	aOutTranslateY = nAttr.create("outTranslateY", "outTranslateY", MFnNumericData::kDouble, 0.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutTranslateZ);
	
	aOutTranslateZ = nAttr.create("outTranslateZ", "outTranslateZ", MFnNumericData::kDouble, 0.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutTranslateZ);
	
	aOutTranslate = nAttr.create("outTranslate", "outT", aOutTranslateX, aOutTranslateY, aOutTranslateZ);
	addAttribute(aOutTranslate);


	// rotate attributes output
	aOutRotateX = uAttr.create("outRotateX", "outRotateX", MFnUnitAttribute::kAngle, 0.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutRotateX);

	aOutRotateY = uAttr.create("outRotateY", "outRotateY", MFnUnitAttribute::kAngle, 0.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutRotateY);

	aOutRotateZ = uAttr.create("outRotateZ", "outRotateZ", MFnUnitAttribute::kAngle, 0.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutRotateZ);

	aOutRotate = nAttr.create("outRotate", "outR", aOutRotateX, aOutRotateY, aOutRotateZ);
	addAttribute(aOutRotate);

	// scale attributes output
	aOutScaleX = nAttr.create("aOutScaleX", "aOutScaleX", MFnNumericData::kDouble, 1.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutScaleX);

	aOutScaleY = nAttr.create("aOutScaleY", "aOutScaleY", MFnNumericData::kDouble, 1.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutScaleY);
	
	aOutScaleZ = nAttr.create("aOutScaleZ", "aOutScaleZ", MFnNumericData::kDouble, 1.0);
	//nAttr.setWritable(false);
	//nAttr.setStorable(false);
	//addAttribute(aOutScaleZ);

	aOutScale = nAttr.create("outScale", "outS", aOutScaleX, aOutScaleY, aOutScaleZ);
	addAttribute(aOutScale);

	// set the influences of the inputs/outputs

	attributeAffects(aInParentWorldMatrix, aOutTranslate);

	attributeAffects(aInParentWorldMatrix, aOutRotate);

	attributeAffects(aInParentWorldMatrix, aOutScale);

	attributeAffects(aInParentWorldInverseMatrix, aOutTranslate);

	attributeAffects(aInParentWorldInverseMatrix, aOutRotate);

	attributeAffects(aInParentWorldInverseMatrix, aOutScale);

	attributeAffects(aInTargetWorldMatrix, aOutTranslate);

	attributeAffects(aInTargetWorldMatrix, aOutRotate);

	attributeAffects(aInTargetWorldMatrix, aOutScale);

	attributeAffects(aInTargetWorldInverseMatrix, aOutTranslate);

	attributeAffects(aInTargetWorldInverseMatrix, aOutRotate);

	attributeAffects(aInTargetWorldInverseMatrix, aOutScale);

	return MS::kSuccess;
}

MStatus simpleParentConstraint::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	MDataHandle inMantainOffsetHandle = data.inputValue(aMantainOffset, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	int mo = inMantainOffsetHandle.asInt();

	MDataHandle inParentWorldMatrixHandle = data.inputValue(aInParentWorldMatrix, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MMatrix mPWM = inParentWorldMatrixHandle.asMatrix();

	MDataHandle inTargetWorldInverseMatrixHandle = data.inputValue(aInTargetWorldInverseMatrix, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	const MMatrix mTWIM = inTargetWorldInverseMatrixHandle.asMatrix();

	MDataHandle inParentWorldInverseMatrixHandle = data.inputValue(aInParentWorldInverseMatrix, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MMatrix mPWIM = inParentWorldInverseMatrixHandle.asMatrix();

	MDataHandle inTargetWorldMatrixHandle = data.inputValue(aInTargetWorldMatrix, &status);
	CHECK_MSTATUS_AND_RETURN_IT(status);
	MMatrix mTWM = inTargetWorldMatrixHandle.asMatrix();

	MMatrix outMatrix;
	//MTransformationMatrix offsetMatrix;
	MMatrix offsetMatrix;
	//const MFloatMatrix ;
	//double outScale
	/*
	if (mo == 0)
	{
		if ((plug == aInParentWorldMatrix) || (plug == aInTargetWorldInverseMatrix))
		{

			outMatrix = mPWM * mTWIM;

		}
		else
		{
			return MS::kSuccess;
		}
	}
	else
	{
		if ((plug == aInParentWorldMatrix) || (plug == aInTargetWorldInverseMatrix) || (plug == aInParentWorldInverseMatrix) || (plug == aInTargetWorldMatrix))
		{

			
			constexpr double offsetConstMatrix[4][4] = 
			{
				{1.0, 0.0, 0.0, 0.0},
				{0.0, 1.0, 0.0, 0.0},
				{0.0, 0.0, 1.0, 0.0},
				{0.0, 0.0, 0.0, 1.0},
			};
			
			offsetMatrix = mTWM * mPWIM;

			//offsetConstMatrix = offsetMatrix.asMatrix(status);

			outMatrix = offsetMatrix * mPWM * mTWIM;

		}
		else
		{
			return MS::kSuccess;
		}
	}
	*/

	offsetMatrix = mTWM * mPWIM;

	//outMatrix = offsetMatrix * mPWM * mTWIM;

	outMatrix = mPWM * mTWIM;

	std::cout << "sono quì" << endl;

	MTransformationMatrix outTransformMatrix = outMatrix;

	MVector outTranslations = outTransformMatrix.getTranslation(MSpace::kWorld);

	MTransformationMatrix::RotationOrder rotateOrder = MTransformationMatrix::kXYZ;

	double outRotations[3] = {0.0, 0.0, 0.0};
	outTransformMatrix.getRotation(outRotations, rotateOrder);

	double outScales[3] = {1.0, 1.0, 1.0};
	outTransformMatrix.getScale(outScales, MSpace::kWorld);


	MDataHandle outTranslateHandle = data.outputValue(aOutTranslate);
	outTranslateHandle.set(outTranslations[0], outTranslations[1], outTranslations[2]);
	outTranslateHandle.setClean();

	MDataHandle outRotateHandle = data.outputValue(aOutRotate);
	outRotateHandle.set(outRotations[0], outRotations[1], outRotations[2]);
	outRotateHandle.setClean();

	MDataHandle outScaleHandle = data.outputValue(aOutScale);
	outScaleHandle.set(outScales[0], outScales[1], outScales[2]);
	outScaleHandle.setClean();
	/*
	CHECK_MSTATUS(data.setClean(aOutTranslate));
	CHECK_MSTATUS(data.setClean(aOutTranslateX));
	CHECK_MSTATUS(data.setClean(aOutTranslateY));
	CHECK_MSTATUS(data.setClean(aOutTranslateZ));

	CHECK_MSTATUS(data.setClean(aOutRotate));
	CHECK_MSTATUS(data.setClean(aOutRotateX));
	CHECK_MSTATUS(data.setClean(aOutRotateY));
	CHECK_MSTATUS(data.setClean(aOutRotateZ));

	CHECK_MSTATUS(data.setClean(aOutScale));
	CHECK_MSTATUS(data.setClean(aOutScaleX));
	CHECK_MSTATUS(data.setClean(aOutScaleY));
	CHECK_MSTATUS(data.setClean(aOutScaleZ));
	*/
	return MS::kSuccess;
}