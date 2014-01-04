#FLM: Glyphs Import
# -*- coding: utf8 -*-
# Version 0.2
# copyright Georg Seifert 2012, schriftgestaltung.de
# 
# The script will read a .glyphs file and import it into FontLab.
# It requires FontLab 5.1 on Mac
# if you find any bugs, please report to info@glyphsapp.com

from FL import *
from Foundation import *
from objc import *
import os.path
import math, time
import Nav
import MacOS
import Carbon.File
from plistlib import *

convertName = True
Nice2Legacy = {}
Name2Category = {}
Name2SubCategory = {}

shortStyleList = {"Extra": "Ex", "Condensed": "Cond", "Extended": "Extd", "Semi":"Sm", "Italic": "It", "Bold":"Bd", " Sans":"", " Mono":""}
weightCodes = {}
def NotNiceName(Name):
	Suffix = ""
	if "." in Name:
		Name, Suffix = Name.split(".", 1)
	if convertName and Name in Nice2Legacy:
		Name = Nice2Legacy[Name]
	else:
		Name = Name.replace("-", "")
	if len(Suffix) > 0:
		Name = Name + "." + Suffix
	return Name

def setInstanceStyleNames(Font, Dict):
	_Familie = str(Dict['familyName'])
	try:
		_Instance = Dict['instances'][0]
	except:
		_Instance = {"name":"Regular"}
	_Schnitt = str(_Instance['name'])
	
	if "linkStyle" in _Instance:
		_FamSchnitt = str(_Instance["linkStyle"]) # für Style linking
	else:
		_FamSchnitt = _Schnitt
	
	try:
		_isBold = bool(_Instance["isBold"])
	except:
		_isBold = False
	try:
		_isItalic = bool(_Instance["isItalic"])
	except:
		_isItalic = False
	
	_Weight = "Regular"
	_Width = "Medium (normal)"
	_Weightcode = 400
	#_Widthcode = 
	if "weightClass" in _Instance:
		_Weight = str(_Instance["weightClass"])
	if "widthClass" in _Instance:
		_Width = str(_Instance["widthClass"])
	if _Weight in weightCodes:
		_Weightcode = int(weightCodes[_Weight])
	
	if "customParameters" in _Instance:
		_CustomParameters = _Instance["customParameters"]
		for Parameter in _CustomParameters:
			if Parameter["name"] == "openTypeOS2WeightClass":
				_Weightcode = int(Parameter["value"])
			if Parameter["name"] == "openTypeOS2WidthClass":
				_Widthcode = int(Parameter["value"])
	Font.weight = _Weight
	Font.weight_code = _Weightcode
	Font.width = _Width
	#Font.width_code = _Widthcode
	
	_Flag = 0
	if _isBold:
		_Flag = 32
	if _isItalic:
		_Flag = _Flag + 1
		
	Font.font_style = _Flag
	
	if _Flag == 1:
		_WinStyle = "Italic"
	elif _Flag == 32:
		_WinStyle = "Bold"
	elif _Flag == 33:
		_WinStyle = "Bold Italic"
	else:
		_WinStyle = "Regular"
	
	_WinFamily = _Schnitt.replace(_WinStyle, "")
	if len(_WinFamily) > 0 :
		_WinFamily = " " + _WinFamily
		if _WinFamily[-1] == " ":
			_WinFamily = _WinFamily[0:-1]
	_shortStyle = _Schnitt
	for any in shortStyleList:
		if len(_Familie + " " + _shortStyle) <= 28:
			break
		_shortStyle = _shortStyle.replace(any, shortStyleList[any])
	_postscriptName = _Familie + "-" + _shortStyle
	_postscriptName = _postscriptName.replace(" ", "")
	print _postscriptName
	Font.family_name = _Familie
	Font.style_name = _WinStyle
	
	Font.full_name = _Familie + " " + _Schnitt
	Font.font_name = _postscriptName
	Font.menu_name = _Familie + " " + _Schnitt
	Font.apple_name = _postscriptName
	Font.pref_style_name = _Schnitt
	Font.pref_family_name = _Familie
	
	Font.mac_compatible = ""
	Font.menu_name = ""
	
	Font.fontnames.clean()
	try:
		Font.fontnames.append(NameRecord( 0,1,0,0,		Font.copyright))
		Font.fontnames.append(NameRecord( 0,3,1,1033,	Font.copyright))
	except:
		print "Copyright-Angabe fehlt"
	
	Font.fontnames.append(NameRecord( 1,1,0,0,		_Familie))
	Font.fontnames.append(NameRecord( 1,3,1,1033,	_Familie + _WinFamily))
	Font.fontnames.append(NameRecord( 2,1,0,0,		_Schnitt))
	Font.fontnames.append(NameRecord( 2,3,1,1033,	_WinStyle))
	Font.fontnames.append(NameRecord( 3,1,0,0,		"%s: %s %s, %d" % (Font.designer, _Familie, _Schnitt, Font.year)))
	Font.fontnames.append(NameRecord( 3,3,1,1033,	"%s: %s %s, %d" % (Font.designer, _Familie, _Schnitt, Font.year)))
	if _Schnitt == "Regular":
		Font.fontnames.append(NameRecord( 4,1,0,0,	_Familie))
	else:
		Font.fontnames.append(NameRecord( 4,1,0,0,	_Familie + " " + _Schnitt))
	Font.fontnames.append(NameRecord( 4,3,1,1033,	_Familie + " " + _Schnitt))
	try:
		Font.fontnames.append(NameRecord( 5,1,0,0,		Font.version))
		Font.fontnames.append(NameRecord( 5,3,1,1033,	Font.version))
	except:
		print "Version-Angabe fehlt"
	Font.fontnames.append(NameRecord( 6,1,0,0,		_postscriptName))
	Font.fontnames.append(NameRecord( 6,3,1,1033,	_postscriptName))
	try:
		Font.fontnames.append(NameRecord( 7,1,0,0,		Font.trademark))
		Font.fontnames.append(NameRecord( 7,3,1,1033,	Font.trademark))
	except:
		print "Trademark-Angabe fehlt"
	try:
		Font.fontnames.append(NameRecord( 9,1,0,0,		Font.designer))
		Font.fontnames.append(NameRecord( 9,3,1,1033,	Font.designer))
	except:
		print "Trademark-Angabe fehlt"
	try:
		Font.fontnames.append(NameRecord( 11,1,0,0,	Font.vendor_url))
		Font.fontnames.append(NameRecord( 11,3,1,1033,	Font.vendor_url))
	except:
		print "Vendor-URL-Angabe fehlt"
	try:
		Font.fontnames.append(NameRecord( 12,1,0,0,	Font.designer_url))
		Font.fontnames.append(NameRecord( 12,3,1,1033,	Font.designer_url))
	except:
		print "Trademark-Angabe fehlt"
	Font.fontnames.append(NameRecord( 16,3,1,1033,	_Familie))
	Font.fontnames.append(NameRecord( 17,3,1,1033,	_Schnitt))
	if len(_Familie + " " + _Schnitt) >= 28:
		Font.fontnames.append(NameRecord( 18,1,0,0, _Familie + " " + _shortStyle))
	

def setFontInfo(Font, Dict):
	KeyTranslate = {
		"familyName" : ("family_name", str),
		"versionMajor" : ("version_major", int),
		"versionMinor": ("version_minor", int),
		"unitsPerEm" : ("upm", int),
		"copyright" : ("copyright", unicode),
		"designer" : ("designer", unicode),
		"designerURL" : ("designer_url", unicode),
		"manufacturer" : ("vendor", unicode),
		"manufacturerURL" : ("vendor_url", unicode),
	}
	for Key in KeyTranslate:
		if Key in Dict.allKeys():
			FlKey, FlType = KeyTranslate[Key]
			if FlType == unicode:
				setattr(Font, FlKey, unicode(Dict[Key]).encode("utf-8"))
			elif FlType == str:
				setattr(Font, FlKey, str(Dict[Key]))
			elif FlType == int:
				setattr(Font, FlKey, int(Dict[Key]))
	if "date" in Dict:
		try:
			import datetime
			Date = datetime.datetime.strptime(Dict["date"][:-6], "%Y-%m-%d %H:%M:%S") #2004-03-02 15:27:47 +0100
			Font.year = int(Date.year)
		except:
			Font.year = int(Dict["date"][:4])
	if "versionMajor" in Dict and "versionMinor" in Dict:
		Font.version = "%d.%03d" % (Font.version_major, Font.version_minor)
	FontMasters = Dict["fontMaster"]
	
	if len(FontMasters) == 1:
		setInstanceStyleNames(Font, Dict)
	else:
		Font.weight = "All"
	MasterCount = len(FontMasters)
	
	for FontMaster in FontMasters:
		if "weight" not in FontMaster.keys():
			FontMaster["weight"] = "Regular"
	
	if MasterCount == 1:
		pass
	elif MasterCount == 2:
		if FontMasters[0]["weight"] != FontMasters[1]["weight"]:
			Font.DefineAxis("Weight", "Weight", "Wt")
		else:
			Font.DefineAxis("Width", "Width", "Wd")
	elif MasterCount == 4:
		if FontMasters[0]["weight"] != FontMasters[1]["weight"]:
			Font.DefineAxis("Weight", "Weight", "Wt")
			Font.DefineAxis("Width", "Width", "Wd")
		else:
			Font.DefineAxis("Width", "Width", "Wd")
			Font.DefineAxis("Weight", "Weight", "Wt")
		print "Please check the arrangement of the axis and masters. The association of the Glyphs masters might not fit."
	else:
		print "Fonts with a master count of %d are not supported" % MasterCount
		return False
	
	KeyTranslate = {
		"postscriptIsFixedPitch" : ("is_fixed_pitch", bool),
		"postscriptUnderlinePosition" : ("underline_position", int),
		"postscriptUnderlineThickness" : ("underline_thickness", int),
		#"openTypeOS2StrikeoutSize" : ("ttinfo.os2_y_strikeout_size", int),
		#"openTypeOS2StrikeoutPosition" : ("ttinfo.os2_y_strikeout_position", int),
		"openTypeNameLicense" : ("license", unicode),
		"openTypeNameLicenseURL" : ("license_url", unicode),
		"openTypeOS2Type" : ("ttinfo.os2_fs_type", "fsType")
	}
	if "customParameters" in Dict:
		for Parameter in Dict["customParameters"]:
			Name = Parameter["name"]
			Value = Parameter["value"]
			try:
				FlKey, FlType = KeyTranslate[Name]
				if Name in KeyTranslate:
					if FlType == str:
						setattr(Font, FlKey, str(Value))
					elif FlType == int:
						setattr(Font, FlKey, int(Value))
					elif FlType == unicode:
						setattr(Font, FlKey, unicode(Value).encode("utf-8"))
					elif FlType == bool:
						setattr(Font, FlKey, bool(Value))
					elif FlType == "fsType":
						fs_type = 0
						for Bit in Value:
							fs_type = fs_type + 2**int(Bit)
						Font.ttinfo.os2_fs_type = int(fs_type)
			except:
				pass
	for i in range(MasterCount):
			Font.ascender[i] = int(FontMasters[i]["ascender"])
			Font.descender[i] = int(FontMasters[i]["descender"])
			Font.cap_height[i] = int(FontMasters[i]["capHeight"])
			Font.x_height[i] = int(FontMasters[i]["xHeight"])
			if "italicAngle" in FontMasters[i]:
				Font.italic_angle = float(FontMasters[i]["italicAngle"])
			
			if "horizontalStems" in FontMasters[i]:
				if i == 0:
					Font.stem_snap_h_num = len(FontMasters[i]["horizontalStems"])
				for j in range(len(FontMasters[i]["horizontalStems"])):
					Font.stem_snap_h[i][j] = int(FontMasters[i]["horizontalStems"][j])
			
			if "verticalStems" in FontMasters[i]:
				if i == 0:
					Font.stem_snap_v_num = len(FontMasters[i]["verticalStems"])
				for j in range(len(FontMasters[i]["verticalStems"])):
					Font.stem_snap_v[i][j] = int(FontMasters[i]["verticalStems"][j])
			
			if "alignmentZones" in FontMasters[i]:
				BlueZones = []
				OtherZones = []
				for ZoneString in FontMasters[i]["alignmentZones"]:
					Zone = str(ZoneString)[1:-1].split(", ")
					Zone = map(int, Zone)
					
					if Zone[1] < 0 and Zone[0] != 0:
						OtherZones.append(Zone[0])
						OtherZones.append(Zone[0] + Zone[1])
					else:
						BlueZones.append(Zone[0])
						BlueZones.append(Zone[0] + Zone[1])
				if len(BlueZones) >= 14:
					BlueZones = BlueZones[:13]
					print "Warning: There are to many Blue Zones."
				if i == 0:
					Font.blue_values_num = len(BlueZones)
					Font.other_blues_num = len(OtherZones)
				
				for j in range(Font.blue_values_num):
					Font.blue_values[i][j] = BlueZones[j]
				for j in range(Font.other_blues_num):
					Font.other_blues[i][j] = OtherZones[j]
	return True

def applicationSupportFolder(appname=u"Glyphs"):
	paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,True)
	basePath = (len(paths) > 0 and paths[0]) or NSTemporaryDirectory()
	fullPath = basePath.stringByAppendingPathComponent_(appname)
	if not os.path.exists(fullPath):
		return None
	return fullPath

def parseGlyphDataFile(Path):
	try:
	from xml.etree import ElementTree as ET
		element = ET.parse(Path)
	
	for subelement in element.getiterator():
		Attribs = subelement.attrib
		if "legacy" in Attribs:
			Nice2Legacy[Attribs["name"]] = Attribs["legacy"]
		if "category" in Attribs:
			Name2Category[Attribs["name"]] = Attribs["category"]
		if "subCategory" in Attribs:
			Name2SubCategory[Attribs["name"]] = Attribs["subCategory"]
	except:
		print "there was a problem reading the GlyphData.xml file. Probably because you did not have a copy of Glyphs in the application folder.(%s)" % Path

def loadGlyphsInfo():
	try:
		GlyphsPath = NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_("com.GeorgSeifert.Glyphs")
		if GlyphsPath is None:
			GlyphsPath = NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_("com.schriftgestaltung.Glyphs")
		if GlyphsPath is None:
			GlyphsPath = NSWorkspace.sharedWorkspace().URLForApplicationWithBundleIdentifier_("com.schriftgestaltung.GlyphsMini")
		GlyphsPath = GlyphsPath.path()
	except:
		return
	
	if GlyphsPath is not None:
		GlyphsInfoPath = GlyphsPath+"/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources/GlyphData.xml"
		WeightCodesPath = GlyphsPath+"/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources/weights.plist"
	
	parseGlyphDataFile(GlyphsInfoPath)
	
	CustomGlyphsInfoPath = applicationSupportFolder()
	if CustomGlyphsInfoPath:
		CustomGlyphsInfoPath = CustomGlyphsInfoPath.stringByAppendingPathComponent_("/Info/GlyphData.xml")
		parseGlyphDataFile(CustomGlyphsInfoPath)
	
	global weightCodes
	weightCodes = NSDictionary.alloc().initWithContentsOfFile_(WeightCodesPath)
	
def fixNodes(Nodes):
	while "OFFCURVE" in Nodes[-1]:
		Node = Nodes[-1]
		Nodes.insert(0, Nodes.pop(Nodes.index(Node)))
	return Nodes
	
def _isNonSpacingMark(Name):
	try:
		Category = Name2Category[Name]
		SubCategory = Name2SubCategory[Name]
	except:
		try:
			Name = Name[:Name.find(".")]
			Category = Name2Category[Name]
			SubCategory = Name2SubCategory[Name]
		except:
			return False
	
	return Category == "Mark" and SubCategory == "Nonspacing"

def checkForNestedComponentsAndDecompose(Font, glyph, MasterCount):
	ComponentCount = len(glyph.components)
	DidDecompose = False
	for ComponentIndex in range(ComponentCount-1, -1, -1):
		component = glyph.components[ComponentIndex]
		ComponentGlyph = Font.glyphs[component.index]
		if len(ComponentGlyph.components) > 0:
			
			print "__ needs decompostion", glyph.name
			for ComponentGlyphComponent in ComponentGlyph.components:
				CopyComponent = Component(ComponentGlyphComponent)
				print "__ComponentGlyphComponent", ComponentGlyphComponent
				for masterIndex in range(MasterCount):
					print "Decompose", CopyComponent.deltas[masterIndex].x, component.scales[masterIndex].x, component.deltas[masterIndex].x
					CopyComponent.scales[masterIndex].x = CopyComponent.scales[masterIndex].x * component.scales[masterIndex].x
					CopyComponent.scales[masterIndex].y = CopyComponent.scales[masterIndex].y * component.scales[masterIndex].y
					CopyComponent.deltas[masterIndex].x = (CopyComponent.deltas[masterIndex].x * component.scales[masterIndex].x) + component.deltas[masterIndex].x
					CopyComponent.deltas[masterIndex].y = (CopyComponent.deltas[masterIndex].y * component.scales[masterIndex].y) + component.deltas[masterIndex].y
				glyph.components.append(CopyComponent)
			del(glyph.components[ComponentIndex])
			
			ComponentGlyphPath = ComponentGlyph.nodes
			NewPath = []
			for node in ComponentGlyphPath:
				NewPath.append(Node(node))
			
			for ComponentNode in ComponentGlyph.nodes:
				node = Node(ComponentNode)
				for masterIndex in range(MasterCount):
					for pointIndex in range(node.count):
						node.Layer(masterIndex)[pointIndex].x = (node.Layer(masterIndex)[pointIndex].x * component.scales[masterIndex].x) + component.deltas[masterIndex].x
						node.Layer(masterIndex)[pointIndex].y = (node.Layer(masterIndex)[pointIndex].y * component.scales[masterIndex].y) + component.deltas[masterIndex].y
				glyph.Insert(node, len(glyph))
			DidDecompose = True
	return DidDecompose

def readGlyphs(Font, Dict):
	Glyphs = Dict["glyphs"]
	GlyphsCount = len(Glyphs)
	FontMasters = Dict["fontMaster"]
	MasterCount = len(FontMasters)
	GlyphIndexes = {}
	for i in range(GlyphsCount):
		
		GlyphDict = Glyphs[i]
		glyph = Glyph(MasterCount)
		glyph.name = str(GlyphDict["glyphname"])
		if "unicode" in GlyphDict.keys():
			glyph.unicode = int(GlyphDict["unicode"], 16)
		if "export" in GlyphDict.keys() and str(GlyphDict["export"]) == "0":
			glyph.customdata = "Not Exported"
			glyph.mark = 2
		isNonSpacingMark = False
		try:
			isNonSpacingMark = Name2Category[glyph.name] == "Mark" and Name2SubCategory[glyph.name] == "Nonspacing"
		except:
			pass
		for masterIndex in range(MasterCount):
			FontMaster = FontMasters[masterIndex]
			Layer = None
			try:
				for Layer in GlyphDict["layers"]:
					if Layer["layerId"] == FontMaster["id"]:
						break
			except:
				continue
			ShiftNodes = 0
			if isNonSpacingMark:
				ShiftNodes = round(float(Layer["width"]))
				glyph.SetMetrics(Point(0, 0), masterIndex)
			else:
				glyph.SetMetrics(Point(round(float(Layer["width"])), 0), masterIndex)
			
			if "paths" not in Layer.keys():
				continue
			nodeIndex = 0
			lastMoveNodeIndex = 0
			for PathIndex in range(len(Layer["paths"])):
				Path = Layer["paths"][PathIndex]
				Nodes = Path["nodes"]
				Nodes = fixNodes(Nodes)
				NodeString = Nodes[-1]
				NodeList = NodeString.split(" ")
				Position = Point(round(float(NodeList[0])) - ShiftNodes, round(float(NodeList[1])))
				if masterIndex == 0:
					node = Node(nMOVE, Position)
					glyph.Insert(node, len(glyph))
				else:
					Index = nodeIndex
					if Index > len(glyph):
						Index = Index - len(glyph)
					try:
						glyph.nodes[Index].Layer(masterIndex)[0].x = Position.x
						glyph.nodes[Index].Layer(masterIndex)[0].y = Position.y
					except:
						continue # if the master has more paths then the first master
				firstPoint = Position
				firstNodeIndex = nodeIndex
				nodeIndex = nodeIndex + 1
				OffcurveNodes = []
				for NodeString in Nodes:
					NodeList = NodeString.split(" ")
					Position = Point(round(float(NodeList[0])) - ShiftNodes, round(float(NodeList[1])))
					node = None
					if NodeList[2] == "LINE":
						if masterIndex == 0:
							node = Node(nLINE, Position)
							try:
								if NodeList[3] == "SMOOTH":
									node.alignment = nSMOOTH
							except:
								pass
							glyph.Insert(node, len(glyph))
						else:
							Index = nodeIndex
							if Index >= len(glyph):
								Index = Index - len(glyph)
							
							glyph.nodes[Index].Layer(masterIndex)[0].x = Position.x
							glyph.nodes[Index].Layer(masterIndex)[0].y = Position.y
						nodeIndex = nodeIndex + 1
					elif NodeList[2] == "CURVE":
						if len(OffcurveNodes) == 2:
							if masterIndex == 0:
								node = Node(nCURVE, Position)
								try:
									if NodeList[3] == "SMOOTH":
										node.alignment = nSMOOTH
								except:
									pass
								node.points[1].x = OffcurveNodes[0].x
								node.points[1].y = OffcurveNodes[0].y
								node.points[2].x = OffcurveNodes[1].x
								node.points[2].y = OffcurveNodes[1].y
								glyph.Insert(node, len(glyph))
							else:
								Index = nodeIndex
								if Index >= len(glyph):
									Index = Index - len(glyph) + 1
								
								Points = glyph.nodes[Index].Layer(masterIndex)
								if len(Points) == 3:
									Points[0].x = Position.x
									Points[0].y = Position.y
									Points[1].x = OffcurveNodes[0].x
									Points[1].y = OffcurveNodes[0].y
									Points[2].x = OffcurveNodes[1].x
									Points[2].y = OffcurveNodes[1].y
							nodeIndex = nodeIndex + 1
						OffcurveNodes = []
						
						
					elif NodeList[2] == "OFFCURVE":
						OffcurveNodes.append(Point(round(float(NodeList[0])) - ShiftNodes, round(float(NodeList[1]))))
					
				if "closed" in Path and masterIndex == MasterCount-1:
					# we may have output a node too much
					node = glyph[nodeIndex-1]
					firstNode = glyph[firstNodeIndex]
					if node is not None and firstNodeIndex is not None:
						if node.x == firstNode.x and node.y == firstNode.y:
							if node.type == nLINE:
								glyph.DeleteNode(nodeIndex-1)
								nodeIndex = nodeIndex - 1
							elif node.type == nCURVE and glyph[firstNodeIndex+1].type != nCURVE:
								glyph.DeleteNode(firstNodeIndex)
								nodeIndex = nodeIndex - 1
					else:
						print "There was a problem with the outline in the glyph: \"%s\". Probably because the outlines are not compatible." % glyph.name
						glyph.mark = 34
			
			if "hints" in Layer.keys():
				vHintIndex = 0
				hHintIndex = 0
				for HintIndex in range(len(Layer["hints"])):
					HintDict = Layer["hints"][HintIndex]
					Horizontal = "horizontal" in HintDict
					if "target" in HintDict and "origin" in HintDict: # add Links
						if masterIndex > 0:
							continue
						FlNodeIndex1 = None
						FlNodeIndex2 = None
						PathIndex, NodeIndex = HintDict["origin"][1:-1].split(", ")
						PathIndex = int(PathIndex)
						NodeIndex = int(NodeIndex)
						PathCounter = -1
						NodeCounter = 0
						for i in range(len(glyph)):
							node = glyph[i]
							
							if node.type == nMOVE:
								PathCounter = PathCounter + 1
							if PathCounter >= PathIndex:
								NodeCounter = NodeCounter + node.count
							if NodeCounter > NodeIndex:
								FlNodeIndex1 = i
								break
						if HintDict["target"][0] == "{":
							PathIndex, NodeIndex = HintDict["target"][1:-1].split(", ")
							PathIndex = int(PathIndex)
							NodeIndex = int(NodeIndex)
							PathCounter = -1
							NodeCounter = 0
							for i in range(len(glyph)):
								node = glyph[i]
								if node.type == nMOVE:
									PathCounter = PathCounter + 1
								if PathCounter >= PathIndex:
									NodeCounter = NodeCounter + node.count
								if NodeCounter > NodeIndex:
									FlNodeIndex2 = i
									break
						elif HintDict["target"] == "down":
							FlNodeIndex2 = -2
						elif HintDict["target"] == "up":
							FlNodeIndex2 = -1
						if FlNodeIndex1 != None and FlNodeIndex2 != None:
							link = Link(FlNodeIndex1, FlNodeIndex2)
							if Horizontal:
								glyph.hlinks.append(link)
							else:
								glyph.vlinks.append(link)
					elif "place" in HintDict:
						Origin, Size = HintDict["place"][1:-1].split(", ")
						Origin = int(round(float(Origin)))
						Size = int(round(float(Size)))
						if masterIndex == 0:
							
							if Horizontal:
								hint = Hint(Origin, Size)
								glyph.hhints.append(hint)
							else:
								Origin = Origin - ShiftNodes
								hint = Hint(Origin, Size)
								glyph.vhints.append(hint)
						else:
							if Horizontal:
								hint = glyph.hhints[hHintIndex]
								hint.positions[masterIndex] = Origin
								hint.widths[masterIndex] = Size
								hHintIndex = hHintIndex + 1
							else:
								hint = glyph.vhints[vHintIndex]
								hint.positions[masterIndex] = Origin
								hint.widths[masterIndex] = Size
								vHintIndex = vHintIndex + 1
			if "anchors" in Layer.keys():
				for AnchorIndex in range(len(Layer["anchors"])):
					# print "__nodeIndex:", nodeIndex
					AnchorDict = Layer["anchors"][AnchorIndex]
					Name = str(AnchorDict["name"])
					X, Y = AnchorDict["position"][1:-1].split(", ")
					X = round(float(X)) - ShiftNodes
					Y = round(float(Y))
					if masterIndex == 0:
						anchor = Anchor(Name, X, Y)
						# print "Move __node", node
						glyph.anchors.append(anchor)
					else:
						Index = nodeIndex
						#print "_set move point", Index, Position, glyph.nodes #, glyph.nodes[Index].Layer(masterIndex)
						try:
							glyph.anchors[AnchorIndex].Layer(masterIndex).x = X
							glyph.anchors[AnchorIndex].Layer(masterIndex).y = Y
						except:
							continue
				
		Font.glyphs.append(glyph)
		GlyphIndexes[glyph.name] = len(Font.glyphs)-1
	
	# Read the components. 
	for i in range(GlyphsCount):
		glyph = Font.glyphs[i]
		GlyphDict = Glyphs[i]
		for masterIndex in range(MasterCount):
			FontMaster = FontMasters[masterIndex]
			try:
				for Layer in GlyphDict["layers"]:
					if Layer["layerId"] == FontMaster["id"]:
						break
			except:
				continue
			try:
				if "components" in Layer.keys():
					for componentIndex in range(len(Layer["components"])):
						try:
							componentDict = Layer["components"][componentIndex]
						except:
							continue
						ShiftNodes = 0
						
						# reconstruct the correct positioning of Nonspacing marks. They where set to zero width on outline import.
						try:
							isNonSpacingMarkComponent = _isNonSpacingMark(componentDict['name'])
							if isNonSpacingMarkComponent:
								ComponentIndex = GlyphIndexes[componentDict['name']]
								ComponentGlyphDict = Glyphs[ComponentIndex]
								ShiftNodes = float(str(ComponentGlyphDict['layers'][masterIndex]["width"]))
						except:
							pass
						
						# if the glyph itself is a nonspacing mark, move the component
						try:
							isNonSpacingMark = _isNonSpacingMark(glyph.name)
							if isNonSpacingMark:
								ShiftNodes -= float(str(Layer["width"]))
						except Exception, e:
							print e
						componentTransformString = componentDict["transform"][1:-1]
						componentTransformList = componentTransformString.split(", ")
						
						if masterIndex == 0:
							ComponentIndex = GlyphIndexes[componentDict['name']]
							Delta = Point(round(float(str(componentTransformList[4]))) + ShiftNodes, round(float(str(componentTransformList[5]))))
							Scale = Point(float(str(componentTransformList[0])), float(str(componentTransformList[3])))
							component = Component(ComponentIndex, Delta, Scale)
							glyph.components.append(component)
						else:
							component = glyph.components[componentIndex]
							component.scales[masterIndex].x = float(str(componentTransformList[0]))
							component.scales[masterIndex].y = float(str(componentTransformList[3]))
							component.deltas[masterIndex].x = round(float(str(componentTransformList[4])) + ShiftNodes)
							component.deltas[masterIndex].y = round(float(str(componentTransformList[5])))
			except:
				print "There was a problem reading the components for glyph:", glyph.name
				
	# Resolve nested components.
	GlyphsWithNestedComponemts = set()
	
	for glyph in Font.glyphs:
		ComponentCount = len(glyph.components)
		for ComponentIndex in range(ComponentCount-1, -1, -1):
			component = glyph.components[ComponentIndex]
			ComponentGlyph = Font.glyphs[component.index]
			if ComponentGlyph.customdata == "Not Exported":
				for ComponentGlyphComponent in ComponentGlyph.components:
					CopyComponent = Component(ComponentGlyphComponent)
					for masterIndex in range(MasterCount):
						CopyComponent.scales[masterIndex].x = CopyComponent.scales[masterIndex].x * component.scales[masterIndex].x
						CopyComponent.scales[masterIndex].y = CopyComponent.scales[masterIndex].y * component.scales[masterIndex].y
						CopyComponent.deltas[masterIndex].x = (CopyComponent.deltas[masterIndex].x * component.scales[masterIndex].x) + component.deltas[masterIndex].x
						CopyComponent.deltas[masterIndex].y = (CopyComponent.deltas[masterIndex].y * component.scales[masterIndex].y) + component.deltas[masterIndex].y
					glyph.components.append(CopyComponent)
				del(glyph.components[ComponentIndex])
				
				ComponentGlyphPath = ComponentGlyph.nodes
				NewPath = []
				for node in ComponentGlyphPath:
					NewPath.append(Node(node))
				for ComponentNode in ComponentGlyph.nodes:
					node = Node(ComponentNode)
					for masterIndex in range(MasterCount):
						for pointIndex in range(node.count):
							node.Layer(masterIndex)[pointIndex].x = (node.Layer(masterIndex)[pointIndex].x * component.scales[masterIndex].x) + component.deltas[masterIndex].x
							node.Layer(masterIndex)[pointIndex].y = (node.Layer(masterIndex)[pointIndex].y * component.scales[masterIndex].y) + component.deltas[masterIndex].y
					glyph.Insert(node, len(glyph))
	
	for glyph in Font.glyphs:
		if checkForNestedComponentsAndDecompose(Font, glyph, MasterCount):
			GlyphsWithNestedComponemts.add(glyph.name)
			checkForNestedComponentsAndDecompose(Font, glyph, MasterCount) # run it again to get double nests.

				
	if len(GlyphsWithNestedComponemts) > 0:
		print "The font has nested components. They are not supported in FontLab and were decomposed.\n(%s)" % ", ".join(sorted(GlyphsWithNestedComponemts))
	fl.UpdateFont()
	
def readKerning(Font, Dict):
	Glyphs = Dict["glyphs"]
	GlyphsCount = len(Glyphs)
	
	GlyphIndexes = {}
	LeftClasses = {}
	RightClasses = {}
	
	for i in range(GlyphsCount):
		GlyphDict = Glyphs[i]
		LeftGroup = None
		try:
			LeftGroup = str(GlyphDict["leftKerningGroup"])
		except:
			pass
		RightGroup = None
		try:
			RightGroup = str(GlyphDict["rightKerningGroup"])
		except:
			pass
		if LeftGroup is not None:
			if LeftGroup in RightClasses.keys():
				RightClasses[LeftGroup].append(str(GlyphDict["glyphname"]))
			else:
				RightClasses[LeftGroup] = [str(GlyphDict["glyphname"])]
		if RightGroup is not None:
			if RightGroup in LeftClasses.keys():
				LeftClasses[RightGroup].append(str(GlyphDict["glyphname"]))
			else:
				LeftClasses[RightGroup] = [str(GlyphDict["glyphname"])]
	AllKeys = LeftClasses.keys()
	AllKeys.sort()
	Classes = []
	for Key in AllKeys:
		Members = LeftClasses[Key]
		Key = Key.replace(".", "_")
		Key = Key.replace("-", "_")
		Member = NotNiceName(Members[0])
		ClassString = "_%s_l: %s'" % (Key, Member)
		for Member in Members[1:]:
			Member = NotNiceName(Member)
			ClassString = ClassString+" "+Member
		Classes.append(ClassString)
	
	AllKeys = RightClasses.keys()
	AllKeys.sort()
	for Key in AllKeys:
		Members = RightClasses[Key]
		Key = Key.replace(".", "_")
		Key = Key.replace("-", "_")
		Member = NotNiceName(Members[0])
		ClassString = "_%s_r: %s'" % (Key, Member)
		for Member in Members[1:]:
			Member = NotNiceName(Member)
			ClassString = ClassString+" "+Member
		Classes.append(ClassString)
	
	Font.classes = Classes
	for i in range(len(Classes)):
		if Classes[i][0] == "_":
			if "_l: " in Classes[i]:
				Font.SetClassFlags(i, True, False)
			if "_r: " in Classes[i]:
				Font.SetClassFlags(i, False, True)
	
	FontMasters = Dict["fontMaster"]
	if "kerning" in Dict.keys():
		Kerning = Dict["kerning"]
		allLeftKeys = set()
		for LeftKeys in Kerning.values():
			allLeftKeys = set.union(allLeftKeys, set(LeftKeys.keys()))
	
		for LeftKey in allLeftKeys:
			LeftGlyph = None
			if LeftKey[0] == "@":
				#@MMK_L_
				try:
					ClassKey = LeftKey[7:]
					GlyphName = LeftClasses[ClassKey][0]
					LeftGlyph = Font[GlyphName]
				except:
					continue
			else:
				LeftGlyph = Font[str(LeftKey)]
			allRightKeys = set()
			for FontMaster in FontMasters:
				try:
					RightKeys = Kerning[FontMaster["id"]][LeftKey].keys()
					allRightKeys = set.union(allRightKeys, set(RightKeys))
				except:
					pass
			for RightKey in allRightKeys:
				RightGlyph = None
				if RightKey[0] == "@":
					#@MMK_R_
					try:
						ClassKey = RightKey[7:]
						GlyphName = RightClasses[ClassKey][0]
						RightGlyph = Font[GlyphName]
					except:
						continue
				else:
					RightGlyph = Font[str(RightKey)]
				KernPair = KerningPair(RightGlyph.index)
			
				for j in range(len(FontMasters)):
					FontMaster = FontMasters[j]
					value = 0
					try:
						value = int(Kerning[FontMaster["id"]][LeftKey][RightKey])
					except:
						pass
					KernPair.values[j] = value
			
				LeftGlyph.kerning.append(KernPair)

def readFeatures(Font, Dict):
	Font.ot_classes = ""
	try:
		for FeatureDict in Dict["featurePrefixes"]:
			if "name" in FeatureDict.keys() and "code" in FeatureDict.keys():
				Font.ot_classes = Font.ot_classes + "# " + str(FeatureDict["name"]) + "\n" + str(FeatureDict["code"]) + "\n"
	except:
		pass
	try:
		Classes = Font.classes
		if "classes" in Dict.keys():
			for FeatureDict in Dict["classes"]:
				if "name" in FeatureDict.keys() and "code" in FeatureDict.keys():
			
					CleanCode = str(FeatureDict["code"])
					CleanCodeList = CleanCode.split(" ")
					CleanCodeList = map(NotNiceName, CleanCodeList)
					CleanCode = " ".join(CleanCodeList)
					Classes.append(str(FeatureDict["name"]) + ": " + CleanCode)
			Font.classes = Classes
		else:
			print "the font has no Classes."
	except:
		print "__ Error in Classes:", sys.exc_info()[0]
		pass
	try:
		if "features" in Dict.keys():
			for FeatureDict in Dict["features"]:
				if "name" in FeatureDict.keys() and "code" in FeatureDict.keys():
						Name = str(FeatureDict["name"])
						try:
							CleanCode = str(unicode(FeatureDict["code"]).encode("utf-8"))
							CleanCode = CleanCode.replace("'", " ~~'")
							CleanCode = CleanCode.replace("]", " ~~]")
							CleanCode = CleanCode.replace("[", "[~~ ")
							CleanCode = CleanCode.replace(";", " ~~;")
							CleanCodeList = CleanCode.split(" ")
							CleanCodeList = map(NotNiceName, CleanCodeList)
							CleanCode = " ".join(CleanCodeList)
							CleanCode = CleanCode.replace(" ~~'", "'")
							CleanCode = CleanCode.replace(" ~~]", "]")
							CleanCode = CleanCode.replace("[~~ ", "[")
							CleanCode = CleanCode.replace(" ~~;", ";")
							CleanCode = CleanCode.replace("\n", "\n	")
					
							feature = Feature(Name, "feature %s {\n	%s\n} %s;" % (Name, CleanCode, Name))
							Font.features.append(feature)
						except:
							print "__ Error in Feature[%s]: %s" % (Name, sys.exc_info()[0])
							pass
		else:
			print "The font has no Feature."
	except:
		print "__ Error in Feature:", sys.exc_info()[0]
	
def setLegacyNames(Font):
	for glyph in Font.glyphs:
		Name = glyph.name
		NewName = NotNiceName(Name)
		if NewName != Name:
			glyph.name = NewName
	
def readGlyphsFile(filePath):
	print "Import Glyphs File"
	pool = NSAutoreleasePool.alloc().init()
	GlyphsDoc = NSDictionary.alloc().initWithContentsOfFile_(filePath)
	
	loadGlyphsInfo()
	from FL import fl, Font
	folder, base = os.path.split(filePath)
	base = base.replace(".glyphs", ".vfb")
	dest = os.path.join(folder, base)
	f = Font(  )
	fl.Add(f)
	global convertName
	try:
		convertName = GlyphsDoc["disablesNiceNames"] != None
	except:
		pass
	if not setFontInfo(f, GlyphsDoc):
		return False
	readGlyphs(f, GlyphsDoc)
	readKerning(f, GlyphsDoc)
	setLegacyNames(f)
	readFeatures(f, GlyphsDoc)
	
	fl.UpdateFont()
	f.modified = 0
	pool.drain()


def GetFile(message=None, filetypes = None, selectFolders = True, selectFiles = True):
	assert(filetypes)
	Panel = NSOpenPanel.openPanel()
	if message != None:
		Panel.setMessage_(message)
	Panel.setCanChooseFiles_(selectFiles)
	Panel.setCanChooseDirectories_(selectFolders)
	Panel.setAllowsMultipleSelection_(False)
	pressedButton = Panel.runModalForTypes_(filetypes)
	if pressedButton == 1:
		return Panel.filename()
	return None

def main():
	fl.output = ""
	path = GetFile(message="Please select a .glyphs file", filetypes=["glyphs"], selectFolders=False, selectFiles=True)
	StartTime = time.clock()
	if path is None:
		return
	readGlyphsFile(path)
	
	print "import Time:", (time.clock() - StartTime), "s."

if __name__ == '__main__':
	main()
