"""Pens for creating glyphs in Glyphs."""

import sys
import objc
from AppKit import *
from Foundation import *

from GlyphsApp import *
from objectsGS import RGlyph, GSLINE, GSCURVE, GSOFFCURVE, GSSHARP, GSSMOOTH

from robofab.objects.objectsBase import MOVE, LINE, CURVE, QCURVE, OFFCURVE

__all__ = ["GSPen", "GSPointPen"]

from robofab.pens.pointPen import AbstractPointPen
from robofab.pens.adapterPens import SegmentToPointPen

class GSPen(SegmentToPointPen):
	def __init__(self, r_glyph):
		SegmentToPointPen.__init__(self, GSPointPen(r_glyph))

class GSPointPen(SegmentToPointPen):
	
	def __init__(self, r_glyph, layer):
		self._glyph = r_glyph
		self._layer = layer
		self._path = None
	
	def beginPath(self):
		self._path = GSPath()
		self._path.closed = True
		self._layer.paths.append(self._path)
	
	def endPath(self):
		self._glyph._invalidateContours()
	
	def moveTo(self, pt):
		self._path = GSPath()
		self._path.closed = True
		self._layer.paths.append(self._path)
		self.addPoint(pt, MOVE)
		
	def lineTo(self, pt):
		self.addPoint(pt, LINE)
		
	def addPoint(self, pt, segmentType=None, smooth=None, name=None, **kwargs):
		if name is not None:
			_Anchor = GSAnchor(name=name, pt=pt)
			self._layer.anchors.append(_Anchor)
		else:
			_Node = GSNode(pt)
			if segmentType == LINE:
				_Node.type = GSLINE
			elif segmentType == CURVE:
				_Node.type = GSCURVE
			elif segmentType == QCURVE:
				_Node.type = GSQCURVE
			elif segmentType == OFFCURVE or segmentType is None:
				_Node.type = GSOFFCURVE
			elif segmentType == MOVE:
				_Node.type = GSLINE
				self._layer.paths[-1].setClosed_(0)
			if smooth:
				_Node.connection = GSSMOOTH
			self._path.addNodeFast_(_Node)
	
	def addComponent(self, baseName, transformation):
		if isinstance(baseName, RGlyph):
			baseName = baseName.name
		_Component = GSComponent(baseName, transform=transformation)
		self._layer.addComponent_(_Component)
	
	def closePath(self):
		if self._path is not None:
			self._path.setClosePath_(1)

def test():
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
