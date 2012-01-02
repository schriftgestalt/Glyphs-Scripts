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
	Font.disableUpdateInterface()
	for Glyph in Font.glyphs:
		if not Glyph.keep():
			continue
		Glyph.undoManager().beginUndoGrouping()
		Layer = Glyph.layerForKey_(FontMaster.id)
		Components = Layer.components
		for i in range(2):
			for Component in Components:
				#Component = Layer.components[i]
				
				if not Component.component:
					print Glyph.name, " > Component", Component, Component.component
				ComponentGlyph = Font.glyphs[Component.componentName]
				ComponentLayer = ComponentGlyph.layerForKey_(FontMaster.id)
				if (Glyph.name == "Ncaron"):
					print "__ComponentGlyph:", Glyph.name, " > ", ComponentGlyph.name, ComponentLayer.components
				if (ComponentGlyph and not ComponentGlyph.keep()) or len(Layer.paths) > 0 or len(ComponentLayer.components) > 0:
					if (Glyph.name == "Ncaron"):
						print "__Component.decompose()", Component
					Component.decompose()
		if Glyph.leftKerningGroup:
			Glyph.leftKerningGroup = Glyph.leftKerningGroup.replace("-", "")
		if Glyph.rightKerningGroup:
			Glyph.rightKerningGroup = Glyph.rightKerningGroup.replace("-", "")
		
		for Component in Layer.components:
			if not Component.transformStruct()[0] == 1.0 or not Component.transformStruct()[3] == 1.0:
				Layer.decomposeComponents()
				break
		
		if len(Layer.paths) > 0 and len(Layer.components) > 0:
			Layer.decomposeComponents()
		
		removeOverlapFilter.runFilterWithLayer_error_(Layer, None)
		Glyph.undoManager().endUndoGrouping()
	for Glyph in Font.glyphs:
		Glyph.undoManager().beginUndoGrouping()
		GlyphsInfo = GSGlyphsInfo.glyphInfoForName_(Glyph.name)
		try:
			if GlyphsInfo and GlyphsInfo.legacy() != None:
				Glyph.setName_(GlyphsInfo.legacy())
		except:
			pass
		Glyph.undoManager().endUndoGrouping()
	
	Font.enableUpdateInterface()
	
	print "Doc", Doc

if __name__ == '__main__':
	main()

