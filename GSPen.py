#MenuTitle: GSPen test
"""Pens for creating glyphs in Glyphs."""

import sys
import objc
from AppKit import *
from Foundation import *

from GlyphsApp import *
from objectsGS import RGlyph

__all__ = ["GSPen", "GSPointPen", "drawGSGlyphOntoPointPen"]


#from robofab.tools.toolsFL import NewGlyph
from robofab.pens.pointPen import AbstractPointPen
from robofab.pens.adapterPens import SegmentToPointPen

GSLINE = 1
GSCURVE = 35
GSOFFCURVE = 65
GSSHARP = 0
GSSMOOTH = 4096


class GSPen(SegmentToPointPen):
	def __init__(self, r_glyph):
		SegmentToPointPen.__init__(self, GSPointPen(r_glyph))

class GSPointPen(AbstractPointPen):
	
	def __init__(self, r_glyph, masterIndex = 0):
		# try:
		# 	if hasattr(glyph, "isRobofab"):
		# 		self.glyph = glyph.naked()
		# except:
		#print "pen: glyph", r_glyph
		self._glyph = r_glyph
		#print "Glyph:", r_glyph
		#print "self._glyph._object", self._glyph._object
		#print "self._glyph._object.layers", self._glyph._object.layers
		#print "self._glyph._object.layers[", masterIndex, "]", self._glyph._object.layers[masterIndex]
		if self._glyph._object.parent:
			self._layerID = self._glyph._object.parent.masters[masterIndex].id
			self._layer = self._glyph._object.layerForKey_(self._layerID)
		elif self._glyph._object.layers[masterIndex]:
			#print "__masterIndex"
			self._layerID = self._glyph._object.layers[masterIndex].layerId
			self._layer = self._glyph._object.layers[masterIndex]
		#print "__GSPointPen self._layer:", self._layer
	
	def beginPath(self):
		#print "begin", self._layer.paths
		_Path = GSPath()
		_Path.closed = True
		#print "_Path", _Path
		self._layer.paths.append( _Path )
		#print "newPath:", self._layer.paths
	
	def endPath(self):
		self._glyph._invalidateContours()
		# print "compareString", self._layer.compareString()
		pass
		# path = self.currentPath
		# self.currentPath = None
		# glyph = self.glyph
		# if len(path) == 1 and path[0][3] is not None:
		# 	# Single point on the contour, it has a name. Make it an anchor.
		# 	x, y = path[0][0]
		# 	name = path[0][3]
		# 	anchor = Anchor(name, roundInt(x), roundInt(y))
		# 	glyph.anchors.append(anchor)
		# 	return
		# firstOnCurveIndex = None
		# for i in range(len(path)):
		# 	if path[i][1] is not None:
		# 		firstOnCurveIndex = i
		# 		break
		# if firstOnCurveIndex is None:
		# 	# TT special case: on-curve-less contour. FL doesn't support that,
		# 	# so we insert an implied point at the end.
		# 	x1, y1 = path[0][0]
		# 	x2, y2 = path[-1][0]
		# 	impliedPoint = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
		# 	path.append((impliedPoint, "qcurve", True, None))
		# 	firstOnCurveIndex = 0
		# path = path[firstOnCurveIndex + 1:] + path[:firstOnCurveIndex + 1]
		# firstPoint, segmentType, smooth, name = path[-1]
		# closed = True
		# if segmentType == "move":
		# 	path = path[:-1]
		# 	closed = False
		# 	# XXX The contour is not closed, but I can't figure out how to
		# 	# create an open contour in FL. Creating one by hand shows type"0x8011"
		# 	# for a move node in an open contour, but I'm not able to access
		# 	# that flag.
		# elif segmentType == "line":
		# 	# The contour is closed and ends in a lineto, which is redundant
		# 	# as it's implied by closepath.
		# 	path = path[:-1]
		# x, y = firstPoint
		# node = Node(nMOVE, Point(roundInt(x), roundInt(y)))
		# if smooth and closed:
		# 	if segmentType == "line" or path[0][1] == "line":
		# 		node.alignment = nFIXED
		# 	else:
		# 		node.alignment = nSMOOTH
		# glyph.Insert(node, len(glyph))
		# segment = []
		# nPoints = len(path)
		# for i in range(nPoints):
		# 	pt, segmentType, smooth, name = path[i]
		# 	segment.append(pt)
		# 	if segmentType is None:
		# 		continue
		# 	if segmentType == "curve":
		# 		if len(segment) < 2:
		# 			segmentType = "line"
		# 		elif len(segment) == 2:
		# 			segmentType = "qcurve"
		# 	if segmentType == "qcurve":
		# 		for x, y in segment[:-1]:
		# 			glyph.Insert(Node(nOFF, Point(roundInt(x), roundInt(y))), len(glyph))
		# 		x, y = segment[-1]
		# 		node = Node(nLINE, Point(roundInt(x), roundInt(y)))
		# 		glyph.Insert(node, len(glyph))
		# 	elif segmentType == "curve":
		# 		if len(segment) == 3:
		# 			cubicSegments = [segment]
		# 		else:
		# 			from fontTools.pens.basePen import decomposeSuperBezierSegment
		# 			cubicSegments = decomposeSuperBezierSegment(segment)
		# 		nSegments = len(cubicSegments)
		# 		for i in range(nSegments):
		# 			pt1, pt2, pt3 = cubicSegments[i]
		# 			x, y = pt3
		# 			node = Node(nCURVE, Point(roundInt(x), roundInt(y)))
		# 			node.points[1].x, node.points[1].y = roundInt(pt1[0]), roundInt(pt1[1])
		# 			node.points[2].x, node.points[2].y = roundInt(pt2[0]), roundInt(pt2[1])
		# 			if i != nSegments - 1:
		# 				node.alignment = nSMOOTH
		# 			glyph.Insert(node, len(self.glyph))
		# 	elif segmentType == "line":
		# 		assert len(segment) == 1, segment
		# 		x, y = segment[0]
		# 		node = Node(nLINE, Point(roundInt(x), roundInt(y)))
		# 		glyph.Insert(node, len(glyph))
		# 	else:
		# 		assert 0, "unsupported curve type (%s)" % segmentType
		# 	if smooth:
		# 		if i + 1 < nPoints or closed:
		# 			# Can't use existing node, as you can't change node attributes
		# 			# AFTER it's been appended to the glyph.
		# 			node = glyph[-1]
		# 			if segmentType == "line" or path[(i+1) % nPoints][1] == "line":
		# 				# tangent
		# 				node.alignment = nFIXED
		# 			else:
		# 				# curve
		# 				node.alignment = nSMOOTH
		# 	segment = []
		# if closed:
		# 	# we may have output a node too much
		# 	node = glyph[-1]
		# 	if node.type == nLINE and (node.x, node.y) == (roundInt(firstPoint[0]), roundInt(firstPoint[1])):
		# 		glyph.DeleteNode(len(glyph) - 1)
	
	def addPoint(self, pt, segmentType=None, smooth=None, name=None, **kwargs):
		#print "add:", pt, segmentType
		if name is not None:
			_Anchor = NewAnchor(pt, name)
			self._layer.addAnchor_(_Anchor)
		else:
			#print "addPoint - segmentType:", segmentType, "pt:", pt
			_Node = GSNode(pt)
			if segmentType == "move":
				_Node.setType_(GSLINE)
				self._layer.paths[-1].setClosed_(0)
			elif segmentType == "line":
				_Node.setType_(GSLINE)
			elif segmentType is "curve":
				_Node.setType_(GSCURVE)
			elif segmentType is "qcurve":
				return
				#raise NotImplementedError
			elif segmentType is None:
				_Node.setType_(GSOFFCURVE)
			if smooth:
				_Node.setConnection_(GSSMOOTH)
			#print "node:", _Node
			#print "self._layer.paths", self._layer.paths[-1]
			self._layer.paths[-1].nodes.append(_Node)
			#print "add:", _Node
	
	def addComponent(self, baseName, transformation):
		xx, xy, yx, yy, dx, dy = transformation
		# XXX warn when xy or yx != 0
		_Component = GSComponent()
		
		if baseName:
			if isinstance(baseName, str):
				# print "glyph:", baseName
				_Component.setComponentName_(baseName)
			elif isinstance(name, "GSGlyph"):
				_Component.setComponent_(glyph)
			elif isinstance(name, "RGlyph"):
				_Component.setComponentName_(baseName.name)
		_Component.setTransformStruct_(transformation)
		
		
		# print "Component:", _Component, " > ", _Component.elementDict()
		self._layer.addComponent_(_Component)
		# print "nach add sComponent:", _Component, " > ", _Component.elementDict()

def test():
	# print  "Glyphs.glyphs",  Glyphs
	g = Glyphs.currentDocument.windowControllers()[0].activeLayer().parent
	print "g", g
	p = GSPen(RGlyph(g))
	print "p", p
	# p.moveTo((50, 50))
	# p.lineTo((150,50))
	# p.lineTo((170, 200))
	# p.curveTo((173, 225), (150, 250), (120, 250))
	# p.curveTo((85, 250), (50, 200), (50, 200))
	# p.closePath()
	
	print "m"
	p.moveTo((300, 300))
	print "l"
	p.lineTo((400, 300))
	print "c"
	p.curveTo((450, 325), (450, 375), (400, 400))
	#p.qCurveTo((400, 500), (350, 550), (300, 500), (300, 400))
	p.closePath()
	
	#p.addComponent("B", (1,1,0,0,10,10))
	# p.setWidth(600)
	# p.setNote("Hello, this is a note")
	# p.addAnchor("top", (250, 600))
	

if __name__ == "__main__":
	test()
