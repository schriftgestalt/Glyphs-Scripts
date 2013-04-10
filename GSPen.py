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

class GSPointPen(SegmentToPointPen):
	
	def __init__(self, r_glyph, layer):
		self._glyph = r_glyph
		self._layer = layer
	
	def beginPath(self):
		_Path = GSPath()
		_Path.closed = True
		self._layer.paths.append( _Path )
	
	def endPath(self):
		self._glyph._invalidateContours()
	
	def addPoint(self, pt, segmentType=None, smooth=None, name=None, **kwargs):
		if name is not None:
			_Anchor = NewAnchor(pt, name)
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
			self._layer.paths[-1].nodes.append(_Node)
	
	def addComponent(self, baseName, transformation):
		xx, xy, yx, yy, dx, dy = transformation
		# XXX warn when xy or yx != 0
		_Component = GSComponent()
		
		if baseName:
			if isinstance(baseName, str):
				_Component.setComponentName_(baseName)
			elif isinstance(name, "GSGlyph"):
				_Component.setComponent_(glyph)
			elif isinstance(name, "RGlyph"):
				_Component.setComponentName_(baseName.name)
		_Component.setTransformStruct_(transformation)
		
		self._layer.addComponent_(_Component)
	
	def closePath(self):
		print "__closePath__", self._layer.paths
		Path = self._layer.paths[-1]
		if Path != None:
			self._layer.paths[-1].setClosePath_(1)

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
