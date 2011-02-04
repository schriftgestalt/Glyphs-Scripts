#MenuTitle: import AFM file
# encoding: utf-8
"""
importAFM.py

Created by Georg Seifert on 2010-04-03.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""

import sys
import os
from GlyphsApp import *
import objc
from AppKit import *
from Foundation import *

def importAFM_file(Doc, filePath):
	if os.path.isfile(filePath):
		f = open(filePath)
		
		Font = Doc.font()
		GlyphsInfo = Glyphs.glyphsInfo
		FontMaster = Doc.selectedFontMaster()
		print "GlyphsInfo", GlyphsInfo
		
		Line = f.readline()
		while(len(Line) > 0):
			elements = Line.split(" ")
			if len(elements) == 15 and elements[0] == "C" and elements[2] == ";" and elements[3] == "WX":
				#print elements
				GlyphName = elements[7]
				Glyph = Font.glyphForName_(GlyphName)
				
				if Glyph == None:
					#print "suche niceName for", GlyphName
					GlyphName = GlyphsInfo.niceGlpyhNameForName_(GlyphName)
					Glyph = Font.glyphForName_(GlyphName)
				#print Glyph
				if Glyph != None:
					print Glyph.name(), "W", elements[4], "L", elements[10]
					Layer = Glyph.layerForKey_(FontMaster.id())
					print "Layer", Layer
					Layer.setLSB_(float(elements[10]))
					Layer.setWidth_(float(elements[4]))
				else:
					#print "Glyph not in font", GlyphName
					pass
			elif len(elements) == 4 and elements[0] == "KPX":
				GlyphName1 = elements[1]
				GlyphName2 = elements[2]
				
				Glyph1 = Font.glyphForName_(GlyphName1)
				if Glyph1 == None:
					GlyphName1 = GlyphsInfo.niceGlpyhNameForName_(GlyphName1)
					Glyph1 = Font.glyphForName_(GlyphName1)
				
				Glyph2 = Font.glyphForName_(GlyphName2)
				if Glyph2 == None:
					GlyphName2 = GlyphsInfo.niceGlpyhNameForName_(GlyphName2)
					Glyph2 = Font.glyphForName_(GlyphName2)
				
				if Glyph1 != None and Glyph2 != None:
					Layer1 = Glyph1.layerForKey_(FontMaster.id())
					Layer2 = Glyph2.layerForKey_(FontMaster.id())
					#setLeftKerning:(CGFloat) Value forLayer:(GSLayer*) LeftLayer;
					print GlyphName1, GlyphName2, float(elements[3])
					Layer1.setRightKerning_forLayer_(float(elements[3]), Layer2)
					
			
			Line = f.readline()

def main():
	Doc = Glyphs.currentDocument
	if (Doc):
		openPanel = NSOpenPanel.openPanel()
		openPanel.setCanChooseDirectories_(NO)
		openPanel.setAllowsMultipleSelection_(NO)
		openPanel.setCanCreateDirectories_(NO)
		openPanel.setTitle_("Choose AFM file.")
		openPanel.setPrompt_("Import")
		openPanel.setCanChooseFiles_(YES)
		Doc = Glyphs.currentDocument
		result = openPanel.runModalForDirectory_file_types_relativeToWindow_(objc.nil, objc.nil, ["afm"], Doc.windowForSheet())
		print "result: ", result
		if result == NSOKButton:
			
			print openPanel.URLs().objectAtIndex_(0).path()
			importAFM_file(Doc, openPanel.URLs().objectAtIndex_(0).path())
			#return [self exportFont: GSFontObj toDirectory:[[openPanel URLs] objectAtIndex:0] error:error];
	else:
		Alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(objc.nil, objc.nil, objc.nil, objc.nil, "Please open a document")
		Alert.runModal()

if __name__ == '__main__':
	main()

