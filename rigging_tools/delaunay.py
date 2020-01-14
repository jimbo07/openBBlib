"""
https://www.gaia-gis.it/fossil/libspatialite/wiki?name=tesselations-4.0
http://scicomp.stackexchange.com/questions/3301/concave-polygon-hull-finding
http://en.wikipedia.org/wiki/Standard_deviation
"""

"""
import sys
sys.path.insert(0, '/Users/jarlske/Documents/scripts/python/jm_maya/mesh/')
import delaunay
reload(delaunay)

pointList = [
    [0.8159978060881201, 6.89842885465771, 1.5057350221884591],
    [3.6951309844197633, 1.0500235806877667, 4.710813239825315],
    [16.560572057229557, 18.74079220696262, 14.407498670960582],
    [5.955102464808409, 6.421789014270902, 17.654697053329965],
    [9.022521260109084, 1.4350818652250874, 0.6741873866877901],
    [15.24386888758794, 7.33701746368328, 14.5518474652229],
    [14.416467295307065, 16.85230533988487, 13.949945450995472],
    [14.016617199623676, 11.893369120624978, 15.951873571280736],
    [2.7003763722521668, 8.759107445627574, 11.063673410978561],
    [9.823880008261611, 10.647599678597688, 10.8365859159875],
    [14.170693543195878, 14.77027367366924, 2.70612255230132],
    [19.29947393802449, 15.011760543799506, 1.7921252805945098],
    [15.627453799064362, 5.203439639491851, 13.826827431428871],
    [18.517547884453244, 9.059492585404325, 12.177582598318327],
    [15.747324716438191, 5.094364220709757, 15.648188446881008],
    [13.61978847541345, 11.259894152923804, 13.791599840614746],
    [15.521764814394636, 14.348214547386371, 19.10634124202595],
    [18.091969444984212, 14.360532240168812, 0.2444046064748573],
    [12.736460375757293, 7.362377285952551, 5.925556105709067],
    [17.806815497469113, 13.091728686305368, 8.026943007606581]
]
'''
for each in pointList:
    loc = cmds.spaceLocator()[0]
    cmds.xform(loc, ws=True, t=each)
'''

geo = delaunay.concaveHull(pointList)
"""

import sys
sys.path.insert(0, '/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/')

from math import sqrt, pow
import numpy
from scipy.spatial import Delaunay


def distance3D(point1, point2):
    return sqrt(
        pow((point1[0] - point2[0]), 2) + 
        pow((point1[1] - point2[1]), 2) + 
        pow((point1[2] - point2[2]), 2)
    )


def meanDict(sample):
	sampleMeanDict = {}
	for each in sample:
		for (i, value) in enumerate(each):
			print i
			# Create a list for each column in the sample matrix.
			if not i in sampleMeanDict:
				sampleMeanDict[i] = []
			# Store index for this column of the sample matrix.
			sampleMeanDict[i].append(value)
	return sampleMeanDict


def standardDeviation(sample):

	meanLists = meanDict(sample)


def concaveHull(pointList, factor=3.5):
	# ======================
	# Get Delaunay triangles.
	points = numpy.array(pointList)
	tri = Delaunay(points)
	p = tri.points[tri.simplices]

	# ======================
	# Create standard deviation info.
	# Create list of all edges.
	triList = []
	for points in p:
		triList.append([points[0].tolist(), points[1].tolist(), points[2].tolist()])
		triList.append([points[1].tolist(), points[2].tolist(), points[3].tolist()])
		triList.append([points[2].tolist(), points[3].tolist(), points[0].tolist()])
		triList.append([points[3].tolist(), points[0].tolist(), points[1].tolist()])
	# Create dictionary of distances for each tri list index.
	edgeDistanceDict = {}
	for (triIndex, triPoints) in enumerate(triList):
		edgeDistanceDict[triIndex] = []
		edgeDistanceDict[triIndex].append(distance3D(triPoints[0], triPoints[1]))
		edgeDistanceDict[triIndex].append(distance3D(triPoints[1], triPoints[2]))
		edgeDistanceDict[triIndex].append(distance3D(triPoints[2], triPoints[0]))
	# Gather mean edge length
	compoundEdgeLength = 0
	count = 0
	for triIndex in edgeDistanceDict:
	    for value in edgeDistanceDict[triIndex]:
	        count += 1
	        compoundEdgeLength += value
	meanEdgeLength = compoundEdgeLength / count
	# Calculate difference of each data point
	# from the mean, and square the result of each.
	compoundLengthDiffFromMean = 0
	for triIndex in edgeDistanceDict:
	    for edgeDistance in edgeDistanceDict[triIndex]:
	    	diffFromMeanSquared = pow((edgeDistance - meanEdgeLength), 2)
	    	compoundLengthDiffFromMean += diffFromMeanSquared
	# Next, calculate the mean of these values,
	# and take the square root.
	standardDeviation = sqrt(compoundLengthDiffFromMean / count)

	# ======================
	# Build concave edge list.
	# Remove edges that are larger that standard deviation
	# multiplied by the supplied factor
	count = 0
	distanceMax = standardDeviation * factor
	newTriList = []
	for triIndex in edgeDistanceDict:
		# print '\ntriIndex = ', triIndex
		addToList = True
		for edgeDistance in edgeDistanceDict[triIndex]:
			if edgeDistance < distanceMax: 
				# print "edgeDistance = ", edgeDistance, " < ", distanceMax
				continue
			# print "popping triIndex = ", triIndex
			addToList = False
			break
		if addToList:
			# print 'appending triIndex ', triIndex
			newTriList.append(triList[triIndex])
	# Remove duplicate triangles.
	triList = []
	for each in newTriList:
		appendGo = True
		for index in triList:
			if all((each[0] in index, each[1] in index, each[2] in index)):
				appendGo = False
				break
		if appendGo:
			triList.append(each)
	'''
	# Build list of edges.
	edgeList = []
	for each in triList:
		appendGo1 = True
		appendGo2 = True
		appendGo3 = True
		for crossIndex in edgeList:
			if each[0] in crossIndex and each[1] in crossIndex:
				appendGo1 = False
			if each[1] in crossIndex and each[2] in crossIndex:
				appendGo2 = False
			if each[2] in crossIndex and each[0] in crossIndex:
				appendGo3 = False
		if appendGo1:
			edgeList.append([each[0], each[1]])
		if appendGo2:
			edgeList.append([each[1], each[2]])
		if appendGo3:
			edgeList.append([each[2], each[0]])
	# Count edge occurances
	edgeCount = {}
	for each in triList:
		for edgePoints in edgeList:
			if edgePoints[0] in each and edgePoints[1] in each:
				tupleKey = tuple(edgePoints[0] + edgePoints[1])
				if not tupleKey in edgeCount:
					edgeCount[tupleKey] = 0
				edgeCount[tupleKey] += 1
	# Append triangles with up to 3 occurances:
	newTriList = []
	for each in triList:
		appendGo = True
		for edgeCountKey in edgeCount:
			firstPoint = list(edgeCountKey[:3])
			secondPoint = list(edgeCountKey[3:])
			if firstPoint in each and secondPoint in each:
				if edgeCount[edgeCountKey] > 5:
					appendGo = False
		if not appendGo:
			continue
		newTriList.append(each)

	# ======================
	# Build result triangles.
	for vertList in newTriList:
		cmds.polyCreateFacet(p=[vertList[0], vertList[1], vertList[2]])
	'''

	# ======================
	# Build result triangles.
	for vertList in triList:
		cmds.polyCreateFacet(p=[vertList[0], vertList[1], vertList[2]])


import numpy
from scipy.spatial import Delaunay


def delaunay(pointList):
	points = numpy.array(pointList)
	tri = Delaunay(points)
	p = tri.points[tri.simplices]
	for each in p:
		cmds.polyCreateFacet(p=[each[0].tolist(), each[1].tolist(), each[2].tolist()])
		cmds.polyCreateFacet(p=[each[1].tolist(), each[2].tolist(), each[3].tolist()])
		cmds.polyCreateFacet(p=[each[2].tolist(), each[3].tolist(), each[0].tolist()])
		cmds.polyCreateFacet(p=[each[3].tolist(), each[0].tolist(), each[1].tolist()])


import numpy
from scipy.spatial import ConvexHull
from maya import cmds


def convexHull(pointList):
	"""
	from maya import cmds
	import sys
	sys.path.insert(0, '/Users/jarlske/Documents/scripts/python/jm_maya/mesh/')
	import delaunay
	reload(delaunay)

	sel = cmds.ls(sl=1)
	pointList = []
	for each in sel:
	    vtxLen = cmds.polyEvaluate(each, vertex=1)
	    for i in range(0, vtxLen):
	        pointList.append(cmds.xform('{0}.vtx[{1}]'.format(each, str(i)), q=1, t=1 ,ws=1))
	geo = delaunay.convexHull(pointList)
	"""
	points = numpy.array(pointList)
	hull = ConvexHull(points)
	facetList = []
	for each in hull.simplices:
	    indexList = each.tolist()
	    xpoint = [pointList[indexList[0]][0], pointList[indexList[0]][1], pointList[indexList[0]][2]]
	    ypoint = [pointList[indexList[1]][0], pointList[indexList[1]][1], pointList[indexList[1]][2]]
	    zpoint = [pointList[indexList[2]][0], pointList[indexList[2]][1], pointList[indexList[2]][2]]
	    facetList.append(cmds.polyCreateFacet(ch=False, p=[xpoint, ypoint, zpoint])[0])
	poly = cmds.polyUnite(facetList, ch=False, mergeUVSets=True)
	cmds.polyMergeVertex(poly, ch=False)
	cmds.polyNormal(poly, normalMode=2, userNormalMode=0, ch=False)
	cmds.select(cl=True)
	return poly

