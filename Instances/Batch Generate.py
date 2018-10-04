#MenuTitle: Batch Generate Fonts
# -*- coding: utf-8 -*-
__doc__="""
Batch Generate Fonts.
"""

from GlyphsApp import OTF, TTF, WOFF, WOFF2, EOT

fileFolder = "~/Desktop/files"

otf_path = "~/Desktop/export"
ttf_path = "~/Desktop/export"
ufo_path = "~/Desktop/export"
web_path = "~/Desktop/export"

OTF_AutoHint = True
TTF_AutoHint = True
RemoveOverlap = True
UseSubroutines = True
UseProductionNames = True
Web_OutlineFormat = TTF

import os

fileFolder = os.path.expanduser(fileFolder)
fileNames = os.listdir(fileFolder)

for fileName in fileNames:
	if os.path.splitext(fileName)[1] == ".glyphs":
		font = GSFont(os.path.join(fileFolder, fileName))
		print font.familyName
		for instance in font.instances:
			print "== Exporting OTF =="
			print instance.generate(Format=OTF, FontPath=os.path.expanduser(otf_path), AutoHint=OTF_AutoHint, RemoveOverlap=RemoveOverlap, UseSubroutines=UseSubroutines, UseProductionNames=UseProductionNames)
		print
		for instance in font.instances:
			print "== Exporting TTF =="
			print instance.generate(Format=TTF, FontPath=os.path.expanduser(ttf_path), AutoHint=TTF_AutoHint, RemoveOverlap=RemoveOverlap, UseProductionNames=UseProductionNames)
		print
		for instance in font.instances:
			print "== Exporting Web =="
			print instance.generate(Format=Web_OutlineFormat, FontPath=os.path.expanduser(web_path), AutoHint=TTF_AutoHint, RemoveOverlap=RemoveOverlap, UseSubroutines=UseSubroutines, UseProductionNames=UseProductionNames, Containers=[WOFF, WOFF2, EOT])
		print