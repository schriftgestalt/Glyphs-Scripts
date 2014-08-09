#FLM: Glyphs Export
# -*- coding: utf8 -*-
# Version 0.6 (1. April 2014)
# copyright Georg Seifert 2014, schriftgestaltung.de
# 
# please install it to: /Library/Application Support/FontLab/Studio 5/Macros/Glyphs Export.py
# 
# The scrit will write a .glyphs file at the same loaction than the .vfb file.
# This preserves hints/links, kerning and Multiple Masters.
# if you find any bugs, please report to info@glyphsapp.com

import os.path
import math, time
from plistlib import *
import colorsys
from FL import *

def convertFLSToUnicode(Value):
	Uni = None
	try:
		Uni = Value.decode("UTF-8")
	except:
		try:
			Uni = unicode(Value, 'cp1252')
		except:
			pass
	return Uni

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
			key = None
			for j in range(1, len(elements)):
				if len(elements[j]) > 0:
					if elements[j][-1] == "'":
						key = elements[j][:-1]
						TargetGlyphs.append(key)
					else:
						TargetGlyphs.append( elements[j])
			if key == None:
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
	Font = Plist ()
	if font.pref_family_name is not None:
		Font["familyName"] = font.pref_family_name
	elif font.family_name is not None:
		Font["familyName"] = font.family_name
	
	WeightValues = {
		"Thin" : 250,
		"ExtraLight" : 250,
		"UltraLight" : 250,
		"Light" : 300,
		"Normal" : 400,
		"Regular" : 400,
		"Medium" : 500,
		"SemiBold" : 600,
		"DemiBold" : 600,
		"Bold" : 700,
		"ExtraBold" : 800,
		"UltraBold" : 800,
		"Black" : 900,
		"Heavy" : 900,
		"Fat" : -1,
		"ExtraBlack" : -1,
	}
	WidthMap = {
		"Ultra-condensed" : "Ultra Condensed",
		"Extra-condensed" : "Extra Condensed",
		"Condensed" : "Condensed",
		"Semi-condensed" : "SemiCondensed",
		"Normal" : "Medium (normal)",
		"Medium (normal)" : "Medium (normal)",
		"Semi-expanded" : "Semi Expanded",
		"Expanded" : "Expanded",
		"Extra-expanded" : "Extra Expanded",
		"Ultra-expanded" : "Ultra Expanded"
	}
	
	
	Instance = {}
	if font.pref_style_name is not None:
		Instance["name"] = font.pref_style_name
	elif font.style_name is not None:
		Instance["name"] = font.style_name
	if font.weight and len(font.weight) > 0:
		Instance["weightClass"] = font.weight
	if font.width and len(font.width) > 0 and font.width in WidthMap.keys():
		Instance["widthClass"] = WidthMap[font.width]

	CustomParameters = []
	# if font.ttinfo.os2_us_weight_class != WeightValues[font.weight]: # There seems to be a bug, os2_us_weight_class is always 400
	# 	CustomParameters.append({"name":"openTypeOS2WeightClass", "value": font.ttinfo.os2_us_weight_class})
	if len(CustomParameters) > 0:
		Instance["customParameters"] = CustomParameters
	
	fontStyle = font.font_style
	if (fontStyle & 1) == 1:
		Instance["isItalic"] = 1
	if (fontStyle & 32) == 32:
		Instance["isBold"] = 1
	
	if len(Instance) > 0:
		Font["instances"] = [Instance]
	
	
	Font["gridLength"] = 1
	Font["unitsPerEm"] = font.upm
	FontMasters = []
	
	# Font Info
	FontInfoMapping = {
		"designer":"designer",
		"designer_url":"designerURL",
		"source":"manufacturer",
		"vendor_url":"manufacturerURL",
		"copyright":"copyright"
	}
	for FLKey, GlyphsKey in FontInfoMapping.iteritems():
		Value = getattr(font, FLKey)
		if Value and len(Value) > 0:
			Value = convertFLSToUnicode(Value)
			if Value is not None:
				Font[GlyphsKey] = Value
			else:
				print "!!  invalid character or encoding in Font Info field: ", FLKey
					
	CustomParametersMapping = {
		"trademark":"trademark",
		"notice":"description",
		"license":"license",
		"license_url":"licenseURL",
		#"vendor":"openTypeOS2VendorID",
	}
	
	Sec = getattr(font.ttinfo, "head_creation")[0]
	if Sec < 0:
		Font["date"] = time.strftime("%Y-%m-%d %H:%M:%S +0000", time.gmtime(Sec + 2212126081))#"2013-04-01 21:32:44 +0000";
		
		# head_creation [-2147483596,0] kleinster vorkommender Wert. 
		# head_creation [ 2147483400,0] wenn fünf Minuten früher dann kommt das dabei heraus.
		
	Font["versionMajor"] = font.version_major
	Font["versionMinor"] = font.version_minor
	
	CustomParameters = []
	for FLKey, GlyphsKey in CustomParametersMapping.iteritems():
		Value = None
		if len(FLKey.split(".")) > 1:
			FLKeyList = FLKey.split(".")
			obj = font
			for Key in FLKeyList:
				obj = getattr(obj, Key)
			Value = obj
		else:
			Value = getattr(font, FLKey)
		if Value and len(Value) > 0:
			Value = convertFLSToUnicode(Value)
			if Value is not None:
				CustomParameters.append({"name":GlyphsKey, "value": Value})
			else:
				print "!!! invalid character or encoding in Font Info field: ", FLKey
	
	if font.vendor and len(font.vendor) > 0 and font.vendor.upper() != "PYRS":
		CustomParameters.append({"name":"openTypeOS2VendorID", "value": font.vendor.decode('UTF-8')})
	fsType = font.ttinfo.os2_fs_type
	fsTypeList = []
	
	
	if fsType & 2 == 2:
		fsTypeList.append(1)
	if fsType & 4 == 4:
		fsTypeList.append(2)
	if fsType & 8 == 8:
		fsTypeList.append(3)
	if fsType & 256 == 256:
		fsTypeList.append(8)
	
	if len(fsTypeList) > 0:
		CustomParameters.append({"name":"openTypeOS2Type", "value": fsTypeList})
	
	GlyphOrder = []
	for glyph in font.glyphs:
		if glyph.name != ".notdef":
			GlyphOrder.append(glyph.name)
	CustomParameters.append({"name":"glyphOrder", "value": GlyphOrder})
	
	if len(CustomParameters) > 0:
		Font["customParameters"] = CustomParameters
	
	Font["disablesAutomaticAlignment"] = True
	print "Font is written with \"Disables Automatic Alignment\" activated. Please review this setting in Font Info."

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
		for j in range(AlignmentCount-1, 0, -2):
			FontMaster["alignmentZones"].append("{%d, %d}" %( font.blue_values[i][j-1] , font.blue_values[i][j] - font.blue_values[i][j-1]))
		
		AlignmentCount = font.other_blues_num
		
		for j in range(AlignmentCount-1, 0, -2):
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
		
		if LeftKey:
			Glyph["rightKerningGroup"] = LeftKey
		if RightKey:
			Glyph["leftKerningGroup"] = RightKey
		
		if len(glyph.kerning) > 0:
			for kerningPair in glyph.kerning:
				firstKey = glyph.name
				secondGlyph = f.glyphs[kerningPair.key]
				secondKey = secondGlyph.name
				# add Kerning classes!!!!
				if firstKey in FirstClasses:
					firstKey = "@MMK_L_"+firstKey
				
				if secondKey in SecondClasses:
					secondKey = "@MMK_R_"+secondKey
				
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
			
			if Nodes:
				if Nodes[-1].find("CURVE") > 0:
					LastParts = Nodes[-1].split(" ")
					FirstParts = Nodes[0].split(" ")
					if FirstParts[0] == LastParts[0] and FirstParts[1] == LastParts[1]:
						Nodes.pop(0)
				Paths.append({"nodes": Nodes, "closed":True})
			Layer["paths"] = Paths
		
			Hints = []
			for vhint in glyph.vhints:
				Hint = {}
				Hint["place"] = "{%d, %d}" % (vhint.positions[masterIndex], vhint.widths[masterIndex])
				Hints.append(Hint)
			for hhint in glyph.hhints:
				Hint = {}
				Hint["place"] = "{%d, %d}" % (hhint.positions[masterIndex], hhint.widths[masterIndex])
				if hhint.widths[masterIndex] == -20:
					Hint["target"] = "down"
				if hhint.widths[masterIndex] == -21:
					Hint["target"] = "up"
				Hint["horizontal"] = True
				Hints.append(Hint)
			for vlink in glyph.vlinks:
				Hint = {}
				Hint["origin"] = PathIndesPaths[vlink.node1]
				Hint["target"] = PathIndesPaths[vlink.node2]
				Hints.append(Hint)
			for hlink in glyph.hlinks:
				Hint = {}
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
				Anchor["position"] = "{%d, %d}" % (Position.x, Position.y)
				Anchor["name"] = currAnchor.name
				Anchors.append(Anchor)
			if len(Anchors)>0:
				Layer["anchors"] = Anchors
				
			# Read Background
			Nodes = False
			glyph = glyph.mask
			Paths = []
			for i in range(len(glyph)):
				node = glyph.nodes[i].Layer(masterIndex)
				if glyph.nodes[i].type == nMOVE:
					if Nodes:
						if Nodes[-1].find("CURVE") > 0:
							LastParts = Nodes[-1].split(" ")
							FirstParts = Nodes[0].split(" ")
							if FirstParts[0] == LastParts[0] and FirstParts[1] == LastParts[1]:
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
			
			if Nodes:
				if Nodes[-1].find("CURVE") > 0:
					LastParts = Nodes[-1].split(" ")
					FirstParts = Nodes[0].split(" ")
					if FirstParts[0] == LastParts[0] and FirstParts[1] == LastParts[1]:
						Nodes.pop(0)
				Paths.append({"nodes": Nodes, "closed":True})
			if len(Paths) > 0:
				Layer["background"] = {"paths" : Paths}
			Layers.append(Layer)
		Glyph["layers"] = Layers
		if glyph.unicode > 1:
			Glyph["unicode"] = ("%.4X" % glyph.unicode)
			
		if glyph.mark > 0:
			
			r, g, b = colorsys.hsv_to_rgb(glyph.mark/256., 1., 1.)
			Glyph["color"] = [int(r * 255), int(g*255), int(b*255), 1]
		
		Glyphs.append(Glyph)
	Font["glyphs"] = Glyphs
	Font["kerning"] = Kerning
	return Font
	
def writeFeatures(font, Dict):
	Prefix = {}
	if font.ot_classes is not None and len(font.ot_classes) > 0:
		Prefix["code"] = font.ot_classes.strip()
		Prefix["name"] = "FontLab OTPanel"
		Dict["featurePrefixes"] = [Prefix]
	
	Classes = []
	for i in range(len(font.classes)):
		ClassText = font.classes[i]
		if ClassText[0] != "_" and ClassText[0] != ".":
			ClassTupel = ClassText.split(":", 1)
			if len(ClassTupel) == 2:
				Class = {}
				Class["name"] = ClassTupel[0].strip()
				Class["code"] = ClassTupel[1].strip()
				Classes.append(Class)
	if len(Classes) > 0:
		Dict["classes"] = Classes
	Features = []
	import re
	p = re.compile("feature ([A-Za-z0-9]{4}) *{[\\s]*([.'\\{\\}\\[\\]a-zA-Z0-9_ ;,:\\s@<>#+-\\/]*?)} *\\1 *;")
	for i in range(len(font.features)):
		FeatureText = font.features[i]
		Feature = {}
		Feature["name"] = FeatureText.tag
		if Feature["name"] == "kern":
			continue
		
		try:
			Match = p.findall(FeatureText.value.decode('utf8','ignore'))
		except:
			print "__ illegal character in feature", FeatureText.tag
		try:
			Feature["code"] = Match[0][1]
			Features.append(Feature)
		except:
			StartIndex = FeatureText.value.find("{")
			EndIndex = FeatureText.value.rfind("}")
			if StartIndex > 0 and EndIndex > 0 and EndIndex > StartIndex:
				Feature["code"] = FeatureText.value[StartIndex+1:EndIndex].strip()
				Features.append(Feature)
				continue
			print "__ Problme with Features:", FeatureText.tag, "\n", FeatureText.value
	if len(Features) > 0:
		Dict["features"] = Features
	return Dict
def main():
	StartTime = time.clock()
	font = fl.font
	
	path = font.file_name
	if path is None:
		from robofab.interface.all.dialogs import PutFile
		path = PutFile("Please choose a name for the .glyph")
		if path is None:
			return
	path = os.path.splitext(path)[0]
	path = path+".glyphs"
	print "Will write font to:", path.decode("utf-8",'ignore')
	Dict = makePlist(font)
	Dict = writeFeatures(font, Dict)
	Dict.write(path)
	print "export Time:", (time.clock() - StartTime), "s."

if __name__ == '__main__':
	main()

