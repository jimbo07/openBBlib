#include <matrixSelector.h>

#define _USE_MATH_DEFINES

const MTypeId	matrixSelector::typeId( 0x89004 );
const MString	matrixSelector::typeName( "matrixSelector" );

MObject 		matrixSelector::aInMatrix;
MObject 		matrixSelector::aInMatrixList;
MObject 		matrixSelector::aOutRotate;
MObject 		matrixSelector::aOutRotateX;
MObject 		matrixSelector::aOutRotateY;
MObject 		matrixSelector::aOutRotateZ;
MObject 		matrixSelector::aOutTranslate;
MObject 		matrixSelector::aOutTranslateX;
MObject 		matrixSelector::aOutTranslateY;
MObject 		matrixSelector::aOutTranslateZ;
MObject 		matrixSelector::aInMatrixIndex;

matrixSelector::matrixSelector(){}
matrixSelector::~matrixSelector(){}
void* matrixSelector::creator(){ return new matrixSelector(); }

MStatus matrixSelector::compute(const MPlug& plug, MDataBlock& data)
{
	MStatus status;

	if(plug == aOutRotate || plug == aOutTranslate || plug.parent() == aOutRotate || plug.parent() == aOutTranslate) {
		unsigned int matrixIndex = data.inputValue( aInMatrixIndex ).asShort();
		MArrayDataHandle arrayHandle = data.inputArrayValue(aInMatrixList, &status);
		if (status == MS::kSuccess) {
			unsigned int count = arrayHandle.elementCount();
			if (matrixIndex<count) {
				arrayHandle.jumpToArrayElement(matrixIndex);
				MDataHandle inputHandle = arrayHandle.inputValue(&status).child(aInMatrix);
				if (status == MS::kSuccess) {
					MTransformationMatrix matrix = inputHandle.asMatrix();

					// EXTRACT ROTATION
					MDataHandle rotateHnd = data.outputValue(aOutRotate);
					MEulerRotation erotation = matrix.eulerRotation();
					rotateHnd.set3Double(erotation.x, erotation.y, erotation.z);
					rotateHnd.setClean();

					// EXTRACT TRANSLATION
					MDataHandle translateHnd = data.outputValue(aOutTranslate);
					MVector pos = matrix.getTranslation(MSpace::kWorld);
					translateHnd.set3Double(double(pos.x),double(pos.y),double(pos.z));
					translateHnd.setClean();
				} else {
					MGlobal::displayError("Failed to get Input Handle!");
					return MS::kFailure;
				}
			} else {
				//MGlobal::displayError("Index out of bounds!");
				return MS::kFailure;
			}
		} else {
			MGlobal::displayError("Failed to get InputArray Handle!");
			return MS::kFailure;
		}
	} else {
		return MS::kUnknownParameter;
	}
	data.setClean(plug);
	return MS::kSuccess;
}


MStatus matrixSelector::initialize()
{
	MFnNumericAttribute 	nAttr;
	MFnMatrixAttribute 	mAttr;
	MFnCompoundAttribute    cAttr;
	MFnUnitAttribute uAttr;
	
	aInMatrixIndex = nAttr.create( "matrixIndex", "mi", MFnNumericData::kInt );
	nAttr.setKeyable(true);
	nAttr.setStorable(true);
	nAttr.setWritable(true);
	nAttr.setConnectable(true);
	nAttr.setMin(0);
	addAttribute( aInMatrixIndex );
	
	aInMatrix = mAttr.create( "inMatrix", "im");
	mAttr.setStorable(false);
	mAttr.setConnectable(true);
	addAttribute( aInMatrix );
	
	aInMatrixList = cAttr.create("inMatrixList", "iml");
	cAttr.setArray(true);
	cAttr.addChild(aInMatrix);
	cAttr.setReadable(true);
	cAttr.setUsesArrayDataBuilder(true);
	cAttr.setConnectable(true);
	addAttribute(aInMatrixList);
	
	aOutRotateX = uAttr.create( "outRotateX", "orx", MFnUnitAttribute::kAngle, 0.0);
	uAttr.setWritable(true);
	uAttr.setStorable(true);
	uAttr.setConnectable(true);
	aOutRotateY = uAttr.create( "outRotateY", "ory", MFnUnitAttribute::kAngle, 0.0);
	uAttr.setWritable(true);
	uAttr.setStorable(true);
	uAttr.setConnectable(true);
	aOutRotateZ = uAttr.create( "outRotateZ", "orz", MFnUnitAttribute::kAngle, 0.0);
	uAttr.setWritable(true);
	uAttr.setStorable(true);
	uAttr.setConnectable(true);
	aOutRotate = nAttr.create( "outRotate", "or", aOutRotateX, aOutRotateY, aOutRotateZ);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	addAttribute( aOutRotate );
	
	aOutTranslateX = nAttr.create( "outTranslateX", "otx", MFnNumericData::kDouble, 0.0);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	aOutTranslateY = nAttr.create( "outTranslateY", "oty", MFnNumericData::kDouble, 0.0);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	aOutTranslateZ = nAttr.create( "outTranslateZ", "otz", MFnNumericData::kDouble, 0.0);
	nAttr.setWritable(true);
	nAttr.setStorable(true);
	nAttr.setConnectable(true);
	aOutTranslate = nAttr.create( "outTranslate", "ot", aOutTranslateX, aOutTranslateY, aOutTranslateZ);
	addAttribute( aOutTranslate );
	
	attributeAffects( matrixSelector::aInMatrixIndex,		matrixSelector::aOutRotate );
	attributeAffects( matrixSelector::aInMatrix,			matrixSelector::aOutRotate );
	attributeAffects( matrixSelector::aInMatrixList,		matrixSelector::aOutRotate );
	
	attributeAffects( matrixSelector::aInMatrixIndex,		matrixSelector::aOutTranslate );
	attributeAffects( matrixSelector::aInMatrix,			matrixSelector::aOutTranslate );
	attributeAffects( matrixSelector::aInMatrixList,		matrixSelector::aOutTranslate );

	return MStatus::kSuccess;
}
