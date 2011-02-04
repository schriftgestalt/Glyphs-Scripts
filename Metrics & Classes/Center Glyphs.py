#MenuTitle: Center Glyphs
# encoding: utf-8
"""
Center Layers.py

Created by Georg Seifert on 2011-01-17.
Copyright (c) 2011 schriftgestaltung.de. All rights reserved.
"""

import sys
import os
from GlyphsApp import *
import objc
from AppKit import *
from Foundation import *

def main():
	Doc = Glyphs.currentDocument
	Font = Doc.font()
	SelectedLayers = Doc.selectedLayers()
	for Layer in SelectedLayers:
		LSB = Layer.LSB()
		RSB = Layer.RSB()
		Width = Layer.width()
		newSB = (LSB + RSB) / 2.0
		print LSB, RSB, newSB
		Layer.setLSB_(newSB)
		Layer.setWidth_(Width)

if __name__ == '__main__':
	main()

