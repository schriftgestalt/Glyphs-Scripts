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

doMetrics = False

def importAFM_file(Doc, filePath):
	global doMetrics
	if os.path.isfile(filePath):
		f = open(filePath)
		
		Font = Doc.font
		FontMaster = Doc.selectedFontMaster()
		
		Line = f.readline()
		while(len(Line) > 0):
			elements = Line.split(" ")
			if len(elements) == 15 and elements[0] == "C" and elements[2] == ";" and elements[3] == "WX" and doMetrics:
				GlyphName = elements[7]
				Glyph = Font.glyphForName_(GlyphName)
				
				if Glyph == None:
					GlyphName = niceName(GlyphName)
					Glyph = Font.glyphForName_(GlyphName)
				if Glyph != None:
					Layer = Glyph.layers[FontMaster.id]
					Layer.LSB = float(elements[10])
					Layer.width = float(elements[4])
				else:
					pass
			elif len(elements) == 4 and elements[0] == "KPX":
				GlyphName1 = elements[1]
				GlyphName2 = elements[2]
				
				Glyph1 = Font.glyphs[GlyphName1]
				if Glyph1 == None:
					GlyphName1 = niceName(GlyphName1)
					Glyph1 = Font.glyphs[GlyphName1]
				
				Glyph2 = Font.glyphs[GlyphName2]
				if Glyph2 == None:
					GlyphName2 = niceName(GlyphName2)
					Glyph2 = Font.glyphs[GlyphName2]
				
				if Glyph1 != None and Glyph2 != None:
					Font.setKerningForFontMasterID_LeftKey_RightKey_Value_(FontMaster.id, Glyph1.id, Glyph2.id, float(elements[3]))
			
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
		if result == NSOKButton:
			print openPanel.URLs().objectAtIndex_(0).path()
			importAFM_file(Doc, openPanel.URLs().objectAtIndex_(0).path())
	else:
		Alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(objc.nil, objc.nil, objc.nil, objc.nil, "Please open a document")
		Alert.runModal()

if __name__ == '__main__':
	main()

