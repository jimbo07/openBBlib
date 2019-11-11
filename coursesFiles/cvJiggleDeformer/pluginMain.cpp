/*
Copyright (c) 2012 Chad Vernon

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
#include "cvJiggleDeformer.h"
#include "cvJiggleCmd.h"
#include <maya/MFnPlugin.h>


MStatus initializePlugin(MObject obj) { 
  MStatus status;  
  MFnPlugin fnPlugin(obj, "Chad Vernon", "1.0", "Any");

  status = fnPlugin.registerNode("cvJiggle", cvJiggle::id, cvJiggle::creator,
                                 cvJiggle::initialize, MPxNode::kDeformerNode);
  CHECK_MSTATUS_AND_RETURN_IT(status);

  status = fnPlugin.registerCommand("cvJiggle",          
                                    cvJiggleCmd::creator,
                                    cvJiggleCmd::newSyntax);      
  CHECK_MSTATUS_AND_RETURN_IT(status);

  return status;
}


MStatus uninitializePlugin(MObject obj) {
  MStatus   status;
  MFnPlugin fnPlugin(obj);
  status = fnPlugin.deregisterCommand("cvJiggle");        
  CHECK_MSTATUS_AND_RETURN_IT(status);

  status = fnPlugin.deregisterNode(cvJiggle::id);
  CHECK_MSTATUS_AND_RETURN_IT(status);

  return status;
}
