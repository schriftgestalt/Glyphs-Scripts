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

class GSPointPen(SegmentToPointPen):
	
	def __init__(self, r_glyph, layer):
		self._glyph = r_glyph
		self._layer = layer
		self._path = None
	
	def beginPath(self):
		self._path = GSPath()
		self._path.closed = True
		self._layer.paths.append( self._path )
	
	def endPath(self):
		self._glyph._invalidateContours()
	
	def moveTo(self, pt):
		self._path = GSPath()
		self._path.closed = True
		self._layer.paths.append( self._path )
		self.addPoint( pt, "move" )
		
	def lineTo(self, pt):
		self.addPoint( pt, "line" )
		
	def addPoint(self, pt, segmentType=None, smooth=None, name=None, **kwargs):
		if name is not None:
			_Anchor = GSAnchor(name=name, pt=pt)
			self._layer.addAnchor_(_Anchor)
		else:
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
			self._path.nodes.append(_Node)
	
	def addComponent(self, baseName, transformation):
		if isinstance(baseName, "RGlyph"):
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
