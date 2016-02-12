"""RoboFab for Glyphs"""
# -*- coding: utf-8 -*-
import sys
import objc
from GlyphsApp import *
from GlyphsApp import Proxy
from AppKit import *
from Foundation import *

from robofab import RoboFabError, RoboFabWarning, ufoLib
from robofab.objects.objectsBase import BaseFont, BaseKerning, BaseGroups, BaseInfo, BaseFeatures, BaseLib,\
		BaseGlyph, BaseContour, BaseSegment, BasePoint, BaseBPoint, BaseAnchor, BaseGuide, \
		relativeBCPIn, relativeBCPOut, absoluteBCPIn, absoluteBCPOut, _box,\
		_interpolate, _interpolatePt, roundPt, addPt,\
		MOVE, LINE, CORNER, CURVE, QCURVE, OFFCURVE,\
		BasePostScriptFontHintValues, postScriptHintDataLibKey, BasePostScriptGlyphHintValues

import os
from warnings import warn

__all__ = ["CurrentFont", "AllFonts", "CurrentGlyph", 'OpenFont', 'RFont', 'RGlyph', 'RContour', 'RPoint', 'RAnchor', 'RComponent', "NewFont", "GSMOVE", "GSLINE", "GSCURVE", "GSOFFCURVE", "GSSHARP", "GSSMOOTH", "GlyphPreview"]

GSMOVE_ = 17
GSLINE_ = 1
GSCURVE_ = 35
GSOFFCURVE_ = 65
GSSHARP = 0
GSSMOOTH = 100

GSMOVE = MOVE
GSLINE = LINE
GSCURVE = CURVE
GSOFFCURVE = OFFCURVE

LOCAL_ENCODING = "macroman"

# This is for compatibility until the proper implementaion is shipped.
if type(GSElement.parent) != type(GSGlyph.parent):
	GSElement.parent = property(lambda self: self.valueForKey_("parent"))


def CurrentFont():
	"""Return a RoboFab font object for the currently selected font."""
	doc = Glyphs.currentDocument
	if doc:
		try:
			return RFont(doc.font, doc.windowControllers()[0].masterIndex())
		except:
			pass
	return None

def AllFonts():
	"""Return a list of all open fonts."""
	all = []
	for doc in Glyphs.documents:
		for master_index, master_object in enumerate(doc.font.masters):
			all.append(RFont(doc.font, master_index))
	return all


def CurrentGlyph():
	"""Return a RoboFab glyph object for the currently selected glyph."""
	Doc = Glyphs.currentDocument
	try:
		Layer = Doc.selectedLayers()[0]
		return RGlyph(Layer.parent)
	except: pass
	
	print "No glyph selected!"
	return None

def OpenFont(path=None, note=None):
	"""Open a font from a path."""
	if path == None:
		#from robofab.interface.all.dialogs import GetFile
		path = GetFile(note, filetypes=["ufo", "glyphs", "otf", "ttf"])
	if path:
		if path[-7:].lower() == '.glyphs' or path[-3:].lower() in ["ufo", "otf", "ttf"]:
			doc = Glyphs.openDocumentWithContentsOfFile_display_(path, False) #chrashed !!
			if doc != None:
				return RFont(doc.font)
	return None

def NewFont(familyName=None, styleName=None):
	"""Make a new font"""
	doc = Glyphs.documentController().openUntitledDocumentAndDisplay_error_(True, None)
	rf = RFont(doc.font)
	if familyName:
		rf.info.familyName = familyName
	if styleName:
		rf.info.styleName = styleName
	return rf

class PostScriptFontHintValues(BasePostScriptFontHintValues):
	"""	Font level PostScript hints object for objectsRF usage.
		If there are values in the lib, use those.
		If there are no values in the lib, use defaults.
		
		The psHints attribute for objectsRF.RFont is basically just the
		data read from the Lib. When the object saves to UFO, the 
		hints are written back to the lib, which is then saved.
	"""
	
	def __init__(self, aFont=None, data=None):
		self.setParent(aFont)
		BasePostScriptFontHintValues.__init__(self)
		if aFont is not None:
			# in version 1, this data was stored in the lib
			# if it is still there, guess that it is correct
			# move it to font info and remove it from the lib.
			libData = aFont.lib.get(postScriptHintDataLibKey)
			if libData is not None:
				self.fromDict(libData)
				del libData[postScriptHintDataLibKey]
		if data is not None:
			self.fromDict(data)

def getPostScriptHintDataFromLib(aFont, fontLib):
	hintData = fontLib.get(postScriptHintDataLibKey)
	psh = PostScriptFontHintValues(aFont)
	psh.fromDict(hintData)
	return psh
	
class PostScriptGlyphHintValues(BasePostScriptGlyphHintValues):
	"""	Glyph level PostScript hints object for objectsRF usage.
		If there are values in the lib, use those.
		If there are no values in the lib, be empty.
	"""
	def __init__(self, aGlyph=None, data=None):
		# read the data from the glyph.lib, it won't be anywhere else
		BasePostScriptGlyphHintValues.__init__(self)
		if aGlyph is not None:
			self.setParent(aGlyph)
			self._loadFromLib(aGlyph.lib)
		if data is not None:
			self.fromDict(data)

class KerningProxy(Proxy, BaseKerning):
	def _convertKeys(self, keys):
		firstKey, secondKey = keys
		if firstKey[0] != "@":
			firstKey = self._owner._font.glyphForName_(firstKey).id
			if firstKey == None:
				raise KeyError, "glyph with name %s not found" % keys[0]
		if secondKey[0] != "@":
			secondKey = self._owner._font.glyphForName_(secondKey).id
			if secondKey == None:
				raise KeyError, "glyph with name %s not found" % keys[1]
		return (firstKey, secondKey)
	def __getitem__(self, keys):
		if (type(keys) == list or type(keys) == tuple) and len(keys) == 2:
			FontMaster = self._owner._font.masters[self._owner._master]
			firstKey, secondKey = self._convertKeys(keys)
			value = self._owner._font.kerningForFontMasterID_LeftKey_RightKey_(FontMaster.id, firstKey, secondKey)
			if value > 100000: # NSNotFound
				value = None
			return value
		else:
			raise KeyError, 'kerning pair must be a tuple: (left, right)'
	def __setitem__(self, keys, value):
		if not isinstance(value, (int, float)):
			raise ValueError
		if (type(keys) == list or type(keys) == tuple) and len(keys) == 2:
			FontMaster = self._owner._font.masters[self._owner._master]
			firstKey, secondKey = self._convertKeys(keys)
			self._owner._font.setKerningForFontMasterID_LeftKey_RightKey_Value_(FontMaster.id, firstKey, secondKey, value)
		else:
			raise KeyError, 'kerning pair must be a tuple: (left, right)'
	def __delitem__(self, keys):
		if (type(keys) == list or type(keys) == tuple) and len(keys) == 2:
			FontMaster = self._owner._font.masters[self._owner._master]
			firstKey, secondKey = self._convertKeys(keys)
			self._owner._font.removeKerningForFontMasterID_LeftKey_RightKey_(FontMaster.id, firstKey, secondKey)
		else:
			raise KeyError, 'kerning pair must be a tuple: (left, right)'
	def remove(self, keys):
		self.__delitem__(keys)
	def __repr__(self):
		font = "unnamed_font"
		fontParent = self.getParent()
		if fontParent is not None:
			try:
				font = fontParent.info.postscriptFullName
			except AttributeError: pass
		return "<RKerning for %s>" % font
	def keys(self):
		return self._dict().keys()
	def values(self):
		return self._dict().values()
	def __iter__(self):
		for key in self.keys():
			yield key
	def _dict(self):
		FontMaster = self._owner._font.masters[self._owner._master]
		GSKerning = self._owner._font.kerning.objectForKey_(FontMaster.id)
		kerning = {}
		if GSKerning != None:
			for LeftKey in GSKerning.allKeys():
				LeftKerning = GSKerning.objectForKey_(LeftKey)
				if LeftKey[0] != '@':
					LeftKey = self._owner._font.glyphForId_(LeftKey).name
				for RightKey in LeftKerning.allKeys():
					RightKerning = LeftKerning.objectForKey_(RightKey)
					if RightKey[0] != '@':
						RightKey = self._owner._font.glyphForId_(RightKey).name
					kerning[(str(LeftKey), str(RightKey))] = RightKerning
		return kerning

class RFont(BaseFont):
	"""RoboFab UFO wrapper for GS Font object"""
	
	_title = "GSFont"
	
	def __init__(self, font=None, master=0):
		BaseFont.__init__(self)
		if font != None:
			doc = font.parent
		else:
			doc = None
		self._document = doc
		self._font = font
		self._master = master
		self._masterKey = font.masters[master].id
		self.features = RFeatures(font)
		self.info = RInfo(self)
		
		self._supportHints = False
		self._RGlyphs = {}
	
	def copy(self):
		return RFont(self._font.copy())
	
	def keys(self):
		keys = {}
		for glyph in self._font.glyphs:
			glyphName = glyph.name
			if glyphName in keys:
				raise KeyError, "Duplicate glyph name in RFont: %r" % glyphName
			keys[glyphName] = None
		return keys.keys()

	def has_key(self, glyphName):
		glyph = self._font.glyphForName_(glyphName)
		if glyph is None:
			return False
		else:
			return True
	
	__contains__ = has_key
	
	def __setitem__(self, glyphName, glyph):
		self._font.addGlyph_( glyph.naked() )
	
	def __getitem__(self, glyphName):
		GGlyph = self._font.glyphForName_(glyphName)
		if GGlyph is None:
			raise KeyError("Glyph '%s' not in font." % glyphName)
		else:
			glyph = RGlyph(GGlyph, self._master)
			glyph.setParent(self)
			return glyph
	
	def __cmp__(self, other):
		if not hasattr(other, '_document'):
			return -1
		return self._compare(other)
		if self._document.fileName() == other._document.fileName():
			# so, names match.
			# this will falsely identify two distinct "Untitled"
			# let's check some more
			return 0
		else:
			return -1
	
	def __len__(self):
		if self._font.glyphs is None:
			return 0
		return len(self._font.glyphs)
	
	def close(self):
		self._document.close()
	
	def _get_lib(self):
		lib = self._font.userData.objectForKey_("org.robofab.ufoLib")
		if lib is None:
			lib = NSClassFromString("GSNotifyingDictionary").alloc().init()
			lib.setParent_(self._font)
			self._font.setUserObject_forKey_(lib, "org.robofab.ufoLib")
		return lib
	
	def _set_lib(self, obj):
		self._font.userData.setObject_forKey_(obj, "org.robofab.ufoLib")
	
	lib = property(_get_lib, _set_lib, doc="font lib object")
	
	def _hasNotChanged(self, doGlyphs=True):
		raise NotImplementedError
	
	def _get_path(self):
		if self._document.fileURL() is None:
			raise ValueError("Font is not saved yet")
		return self._document.fileURL().path()
	
	path = property(_get_path, doc="path of the font")
	
	def _get_groups(self):
		Dictionary = {}
		for currGlyph in self._font.glyphs:
			if currGlyph.leftKerningGroupId():
				Group = Dictionary.get(currGlyph.leftKerningGroupId(), None)
				if not Group:
					Group = []
					Dictionary[currGlyph.leftKerningGroupId()] = Group
				Group.append(currGlyph.name)
			if currGlyph.rightKerningGroupId():
				Group = Dictionary.get(currGlyph.rightKerningGroupId(), None)
				if not Group:
					Group = []
					Dictionary[currGlyph.rightKerningGroupId()] = Group
				Group.append(currGlyph.name)
		for aClass in self._font.classes:
			Dictionary[aClass.name] = aClass.code.split(" ")
		return Dictionary
	
	def _set_groups(self, GroupsDict):
		for currGroupKey in GroupsDict.keys():
			if currGroupKey.startswith("@MMK_L_"):
				Group = GroupsDict[currGroupKey]
				if Group:
					for GlyphName in Group:
						if ChangedGlyphNames.has_key(currGroupKey):
							currGroupKey = ChangedGlyphNames[currGroupKey]
						if ChangedGlyphNames.has_key(GlyphName): 
							GlyphName = ChangedGlyphNames[GlyphName]
						self._font.glyphForName_(GlyphName).setRightKerningGroupId_( currGroupKey )
			
			elif currGroupKey.startswith("@MMK_R_"):
				Group = GroupsDict[currGroupKey]
				if Group:
					for GlyphName in Group:
						self._font.glyphForName_(GlyphName).setLeftKerningGroupId_(currGroupKey)
			else:
				newClass = GSClass()
				newClass.setName_( currGroupKey )
				newClass.setCode_( " ".join(GroupsDict[currGroupKey]))
				newClass.setAutomatic_( False )
				self._font.addClass_(newClass)
	
	groups = property(_get_groups, _set_groups, doc="groups")
	
	kerning = property( lambda self: KerningProxy(self),
						lambda self, value: KerningProxy(self).setter(value))
	
	#
	# methods for imitating GlyphSet?
	#
	
	def getWidth(self, glyphName):
		if self._font.glyphForName_(glyphName):
			return self._font.glyphForName_(glyphName).layerForKey_(self._masterKey).width()
		raise IndexError		# or return None?
	
	def save(self, path=None):
		"""Save the font, path is required."""
		if not path:
			if not self._document.filePath():
				raise RoboFabError, "No destination path specified."
			else:
				self._document.setFilePath_( self.filename )
		else:
			self._document.setFilePath_( path )
		self._document.saveDocument_(None)
	
	def close(self, save=False):
		"""Close the font, saving is optional."""
		if save:
			self.save()
		else:
			self._document.updateChangeCount_(NSChangeCleared)
		self._document.close()
	
	def _get_glyphOrder(self):
		return self._font.valueForKeyPath_("glyphs.name")
	
	glyphOrder = property(_get_glyphOrder, doc="groups")
	
	def getGlyph(self, glyphName):
		# XXX getGlyph may have to become private, to avoid duplication
		# with __getitem__
		n = None
		if self._RGlyphs.has_key(glyphName):
			# have we served this glyph before? it should be in _object
			n = self._RGlyphs[glyphName]
		else:
			# haven't served it before, is it in the glyphSet then?
			n = RGlyph( self._font.glyphForName_(glyphName) )
			self._RGlyphs[glyphName] = n
			
		if n is None:
			raise KeyError, glyphName
		return n
	
	def newGlyph(self, glyphName, clear=True):
		"""Make a new glyph"""
		g = self._font.glyphForName_(glyphName)
		if g is None:
			g = GSGlyph(glyphName)
			self._font.addGlyph_(g)
		elif clear:
			g.layers[self._masterKey] = GSLayer()
		return self[glyphName]
	
	def insertGlyph(self, glyph, newGlyphName=None):
		"""returns a new glyph that has been inserted into the font"""
		if newGlyphName is None:
			name = glyph.name
		else:
			name = newGlyphName
		glyph = glyph.copy()
		glyph.name = name
		glyph.setParent(self)
		glyph._hasChanged()
		self._RGlyphs[name] = glyph
		# is the user adding a glyph that has the same
		# name as one that was deleted earlier?
		#if name in self._scheduledForDeletion:
		#	self._scheduledForDeletion.remove(name)
		return self.getGlyph(name)
		
	def removeGlyph(self, glyphName):
		"""remove a glyph from the font"""
		# XXX! Potential issue with removing glyphs.
		# if a glyph is removed from a font, but it is still referenced
		# by a component, it will give pens some trouble.
		# where does the resposibility for catching this fall?
		# the removeGlyph method? the addComponent method
		# of the various pens? somewhere else? hm... tricky.
		#
		# we won't actually remove it, we will just store it for removal
		# but only if the glyph does exist
		# if self.has_key(glyphName) and glyphName not in self._scheduledForDeletion:
		#	self._scheduledForDeletion.append(glyphName)
		# now delete the object
		if glyphName in self._font.glyphs:
			del self._font[glyphName]
		self._hasChanged()
	
	def _get_selection(self):
		"""return a list of glyph names for glyphs selected in the font window """
		l=[]
		for Layer in self._document.selectedLayers():
			l.append(Layer.parent.name)
		return l
	
	def _set_selection(self, list):
		raise NotImplementedError
		return
	
	selection = property(_get_selection, _set_selection, doc="list of selected glyph names")

class RGlyph(BaseGlyph):
	
	_title = "GSGlyph"
	preferedSegmentType = "curve"
	
	def __init__(self, _GSGlyph = None, master = 0, layer = None):
		if layer is not None:
			_GSGlyph = layer.parent
		
		if _GSGlyph is None:
			_GSGlyph = GSGlyph()
		
		self._object = _GSGlyph
		self._layerID = None
		if layer is None:
			try:
				if _GSGlyph.parent:
					self._layerID = _GSGlyph.parent.masters[master].id
				elif (_GSGlyph.layers[master]):
					self._layerID = _GSGlyph.layers[master].layerId
			except:
				pass
			self.masterIndex = master
			if self._layerID:
				self._layer = _GSGlyph.layerForKey_(self._layerID)
		else:
			self._layer = layer
			self._layerID = layer.associatedMasterId
		if self._layer is None:
			self._layerID = "undefined"
			self._layer = GSLayer()
			_GSGlyph.setLayer_forKey_(self._layer, self._layerID)
		self._contours = None
		
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		fontParent = self.getParent()
		if fontParent is not None:
			try:
				font = fontParent.info.postscriptFullName
			except AttributeError:
				pass
		try:
			glyph = self.name
		except AttributeError:
			pass
		return "<RGlyph %s for %s.%s>" %(self._object.name, font, glyph)
	
	def getParent(self):
		return RFont(self._object.parent)
	
	def __getitem__(self, index):
		return self.contours[index]
	
	def __delitem__(self, index):
		self._layer.removePathAtIndex_(index)
		self._invalidateContours()
	
	def _invalidateContours(self):
		self._contours = None
	
	def __iter__(self):
		Values = self._layer.paths
		if Values is not None:
			for element in Values:
				yield element
	
	def __len__(self):
		return len(self._layer.paths)
	
	def copy(self):
		Copy = RGlyph(self._object.copy(), self.masterIndex)
		Copy._layerID = self._layerID
		Copy._layer = Copy._object.layerForKey_(self._layerID)
		return Copy
	
	def _get_contours(self):
		return self._layer.paths
	
	contours = property(_get_contours, doc="allow for iteration through glyph.contours")
	
	def _hasNotChanged(self):
		raise NotImplementedError
	
	def _get_box(self):
		bounds = self._layer.bounds
		bounds = (int(round(NSMinX(bounds))), int(round(NSMinY(bounds))), int(round(NSMaxX(bounds))), int(round(NSMaxY(bounds))))
		return bounds
	
	box = property(_get_box, doc="the bounding box of the glyph: (xMin, yMin, xMax, yMax)")
	
	#
	# attributes
	#
	
	def _get_lib(self):
		try:
			return self._object.userData()
		except:
			return None
	
	def _set_lib(self, key, obj):
		if self._object.userData() is objc.nil:
			self._object.setUserData_(NSMutableDictionary.dictionary())
		self._object.userData().setObject_forKey_(obj, key)
		
	lib = property(_get_lib, _set_lib, doc="Glyph Lib")
	
	def _set_name(self, newName):
		prevName = self.name
		if newName == prevName:
			return
		self._object.name = newName
	
	name = property(lambda self: self._object.name, _set_name)
	
	def _get_unicodes(self):
		if self._object.unicode is not None:
			return [int(self._object.unicode, 16)]
		return []
	
	def _set_unicodes(self, value):
		if not isinstance(value, list):
			raise RoboFabError, "unicodes must be a list"
		try:
			self._object.setUnicode = value[0]
		except:
			pass
	
	unicodes = property(_get_unicodes, _set_unicodes, doc="all unicode values for the glyph")
	
	def _get_unicode(self):
		if self._object.unicode is None:
			return None
		return self._object.unicodeChar()
	
	def _set_unicode(self, value):
		if type(value) == str:
			if value is not None and value is not self._object.unicode:
				self._object.setUnicode_(value)
		elif type(value) == int:
			strValue = "%0.4X" % value
			if strValue is not None and strValue is not self._object.unicode:
				self._object.setUnicode_(strValue)
		else:
			raise(KeyError)
	
	unicode = property(_get_unicode, _set_unicode, doc="first unicode value for the glyph")
	
	index =  property(lambda self: self._object.parent.indexOfGlyph_(self._object))
	
	note = property(lambda self: self._object.valueForKey_("note"),
					lambda self, value: self._object.setNote_(value))

	leftMargin = property(lambda self: self._layer.LSB,
						  lambda self, value: self._layer.setLSB_(value), doc="Left Side Bearing")
	
	rightMargin = property(lambda self: self._layer.RSB,
						   lambda self, value: self._layer.setRSB_(value), doc="Right Side Bearing")
	
	width = property(lambda self: self._layer.width,
					 lambda self, value: self._layer.setWidth_(value), doc="width")
	
	components = property(lambda self: self._layer.components, doc="List of components")
	
	guides = property(lambda self: self._layer.guides, doc="List of guides")
	
	def appendComponent(self, baseGlyph, offset=(0, 0), scale=(1, 1)):
		"""append a component to the glyph"""
		new = GSComponent(baseGlyph, offset, scale)
		self._layer.addComponent_(new)
	
	def removeComponent(self, component):
		"""remove  a specific component from the glyph"""
		self._layer.removeComponent_(component)
	
	def getPointPen(self):
		# if "GSPen" in sys.modules.keys():
		# 	del(sys.modules["GSPen"])
		from GSPen import GSPointPen
		return GSPointPen(self, self._layer)
	
	def appendAnchor(self, name, position, mark=None):
		"""append an anchor to the glyph"""
		new = GSAnchor(name=name, pt=position)
		self._layer.addAnchor_(new)
	
	def removeAnchor(self, anchor):
		"""remove  a specific anchor from the glyph"""
		self._layer.removeAnchor_(anchor)
	
	def removeContour(self, index):
		"""remove  a specific contour from the glyph"""
		if type(index) == type(int):
			self._layer.removePathAtIndex_(index)
		else:
			self._layer.removePath_(index)
	
	def center(self, padding=None):
		"""Equalise sidebearings, set to padding if wanted."""
		left = self._layer.LSB
		right = self._layer.RSB
		if padding:
			e_left = e_right = padding
		else:
			e_left = (left + right)/2
			e_right = (left + right) - e_left
		self._layer.setLSB_(e_left)
		self._layer.setRSB_(e_right)
	
	def decompose(self):
		"""Decompose all components"""
		self._layer.decomposeComponents()
	
	def clear(self, contours=True, components=True, anchors=True, guides=True):
		"""Clear all items marked as True from the glyph"""
		if contours:
			self.clearContours()
		if components:
			self.clearComponents()
		if anchors:
			self.clearAnchors()
		if guides:
			self.clearGuides()
	
	def clearContours(self):
		"""clear all contours"""
		while len(self._layer.paths) > 0:
			self._layer.removePathAtIndex_(0)
	
	def clearComponents(self):
		"""clear all components"""
		self._layer.setComponents_(NSMutableArray.array())
	
	def clearAnchors(self):
		"""clear all anchors"""
		self._layer.setAnchors_(NSMutableDictionary.dictionary())
		
	def clearGuides(self):
		"""clear all horizontal guides"""
		self._layer.setGuideLines_(NSMutableArray.array())
	
	def update(self):
		self._contours = None
		#GSGlyphsInfo.updateGlyphInfo_changeName_(self._object, False)
	
	def correctDirection(self, trueType=False):
		self._layer.correctPathDirection()
	
	def removeOverlap(self):
		removeOverlapFilter = NSClassFromString("GlyphsFilterRemoveOverlap").alloc().init()
		removeOverlapFilter.runFilterWithLayer_error_(self._layer, None)
		
	def _mathCopy(self):
		""" copy self without contour, component and anchor data """
		glyph = self._getMathDestination()
		glyph.name = self.name
		glyph.unicodes = list(self.unicodes)
		glyph.width = self.width
		glyph.note = self.note
		try:
			glyph.lib = dict(self.lib)
		except:
			pass
		return glyph
	
	anchors = property(lambda self: self._layer.anchors)
	
	def getRepresentation(self, representaion):
		if representaion == "defconAppKit.NSBezierPath":
			return self._layer.bezierPath.copy()
		return None

	def performUndo(self):
		pass
	def prepareUndo(self, undoTitle):
		pass

RContour = GSPath

GSPath.points = GSPath.nodes

def __GSPath__get_bPoints(self):
	bPoints = []
	for segment in self.segments:
		segType = segment.type
		if segType == MOVE or segType == LINE or segType == CURVE:
			b = RBPoint(segment)
			bPoints.append(b)
		else:
			raise RoboFabError, "encountered unknown segment type"
	return bPoints
	
GSPath.bPoints = property(__GSPath__get_bPoints, doc="view the contour as a list of bPoints")

def __GSPath__draw__(self, pen):
	'''draw the object with a fontTools pen'''
	
	if self.closed:
		for i in range(-1, -4, -1):
			StartNode = self.nodeAtIndex_(i)
			if StartNode.type != OFFCURVE:
				pen.moveTo(StartNode.position)
				break
	else:
		for i in range(len(self)):
			StartNode = self.nodeAtIndex_(i)
			if StartNode.type != OFFCURVE:
				pen.moveTo(StartNode.position)
				break
	for i in range(len(self)):
		Node = self.nodeAtIndex_(i)
		if Node.type == LINE:
			pen.lineTo(Node.position)
		elif Node.type == CURVE:
			pen.curveTo(self.nodeAtIndex_(i-2).position, self.nodeAtIndex_(i-1).position, Node.position)
	if self.closed:
		pen.closePath()
	else:
		pen.endPath()

GSPath.draw = __GSPath__draw__

def __GSPath__drawPoints__(self, pen):
	'''draw the object with a fontTools pen'''
	
	pen.beginPath()
	for i in range(len(self)):
		Node = self.nodeAtIndex_(i)
		pen.addPoint(Node.position, segmentType=Node.type, smooth=Node.smooth)
	pen.endPath()

GSPath.drawPoints = __GSPath__drawPoints__

def __GSPath_get_segments(self):
	if not len(self.nodes):
		return []
	segments = []
	index = 0
	node = None
	for i in range(len(self.nodes)):
		node = self.nodeAtIndex_(i)
		if node.type == GSLINE or node.type == GSCURVE:
			_Segment = RSegment(index, self, node)
			_Segment.parent = self
			_Segment.index = index
			segments.append(_Segment)
			index += 1
	if self.closed:
		# TODO fix this out properly. 
		# _Segment = RSegment(0, self, node)
		# _Segment.type = MOVE
		# segments.insert(0, _Segment)
		pass
	else:
		_Segment = RSegment(0, self, self.nodeAtIndex_(0))
		_Segment.type = MOVE
		segments.insert(0, _Segment)
	return segments

def __GSPath_set_segments(self, segments):
	points = []
	for segment in segments:
		points.append(segment.points)
	
GSPath.segments = property(__GSPath_get_segments, __GSPath_set_segments, doc="A list of all points in the contour organized into segments.")

def __GSPath__reverseContour__(self):
	'''reverse contour direction'''
	self.reverse()
GSPath.reverseContour = __GSPath__reverseContour__

def __GSPath__pointInside__(self, point):
	return self.bezierPath.containsPoint_(point)
GSPath.pointInside = __GSPath__pointInside__

def __GSPath__move__(self, (x, y)):
	"""move the contour"""
	#this will be faster if we go straight to the points
	for point in self.points:
		point.move((x, y))

GSPath.move = __GSPath__move__

def __GSPath__get_selected(self):
	selected = 0
	nodes = self.nodes
	Layer = self.parent
	for node in nodes:
		if node in Layer.selection:
			selected = 1
			break
	return selected

def __GSPath__set_selected(self, value):
	Layer = self.parent
	if value:
		Layer.addObjectsFromArrayToSelection_(self.pyobjc_instanceMethods.nodes())
	else:
		Layer.removeObjectsFromSelection_(self.pyobjc_instanceMethods.nodes())

GSPath.selected = property(__GSPath__get_selected, __GSPath__set_selected, doc="selection of the contour: 1-selected or 0-unselected")


class RSegment(BaseSegment):
	def __init__(self, index, contoure, node):
		BaseSegment.__init__(self)
		self._object = node
		self.parent = contoure
		self.index = index
		self.isMove = False # to store if the segment is a move segment
	
	def __repr__(self):
		return "<RSegment %s (%d), r>"%(self.type, self.smooth)#, self.points)
	def getParent(self):
		return self.parent
	
	def _get_type(self):
		if self.isMove: return MOVE
		return self._object.type
	
	def _set_type(self, pointType):
		if pointType == MOVE:
			self.isMove = True
			return
		raise NotImplementedError
		return
		onCurve = self.points[-1]
		ocType = onCurve.type
		if ocType == pointType:
			return
		#we are converting a cubic line into a cubic curve
		if pointType == CURVE and ocType == LINE:
			onCurve.type = pointType
			parent = self.getParent()
			prev = parent._prevSegment(self.index)
			p1 = RPoint(prev.onCurve.x, prev.onCurve.y, pointType=OFFCURVE)
			p1.setParent(self)
			p2 = RPoint(onCurve.x, onCurve.y, pointType=OFFCURVE)
			p2.setParent(self)
			self.points.insert(0, p2)
			self.points.insert(0, p1)
		#we are converting a cubic move to a curve
		elif pointType == CURVE and ocType == MOVE:
			onCurve.type = pointType
			parent = self.getParent()
			prev = parent._prevSegment(self.index)
			p1 = RPoint(prev.onCurve.x, prev.onCurve.y, pointType=OFFCURVE)
			p1.setParent(self)
			p2 = RPoint(onCurve.x, onCurve.y, pointType=OFFCURVE)
			p2.setParent(self)
			self.points.insert(0, p2)
			self.points.insert(0, p1)
		#we are converting a quad curve to a cubic curve
		elif pointType == CURVE and ocType == QCURVE:
			onCurve.type == CURVE
		#we are converting a cubic curve into a cubic line
		elif pointType == LINE and ocType == CURVE:
			p = self.points.pop(-1)
			self.points = [p]
			onCurve.type = pointType
			self.smooth = False
		#we are converting a cubic move to a line
		elif pointType == LINE and ocType == MOVE:
			onCurve.type = pointType
		#we are converting a quad curve to a line:
		elif pointType == LINE and ocType == QCURVE:
			p = self.points.pop(-1)
			self.points = [p]
			onCurve.type = pointType
			self.smooth = False	
		# we are converting to a quad curve where just about anything is legal
		elif pointType == QCURVE:
			onCurve.type = pointType
		else:
			raise RoboFabError, 'unknown segment type'
			
	type = property(_get_type, _set_type, doc="type of the segment")
	
	def _get_smooth(self):
		return self._object.connection == GSSMOOTH
		
	def _set_smooth(self, smooth):
		raise NotImplementedError
		
	
	smooth = property(_get_smooth, _set_smooth, doc="smooth of the segment")
	
	def insertPoint(self, index, pointType, point):
		x, y = point
		p = RPoint(x, y, pointType=pointType)
		p.setParent(self)
		self.points.insert(index, p)
		self._hasChanged()
	
	def removePoint(self, index):
		del self.points[index]
		self._hasChanged()
		
	def _get_points(self):
		Path = self._object.parent
		index = Path.indexOfNode_(self._object)
		points = []
		if index < len(Path.nodes):
			if self._object.type == GSCURVE:
				points.append(RPoint(Path.nodes[index-2]))
				points.append(RPoint(Path.nodes[index-1]))
				points.append(RPoint(Path.nodes[index]))
			elif self._object.type == GSLINE:
				points.append(RPoint(Path.nodes[index]))
		return points
	
	points = property(_get_points, doc="index of the segment")

	def _get_selected(self):
		Path = self._object.parent
		index = Path.indexOfNode_(self._object)
		Layer = Path.parent
		
		if self._object.type == GSCURVE:
			return Path.nodes[index-2] in Layer.selection or Path.nodes[index-1] in Layer.selection or Path.nodes[index] in Layer.selection
		elif self._object.type == GSLINE:
			return Path.nodes[index] in Layer.selection
	
	def _set_selected(self, select):
		Path = self._object.parent
		index = Path.indexOfNode_(self._object)
		Layer = Path.parent
		
		if self._object.type == GSCURVE:
			if select:
				Layer.addObjectsFromArrayToSelection_([Path.nodes[index-2], Path.nodes[index-1], Path.nodes[index] ] )
			else:
				Layer.removeObjectsFromSelection_([Path.nodes[index-2], Path.nodes[index-1], Path.nodes[index] ] )
		elif self._object.type == GSLINE:
			if select:
				Layer.addSelection_( Path.nodes[index] )
			else:
				Layer.removeObjectFromSelection_( Path.nodes[index] )
	
	selected = property(_get_selected, _set_selected, doc="if segment is selected")


class RBPoint(BaseBPoint):
	
	_title = "GlyphsBPoint"
	
	def __init__(self, segment):
		self._object = segment;
	
	def __repr__(self):
		GlyphName = "unnamed_glyph"
		pathIndex = -1
		nodeIndex = -1
		Path = self._object._object.parent
		if Path is not None:
			try:
				nodeIndex = Path.indexOfNode_(self._object._object)
			except AttributeError: pass
			Layer = Path.parent
			if Layer is not None:
				try:
					pathIndex = Layer.indexOfPath_(Path)
				except AttributeError: pass
				Glyph = Layer.parent
				if Glyph is not None:
					try:
						GlyphName = Glyph.name
					except AttributeError: pass
		return "<RBPoint (%.1f, %.1f) %s[%d][%d]>"%( self._object._object.position.x, self._object._object.position.y, GlyphName, pathIndex, nodeIndex)
	
	def getParent(self):
		return self._object
	
	def _setAnchorChanged(self, value):
		self._anchorPoint.setChanged(value)
	
	def _setNextChanged(self, value):
		self._nextOnCurve.setChanged(value)	
		
	def _get__parentSegment(self):
		return self._object
		
	_parentSegment = property(_get__parentSegment, doc="")
	
	def _get__nextOnCurve(self):
		pSeg = self._parentSegment
		contour = pSeg.getParent()
		#could this potentially return an incorrect index? say, if two segments are exactly the same?
		return contour.segments[(contour.segments.index(pSeg) + 1) % len(contour.segments)]
	
	_nextOnCurve = property(_get__nextOnCurve, doc="")
	
	def _get_index(self):
		return self._parentSegment.index
	
	index = property(_get_index, doc="index of the bPoint on the contour")
	
	def _get_selected(self):
		Path = self._object._object.parent
		Layer = Path.parent
		return self._object._object in Layer.selection
	
	def _set_selected(self, value):
		Path = self._object.parent
		Layer = Path.parent
		Layer.addSelection_(self._object)
		
	selected = property(_get_selected, _set_selected, doc="")
	
RPoint = GSNode

RAnchor = GSAnchor

def _get_name(self):
	try:
		name = self._object.userData()["name"]
		if name is not None:
			return name
	except:
		pass
	
	# Compatibility with old way to store name.
	try:
		a = TAG
	except:
		TAG = -2
	Path = self.parent
	Layer = Path.parent
	for Hint in Layer.hints:
		if Hint.type == TAG and len(Hint.name()) > 0:
			if Hint.originNode is None and Hint.originIndex is not None:
				Hint.updateIndexes()
			if Hint.originNode == self._object:
				self.setUserData_forKey_(Hint.name(), "name")
				Layer.removeHint_(Hint)
				return Hint.name()
	return None

def _set_name(self, value):
	if value is None or type(value) is str or type(value) is unicode or type(value) is objc.pyobjc_unicode:
		self.setUserData_forKey_(value, "name")
	else:
		raise(ValueError)
	
GSNode.name = property(_get_name, _set_name, doc="")

def __GSNode_get_type__(self):
	GS_Type = self.pyobjc_instanceMethods.type()
	if GS_Type == GSMOVE_:
		return MOVE
	elif GS_Type == GSOFFCURVE_:
		return OFFCURVE
	elif GS_Type == GSCURVE_:
		return CURVE
	else:
		return LINE

def __GSNode_set_type__(self, value):
	if value == MOVE:
		self.setType_(GSLINE_)
	elif value == LINE:
		self.setType_(GSLINE_)
	elif value == OFFCURVE:
		self.setType_(GSOFFCURVE_)
	elif value == CURVE:
		self.setType_(GSCURVE_)
	elif value == QCURVE:
		self.setType_(GSQCURVE_)

GSNode.type = property(__GSNode_get_type__, __GSNode_set_type__, doc="")

def __GSNode__get_smooth(self):
	return self.connection == GSSMOOTH

def __GSNode__set_smooth(self, value):
	if value:
		self.connection = GSSMOOTH
	else:
		self.connection = GSSHARP

GSNode.smooth = property(__GSNode__get_smooth, __GSNode__set_smooth, doc="")

def __GSNode__move__(self, (x, y)):
	"""Move the point"""
	self.x, self.y = addPt((self.x, self.y), (x, y))
	
GSNode.move = __GSNode__move__


GSComponent.offset = property(lambda self: self.position)

def __GSComponent_get_scale(self):
	""" Return the scale components of the transformation."""
	(xx, xy, yx, yy, dx, dy) = self.transformStruct()
	return xx, yy
	
def __GSComponent_set_scale(self, (xScale, yScale)):
	""" Set the scale component of the transformation.
		Note: setting this value effectively makes the xy and yx values meaningless.
		We're assuming that if you're setting the xy and yx values, you will use
		the transformation attribute rather than the scale and offset attributes.
	"""
	print self
	Transform = NSAffineTransform.transform()
	Transform.setTransformStruct_(self.transformStruct())
	Transform.scaleXBy_yBy_(xScale, yScale)
	self.setTransformStruct_(Transform.transformStruct())
	
GSComponent.scale = property(__GSComponent_get_scale, __GSComponent_set_scale, doc="the scale of the component")

transformation = property(lambda self: self.transformStruct(),
						  lambda self, value: self.setTransformStruct_(value))

def __GSComponent_move_(self, (x, y)):
	"""Move the component"""
	(xx, xy, yx, yy, dx, dy) = self.transformStruct()
	self.setTransformStruct_((xx, xy, yx, yy, dx+x, dy+y))
GSComponent.move = __GSComponent_move_

GSComponent.baseGlyph = property(lambda self: self.componentName,
								 lambda self, value: self.setComponentName_(value))

def __GSComponent_get_index(self):
	if self.parent is None:
		return None
	return self.parent.components.index(self)
GSComponent.index = property(__GSComponent_get_index, doc="index of the component")

def __GSComponent_get_box_(self):
	Rect = self.bounds
	return (NSMinX(Rect), NSMinY(Rect), NSMaxX(Rect), NSMaxY(Rect))
GSComponent.box = property(__GSComponent_get_box_, doc="the bounding box of the component: (xMin, yMin, xMax, yMax)")

def __GSComponent_round_(self):
	(xx, xy, yx, yy, dx, dy) = self.transformStruct()
	self.setTransformStruct_((xx, xy, yx, yy, int(round(dx)), int(round(dy))))
GSComponent.round = __GSComponent_round_

def __GSComponent_draw_(self, pen):
	pen.addComponent(self.baseGlyph, self.transformation)
	# else:
	#	# It's an "old" 'Fab pen
	#	pen.addComponent(self.baseGlyph, self.offset, self.scale)
GSComponent.draw = __GSComponent_draw_

GSComponent.drawPoints = __GSComponent_draw_

def RComponent(baseGlyphName=None, offset=(0,0), scale=(1,1), transform=None):
	return GSComponent(baseGlyphName, offset, scale, transform)

RAnchor = GSAnchor

def __GSAnchor_draw_(self, pen):
	"""draw the object with a point pen"""
	pen.beginPath()
	pen.addPoint((self.x, self.y), segmentType="move", smooth=False, name=self.name)
	pen.endPath()

GSAnchor.drawPoints = __GSAnchor_draw_

class RKerning(BaseKerning):
	_title = "GlyphsKerning"

class RGroups(BaseGroups):
	_title = "GlyphsGroups"

class RLib(BaseLib):
	_title = "GlyphsLib"

class RInfo(BaseInfo):
	
	_title = "GlyphsFontInfo"
	
	def __init__(self, RFontObject):
		#BaseInfo.__init__(self)
		self._object = RFontObject
		#self.baseAttributes = ["_object", "changed", "selected", "getParent"]
		#_renameAttributes = {"openTypeNameManufacturer": "manufacturer"};
	
	def __setattr__(self, attr, value):
		# check to see if the attribute has been
		# deprecated. if so, warn the caller and
		# update the attribute and value.
		
		if attr in self._deprecatedAttributes:
			newAttr, newValue = ufoLib.convertFontInfoValueForAttributeFromVersion1ToVersion2(attr, value)
			note = "The %s attribute has been deprecated. Use the new %s attribute." % (attr, newAttr)
			warn(note, DeprecationWarning)
			attr = newAttr
			value = newValue
		
		_baseAttributes = ["_object", "changed", "selected", "getParent"]
		_renameAttributes = {"openTypeNameManufacturer": "manufacturer",
						  "openTypeNameManufacturerURL": "manufacturerURL",
								 "openTypeNameDesigner": "designer",
							  "openTypeNameDesignerURL": "designerURL",
								  # "openTypeNameLicense": "license",
								  # "openTypeNameLicenseURL": "licenseURL",
											 "fontName": "postscriptFontName",
											"vendorURL": "manufacturerURL",
											 "uniqueID": "postscriptUniqueID",
											"otMacName": "openTypeNameCompatibleFullName" };
		_masterAttributes = ["postscriptUnderlinePosition",
							 "postscriptUnderlineThickness",
							 "openTypeOS2StrikeoutSize",
							 "openTypeOS2StrikeoutPosition"]
		# setting a known attribute
		if attr in _masterAttributes:
			if type(value) == type([]):
				value = NSMutableArray.arrayWithArray_(value)
			elif type(value) == type(1):
				value = NSNumber.numberWithInt_(value)
			elif type(value) == type(1.2):
				value = NSNumber.numberWithFloat_(value)
			
			if attr in _renameAttributes:
				attr = _renameAttributes[attr]
			
			self._object._font.fontMasterAtIndex_(self._object._master).setValue_forKey_(value, attr)
			return
		
		if attr not in _baseAttributes:
			try:
				if type(value) == type([]):
					value = NSMutableArray.arrayWithArray_(value)
				elif type(value) == type(1):
					value = NSNumber.numberWithInt_(value)
				elif type(value) == type(1.2):
					value = NSNumber.numberWithFloat_(value)
				
				if attr in _renameAttributes:
					attr = _renameAttributes[attr]
				
				self._object._font.setValue_forKey_(value, attr)
			except:
				raise AttributeError("Unknown attribute %s." % attr)
			return
		elif attr in self.__dict__ or attr in self._baseAttributes:
			super(BaseInfo, self).__setattr__(attr, value)
		else:
			raise AttributeError("Unknown attribute %s." % attr)
	
	def __getattr__(self, attr):
		_baseAttributes = ["_object", "changed", "selected", "getParent"]
		_renameAttributes = {
							 "openTypeNameManufacturer": "manufacturer",
						  "openTypeNameManufacturerURL": "manufacturerURL",
								 "openTypeNameDesigner": "designer",
							  "openTypeNameDesignerURL": "designerURL",
							}
		try:
			gsFont = self._object._font
			value = gsFont.valueForKey_(attr)
			if value is None and attr in _renameAttributes:
				value = gsFont.valueForKey_(_renameAttributes[attr])
			if value is None:
				Instance = gsFont.fontMasterAtIndex_(self._object._master)
				if Instance is None:
					raise ValueError("The font has no Instance")
				value = Instance.valueForKey_(attr)
				if value is None and attr in _renameAttributes:
					value = Instance.valueForKey_(_renameAttributes[attr])
				if value is None:
					if attr == "postscriptFullName" or attr == "fullName":
						value = "%s-%s" % (gsFont.valueForKey_("familyName"), Instance.name)
					elif attr == "postscriptFontName" or attr == "fontName":
						value = "%s-%s" % (gsFont.valueForKey_("familyName"), Instance.name)
						value = value.replace(" ", "")
			return value
		except:
			raise AttributeError("Unknown attribute %s." % attr)

class RFeatures(BaseFeatures):
	_title = "GlyphsFeatures"
	
	def __init__(self, font):
		super(RFeatures, self).__init__()
		self._object = font
	def _get_text(self):
		naked = self._object
		features = []
		if naked.classes:
			for aClass in naked.classes:
				features.append(aClass.name+" = ["+aClass.code+"];\n")
		features.append("\n")
		features.append(naked.features.text())
		return "".join(features)
	
	def _set_text(self, value):
		from robofab.tools.fontlabFeatureSplitter import splitFeaturesForFontLab
		classes, features = splitFeaturesForFontLab(value)
		naked = self._object
		for OTClass in classes.splitlines():
			naked.addClassFromCode_( OTClass )
		naked.setFeatures_(None)
		for featureName, featureText in features:
			f = GSFeature()
			f.setName_(featureName)
			f.setCode_(featureText[featureText.find("{")+1: featureText.rfind( "}" )].strip(" \n"))
			naked.addFeature_(f)

	text = property(_get_text, _set_text, doc="raw feature text.")

from AppKit import *
from vanilla.vanillaBase import VanillaBaseObject

class GlyphPreviewView(NSView):
	
	def setGlyph_(self, glyph):
		self._glyph = glyph
	
	def drawRect_(self, rect):
		frame = self.frame()
		NSColor.whiteColor().set()
		NSRectFill(frame)
		try:
			if self._glyph is not None:
				print self._glyph.__class__.__name__, isinstance(self._glyph, GSLayer)
			
				if self._glyph.__class__.__name__ == "NSKVONotifying_GSLayer":
					layer = self._glyph
				elif isinstance(self._glyph, RGlyph):
					layer = self._glyph._layer
				if layer:
					layer.drawInFrame_(frame)
		except:
			import traceback
			print traceback.format_exc()

class GlyphPreview(VanillaBaseObject):

	"""
	A control that allows for showing a glyph

	GlyphPreview objects handle GSLayer or RGlyph
		from vanilla import *
		from objectsGS import GlyphPreview
		class GlyphPreviewDemo(object):
			def __init__(self):
				self.title = "Glyph Preview"
				self.w = FloatingWindow((200, 200), self.title, closable=False)
				glyph = Glyphs.font.selectedLayers[0]
				self.w.Preview = GlyphPreview((0, 0, 0, 0), glyph=glyph)
				self.w.open()
		
		GlyphPreviewDemo()

	**posSize** Tuple of form *(left, top, width, height)* representing the position and size of the color well.

	**glyph** A *GSLayer* or a *RGlyph* object. If *None* is given, the view will be white.
	"""

	nsGlyphPreviewClass = GlyphPreviewView

	def __init__(self, posSize, glyph=None):
		self._setupView(self.nsGlyphPreviewClass, posSize)
		self._nsObject.setGlyph_(glyph)
	
