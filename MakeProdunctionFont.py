#MenuTitle: make Production Font
# encoding: utf-8
"""
MakeProdunctionFont.py

Created by Georg Seifert on 2011-05-11.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""

import sys
import os
from GlyphsApp import *


def main():
	Doc = Glyphs.currentDocument
	Font = Doc.font 
	print "Font", Font
	Font.setDisablesNiceNames_(True)
	FontMaster = Font.fontMasters()[0]
	removeOverlapFilter = NSClassFromString("GlyphsFilterRemoveOverlap").alloc().init()
	
	for Glyph in Font.glyphs:
		Layer = Glyph.layerForKey_(FontMaster.id)
		Components = Layer.components
		for i in range(2):
			for Component in Components:
				#Component = Layer.components[i]
				#print "Component", Component
				ComponentGlyph = Font.glyphs[Component.componentName()]
				if not ComponentGlyph.keep() or len(Layer.paths) > 0 :
					Component.decompose()
		removeOverlapFilter.runFilterWithLayer_error_(Layer, None)
	Font.willChangeValueForKey_("glyphs")
	for Glyph in Font.glyphs:
		GlyphsInfo = GSGlyphsInfo.glyphInfoForName_(Glyph.name)
		try:
			if GlyphsInfo and GlyphsInfo.legacy() != None:
				#print "GlyphsInfo.legacy()", GlyphsInfo.legacy()
				Glyph.setName_(GlyphsInfo.legacy())
		except:
			pass
	
	Font.didChangeValueForKey_("glyphs")
		
	print "Doc", Doc

if __name__ == '__main__':
	main()

