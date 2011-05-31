#FLM: Glyphs Export
# -*- coding: utf8 -*-
# Version 0.3
# copyright Georg Seifert 2011, schriftgestaltung.de
# 
# The scrit will write a .glyphs file at the same loaction than the .vfb file.
# This preserves hints/links, kerning and Multiple Masters.
# if you find any bugs, please report to info@glyphsapp.com

import os.path
import math, time
from plistlib import *

def makePlist(font):
	f = fl.font
	ClassesDict = {}
	FirstClasses = []
	SecondClasses = []
	classes = f.classes
	
	for i in range(len(classes)):
		if classes[i][0] == "_":
			left = f.GetClassLeft(i)
			right = f.GetClassRight(i)
			elements = classes[i].split(" ")
			TargetGlyphs = []
			#print "elements", elements
			key = None
			for j in range(1, len(elements)):
				if len(elements[j]) > 0:
					if elements[j][-1] == "'":
						key = elements[j][:-1]
						TargetGlyphs.append(key)
					else:
						TargetGlyphs.append( elements[j])
			if key == None:
				print "TargetGlyphs ohne Key", TargetGlyphs
				continue
			if left == 1:
				FirstClasses.append(key)
			if right == 1:
				SecondClasses.append(key)
			
			for Target in TargetGlyphs:
				if Target not in ClassesDict:
					ClassesDict[Target] = {}
				if left == 1:
					ClassesDict[Target]['l'] = key
				if right == 1:
					ClassesDict[Target]['r'] = key
	
	#kerning
	#print "ClassesDict", ClassesDict
	#return
	Font = Plist ()
	Font["familyName"] = font.family_name
	Font["gridLength"] = 1
	Font["unitsPerEm"] = font.upm
	FontMasters = []
	MasterCount = font[0].layers_number
	for i in range(MasterCount):
		FontMaster = {}
		FontMaster["ascender"] = font.ascender[i]
		FontMaster["capHeight"] = font.cap_height[i]
		FontMaster["descender"] = font.descender[i]
		FontMaster["xHeight"] = font.x_height[i]
		FontMaster["italicAngle"] = -font.italic_angle
		FontMaster["id"] = ("UUID%d" % i)
		FontMaster["weight"] = "Regular";
		FontMaster["weightValue"] = 100;
		FontMaster["width"] = "Regular";
		FontMaster["widthValue"] = 100;
		FontMasters.append(FontMaster)
		if font.stem_snap_h_num > 0:
			FontMaster["horizontalStems"] = []
			for j in range(font.stem_snap_h_num):
				FontMaster["horizontalStems"].append(font.stem_snap_h[i][j])
		if font.stem_snap_v_num > 0:
			FontMaster["verticalStems"] = []
			for j in range(font.stem_snap_v_num):
				FontMaster["verticalStems"].append(font.stem_snap_v[i][j])
		
		AlignmentCount = font.blue_values_num
		
		FontMaster["alignmentZones"] = []
		for j in range(AlignmentCount, -2, 1):
			print "blue_values __j", j
			FontMaster["alignmentZones"].append("{%d, %d}" %( font.blue_values[i][j-1] , font.blue_values[i][j] - font.blue_values[i][j-1]))
		
		AlignmentCount = font.other_blues_num
		
		for j in range(AlignmentCount, -2, 1):
			print "other_blues __j", j
			FontMaster["alignmentZones"].append("{%d, %d}" %( font.other_blues[i][j-1] , font.other_blues[i][j] - font.other_blues[i][j-1]))
		
		
	if len(FontMasters) == 2:
		try:
			VStem1 = FontMasters[0]["verticalStems"][0]
			VStem2 = FontMasters[1]["verticalStems"][0]
			if VStem2 != VStem1 and VStem1 != 0:
				if VStem1 < VStem2:
					FontMasters[0]["weight"] = "Light"
					FontMasters[0]["weightValue"] = VStem1
					FontMasters[1]["weight"] = "Bold"
					FontMasters[1]["weightValue"] = VStem2
				else:
					FontMasters[1]["weight"] = "Light"
					FontMasters[1]["weightValue"] = VStem1
					FontMasters[0]["weight"] = "Bold"
					FontMasters[0]["weightValue"] = VStem2
		except:
			pass
		
	Font["fontMaster"] = FontMasters
	
	Kerning = {}
	for FontMaster in FontMasters:
		Kerning[FontMaster["id"]] = {}
	
	Glyphs = []
	for glyph in font.glyphs:
		#if len(glyph) > 0:
		#print "f[0].layers_number;", glyph.layers_number
		Glyph = {}
		Glyph["glyphname"] = glyph.name
		Layers = []
		LeftKey = None
		RightKey = None
		try:
			LeftKey = ClassesDict[glyph.name]["l"]
		except:
			pass
		try:
			RightKey = ClassesDict[glyph.name]["r"]
		except:
			pass
		
		#print "Glyph:", glyph.name, " Left: ", LeftKey, " Right: ", RightKey
		if LeftKey:
			Glyph["rightKerningGroup"] = LeftKey
		if RightKey:
			Glyph["leftKerningGroup"] = RightKey
		
		if len(glyph.kerning) > 0:
			print "Glyph:", glyph.kerning, len(glyph.kerning)
			for kerningPair in glyph.kerning:
				firstKey = glyph.name
				secondGlyph = f.glyphs[kerningPair.key]
				secondKey = secondGlyph.name
				# add Kerning classes!!!!
				if firstKey in FirstClasses:
					firstKey = "@MMK_L_"+firstKey
				
				if secondKey in SecondClasses:
					secondKey = "@MMK_R_"+secondKey
				
				print "kerningPair", kerningPair, secondKey
				i = 0
				for FontMaster in FontMasters:
					if firstKey not in Kerning[FontMaster["id"]]:
						Kerning[FontMaster["id"]][firstKey] = {}
						
					value = kerningPair.values[i]
					if secondKey not in Kerning[FontMaster["id"]][firstKey]:
						Kerning[FontMaster["id"]][firstKey][secondKey] = value
					i += 1
		
		for masterIndex in range(glyph.layers_number):
			Layer = {}
			Layer["associatedMasterId"] = FontMasters[masterIndex]["id"]
			Layer["layerId"] = FontMasters[masterIndex]["id"]
			Layer["width"] = glyph.GetMetrics(masterIndex).x
			if len(glyph.components) > 0:
				Components = []
				for component in glyph.components:
					Component = {}
					Component["name"] = font[component.index].name
				
					Component["transform"] = "{%f, 0, 0, %f, %d, %d}" % (component.scales[masterIndex].x, component.scales[masterIndex].y, component.deltas[masterIndex].x, component.deltas[masterIndex].y)
					Components.append(Component)
				Layer["components"] = Components;
			Paths = []
			PathIndesPaths = []
			Nodes = False
			for i in range(len(glyph)):
				node = glyph.nodes[i].Layer(masterIndex)
				if glyph.nodes[i].type == nMOVE:
					if Nodes:
						if Nodes[-1].find("CURVE") > 0:
							LastParts = Nodes[-1].split(" ")
							FirstParts = Nodes[0].split(" ")
							if FirstParts[0] == LastParts[0] and FirstParts[1] == LastParts[1]:
								#print "Entferne ", Nodes[0]
								Nodes.pop(0)
						Paths.append({"nodes": Nodes, "closed":True})
					Nodes = []
				
				if len(node) > 1:
					Nodes.append(("%d %d OFFCURVE" % (node[1].x, node[1].y)))
					Nodes.append(("%d %d OFFCURVE" % (node[2].x, node[2].y)))
					Nodes.append(("%d %d CURVE" % (node[0].x, node[0].y)))
				else:
					Nodes.append(("%d %d LINE" % (node[0].x, node[0].y)))
				if (glyph.nodes[i].alignment != nSHARP):
					Nodes[-1] = Nodes[-1] + " SMOOTH"
				
				PathIndesPaths.append("{%d, %d}" % (len(Paths), len(Nodes)-1))
			
			#print "PathIndesPaths", PathIndesPaths
		
			if Nodes:
				if Nodes[-1].find("CURVE") > 0:
					LastParts = Nodes[-1].split(" ")
					FirstParts = Nodes[0].split(" ")
					if FirstParts[0] == LastParts[0] and FirstParts[1] == LastParts[1]:
						#print "Entferne ", Nodes[0]
						Nodes.pop(0)
				Paths.append({"nodes": Nodes, "closed":True})
			Layer["paths"] = Paths
		
			Hints = []
			for vhint in glyph.vhints:
				Hint = {}
				#print "vhint {%f, %f}" % (vhint.positions[masterIndex], vhint.widths[masterIndex])
				Hint["place"] = "{%f, %f}" % (vhint.positions[masterIndex], vhint.widths[masterIndex])
				Hints.append(Hint)
			for hhint in glyph.hhints:
				Hint = {}
				# if masterIndex == 0:
				# 	print "hhint {%f, %f}" % (hhint.positions[masterIndex], hhint.widths[masterIndex])
				Hint["place"] = "{%f, %f}" % (hhint.positions[masterIndex], hhint.widths[masterIndex])
				Hint["horizontal"] = True
				Hints.append(Hint)
			for vlink in glyph.vlinks:
				Hint = {}
			
				Hint["origin"] = PathIndesPaths[vlink.node1]
				Hint["target"] = PathIndesPaths[vlink.node2]
				#Hint["horizontal"] = False
				Hints.append(Hint)
			for hlink in glyph.hlinks:
				Hint = {}
				# if masterIndex == 0:
				# 	print "hlink {%d, %d} o: %s, t: %s}" % (hlink.node1, hlink.node2, PathIndesPaths[hlink.node1], PathIndesPaths[hlink.node2])
				Hint["origin"] = PathIndesPaths[hlink.node1]
				if hlink.node2 == -1:
					Hint["target"] = "up"
				elif hlink.node2 == -2:
					Hint["target"] = "down"
				else:
					Hint["target"] = PathIndesPaths[hlink.node2]
				Hint["horizontal"] = True
				Hints.append(Hint)
		
			if len(Hints) > 0:
				Layer["hints"] = Hints
			Anchors = []
			for currAnchor in glyph.anchors:
				Anchor = {}
				Position = currAnchor.Layer(masterIndex)
				Anchor["position"] = "{%f, %f}" % (Position.x, Position.y)
				Anchor["name"] = currAnchor.name
				Anchors.append(Anchor)
			if len(Anchors)>0:
				Layer["anchors"] = Anchors
				
			Layers.append(Layer)
		Glyph["layers"] = Layers
		if glyph.unicode > 1:
			Glyph["unicode"] = ("%.4X" % glyph.unicode)
		Glyphs.append(Glyph)
		#else:
		#print glyph.name
	Font["glyphs"] = Glyphs
	Font["kerning"] = Kerning
	return Font
	
def main():
	StartTime = time.clock()
	font = fl.font
	
	path = font.file_name
	if path is None:
		from robofab.interface.all.dialogs import PutFile
		path = PutFile("Please choose a name for the .glyph")
		if path is None:
			return
	folder, base = os.path.split(path)
	#base = base.split(".")[0] + ".glyphs"
	base = base.replace(".vfb", ".glyphs")
	dest = os.path.join(folder, base)
	makePlist(font).write(dest)
	print "export Time:", (time.clock() - StartTime), "s."

if __name__ == '__main__':
	main()

