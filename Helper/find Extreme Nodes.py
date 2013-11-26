#MenuTitle: find extreme Nodes
# encoding: utf-8
"""
Created by Georg Seifert on 2013-11-25.
Copyright (c) 2013 schriftgestaltung.de. All rights reserved.
"""

minX = 0
minXG = "##"
minY = 0
minYG = "##"
maxX = 0
maxXG = "##"
maxY = 0
maxYG = "##"

for g in Font.glyphs:
	bounds = g.layers[0].bounds
	#print "__", g.name, bounds
	if NSMinX(bounds) < minX:
		minX = NSMinX(bounds)
		minXG = g.name
	if NSMinY(bounds) < minY:
		minY = NSMinY(bounds)
		minYG = g.name
	if NSMaxX(bounds) > maxX:
		maxX = NSMaxX(bounds)
		maxXG = g.name
	if NSMaxY(bounds) > maxY:
		maxY = NSMaxY(bounds)
		maxYG = g.name

print "MinX", minXG, minX
print "MinY", minYG, minY
print "MaxX", maxXG, maxX
print "MaxY", maxYG, maxY
