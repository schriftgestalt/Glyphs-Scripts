#MenuTitle: Autopsy 1.2
# encoding: utf-8



########################################################################
#
#   Autopsy Visual Font Auditing
#   1.2
#
#   Version for Glyphs (glyphsapp.com)
#   (c) 2009 by Yanone
#   2013 Georg Seifert, porting to use CoreGraphics instead of RepordLab to write PDF
#
#   http://www.yanone.de/typedesign/autopsy/
#
#   GPLv3 or later
#
########################################################################


from AppKit import *
import time, os, string, math, random

from Quartz.CoreGraphics import *

try:
	from vanilla import *
	from vanilla.dialogs import *
except:
	Message("Missing Library", "Please install the vanilla library from https://github.com/typesupply/vanilla")
	raise ImportError
cm = 72/2.54
mm = cm / 10
A4 = (595.276, 841.89)
letter = (612, 792)


##### Misc.

class Ddict(dict):
	def __init__(self, default=None):
		self.default = default
	   
	def __getitem__(self, key):
		if not self.has_key(key):
			self[key] = self.default()
		return dict.__getitem__(self, key)

def setup_binding_CheckBox(self, Object, KeyPath, options = objc.nil):
	self._nsObject.subviews()[0].bind_toObject_withKeyPath_options_("value", Object, "values."+KeyPath, options)
	
CheckBox.binding = setup_binding_CheckBox

def setup_binding_EditText(self, Object, KeyPath, options = objc.nil):
	self._nsObject.bind_toObject_withKeyPath_options_("value", Object, "values."+KeyPath, options)

EditText.binding = setup_binding_EditText

def del_binding(self, Object, KeyPath):
	Object.unbind_("value")
CheckBox.unbind = del_binding


##### Settings

programname = 'Autopsy'
programversion = '1.2'
releasedate = '201311100012'
verbose = False

availablegraphs = ('width', 'bboxwidth', 'bboxheight', 'highestpoint', 'lowestpoint', 'leftsidebearing', 'rightsidebearing')

graphrealnames = {
	'width' : 'Width',
	'bboxwidth' : 'BBox Width',
	'bboxheight' : 'BBox Height',
	'highestpoint' : 'BBox Highest',
	'lowestpoint' : 'BBox Lowest',
	'leftsidebearing' : 'L Sidebearing',
	'rightsidebearing' : 'R Sidebearing',
	}


pagemargin = Ddict(dict)
pagemargin['left'] = 12
pagemargin['right'] = 10
pagemargin['top'] = 8
pagemargin['bottom'] = 11
scrapboard = Ddict(dict)
graphcoords = Ddict(dict)

# separator between the scrapboard and the tablesboard
headmargin = 15 # mm
separator = 8 # mm
tableseparator = 3 # mm
roundedcorners = 3 # (pt?)
guidelinedashed = (3, 3) # pt on, pt off

# Colors
colourguides = (1, .5, 0, 0)
colourglobalguides = (0, 1, 1, 0)

# Headline
headerheight = 8 # mm
headlinefontsize = 14
#pdfcolour = (0, .05, 1, 0)
pdfcolour = (.25, 0, 1, 0)
#headlinefontcolour = (.25, .25, 1, .8)
headlinefontcolour = (0, 0, 0, 1)


pdffont = Ddict(dict)
pdffont['Regular'] = 'Courier'
pdffont['Bold'] = 'Courier-Bold'


graphcolour = Ddict(dict)
graphcolour['__default__'] = pdfcolour
graphcolour['width'] = (0, .9, .9, 0)
graphcolour['bboxwidth'] = (0, .75, .9, 0)
graphcolour['bboxheight'] = (0, .5, 1, 0)
graphcolour['highestpoint'] = (0, .3, 1, 0)
graphcolour['lowestpoint'] = (0, .1, 1, 0)
graphcolour['leftsidebearing'] = (0, .75, .25, 0)
graphcolour['rightsidebearing'] = (.25, .75, .25, 0)

# Metrics
glyphcolour = (0, 0, 0, 1)
xrayfillcolour = (0, 0, 0, .4)
metricscolour = (0, 0, 0, .5)
metricslinewidth = .5 # pt
scrapboardcolour = (0, 0, 0, 1)
drawboards = False


# Graphs
#tablenamefont = pdffont['Regular']
graphnamefontsize = 8
#pointsvaluefont = pdffont['Regular']
pointsvaluefontsize = 8


############ Classes


class Report:
	def __init__(self):
		self.gridcolour = metricscolour
		self.strokecolour = pdfcolour
		self.gridwidth = metricslinewidth
		self.strokewidth = 1
		self.values = [] # (value, glyphwidth, glyphheight)
		self.pointslist = []
#		self.scope = 'local' # local or global (relative to this single glyph, or to all glyphs in the pdf)
		self.glyphname = ''
		self.graphname = ''
		
		self.min = 0
		self.max = 0
		self.sum = 0
		ratio = 0

	def addvalue(self, value):
		self.values.append(value)
		
		if len(self.values) == 1:
			self.min = value[0]
			self.max = value[0]
		
		if value[0] > self.max:
			self.max = value[0]
		if value[0] < self.min:
			self.min = value[0]
		self.sum += value[0]

	def draw(self):
		global myDialog
		global globalscopemin, globalscopemax
		global glyphs
		
		drawrect(self.left * mm, self.bottom * mm, self.right * mm, self.top * mm, '', self.gridcolour, self.gridwidth, None, roundedcorners)

		r = .05
		mymin = self.min - int(math.fabs(self.min) * r)
		mymax = self.max + int(math.fabs(self.max) * r)


		if self.scope == 'global':
			
			# Walk through the other graphs and collect their min and max values
			for glyph in glyphs:
				
				try:
					if reports[glyph][self.graphname].min < mymin:
						mymin = reports[glyph][self.graphname].min
				except:
					mymin = reports[glyph][self.graphname].min
				
				try:
					if reports[glyph][self.graphname].max > mymax:
						mymax = reports[glyph][self.graphname].max
				except:
					mymax = reports[glyph][self.graphname].max
				
		if mymax - mymin < 10:
			mymin -= 5
			mymax += 5

		pointslist = []

		
		if not Glyphs.boolDefaults["com_yanone_Autopsy_PageOrientation_landscape"]:
			if Glyphs.boolDefaults["com_yanone_Autopsy_drawpointsvalues"] == 1:
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.left * mm + 1*mm, self.bottom * mm - 3*mm, str(int(mymin)))
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.right * mm - 5*mm, self.bottom * mm - 3*mm, str(int(mymax)))
			
			try:
				localratio = (self.right - self.left) / (mymax - mymin)
			except:
				localratio = 0

			try:
				y = self.top - (self.values[0][2] / 2 / mm * ratio)
			except:
				y = self.top

			for i, value in enumerate(self.values):
				x = self.left + (value[0] - mymin) * localratio
				pointslist.append((value[0], x, y))
				try:
					y -= self.values[i+1][2] / mm * ratio
				except:
					pass
			
		else:
			if Glyphs.boolDefaults["com_yanone_Autopsy_drawpointsvalues"] == 1:
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.right * mm + 1*mm, self.bottom * mm + 1*mm, str(int(mymin)))
				DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, self.right * mm + 1*mm, self.top * mm - 3*mm, str(int(mymax)))
#			DrawText(pdffont['Regular'], graphnamefontsize, self.gridcolour, self.left * mm + 1.7*mm, self.top * mm - 4*mm, graphrealnames[self.graphname])

			try:
				localratio = (self.top - self.bottom) / (mymax - mymin)
			except:
				localratio = 0

			try:
				position = self.left + (self.values[0][1] / 2 / mm * ratio)
			except:
				position = self.left

			for i, value in enumerate(self.values):
				x = position
				y = self.bottom + (value[0] - mymin) * localratio
				pointslist.append((value[0], x, y))
				try:
					position += self.values[i+1][1] / mm * ratio
				except:
					pass


		# Calculate thickness of stroke according to scope of graph
		minthickness = 2
		maxthickness = 8
		thickness = -.008 * (mymax - mymin) + maxthickness
		if thickness < minthickness:
			thickness = minthickness
		elif thickness > maxthickness:
			thickness = maxthickness
		
		DrawTableLines(pointslist, self.strokecolour, thickness)
		DrawText(pdffont['Regular'], graphnamefontsize, self.gridcolour, self.left * mm + 1.7*mm, self.top * mm - 4*mm, graphrealnames[self.graphname])


#################################

def SetScrapBoard(pageratio):
	global myDialog
	
	scrapboard['left'] = pagemargin['left']
	scrapboard['right'] = pagewidth/mm - pagemargin['right']
	scrapboard['top'] = pageheight/mm - pagemargin['top'] - headmargin
	scrapboard['bottom'] = pagemargin['bottom']
	graphcoords['left'] = pagemargin['left']
	graphcoords['right'] = pagewidth/mm - pagemargin['right']
	graphcoords['top'] = pageheight/mm - pagemargin['top'] - headmargin
	graphcoords['bottom'] = pagemargin['bottom']

	# Recalculate drawing boards
	if not Glyphs.defaults["com_yanone_Autopsy_PageOrientation_landscape"]:
		availablewidth = pagewidth/mm - pagemargin['left'] - pagemargin['right']
		partial = availablewidth * pageratio
		scrapboard['right'] = pagemargin['left'] + partial - separator / 2
		graphcoords['left'] = scrapboard['right'] + separator
	else:
		availablewidth = pageheight/mm - pagemargin['top'] - pagemargin['bottom'] - headmargin
		partial = availablewidth * pageratio
		scrapboard['bottom'] = pageheight/mm - headmargin - partial + separator / 2
		graphcoords['top'] = scrapboard['bottom'] - separator 



##################################################################
#
#   PDF section
#


def DrawText(font, fontsize, fontcolour, x, y, text):
	attributes = {NSFontAttributeName : NSFont.fontWithName_size_(font, fontsize), NSForegroundColorAttributeName: NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(fontcolour[0], fontcolour[1], fontcolour[2], fontcolour[3], 1)}
	String = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
	String.drawAtPoint_((x, y))

def DrawTableLines(list, colour, thickness):

	global myDialog

	for i, point in enumerate(list):

		try:
			drawline(list[i][1]*mm, list[i][2]*mm, list[i+1][1]*mm, list[i+1][2]*mm, colour, thickness, None)
		except:
			pass

		NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(colour[0], colour[1], colour[2], colour[3], 1).set()
		Rect = NSMakeRect(point[1]*mm-(thickness), point[2]*mm-(thickness), thickness*2, thickness*2)
		NSBezierPath.bezierPathWithOvalInRect_(Rect).fill()
		if Glyphs.defaults["com_yanone_Autopsy_drawpointsvalues"] == 1:
			DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, point[1]*mm + (thickness/6+1)*mm, point[2]*mm - (thickness/6+2.5)*mm, str(int(round(point[0]))))

def DrawHeadlineIntoPage(text):

	drawrect(pagemargin['left']*mm, pageheight - pagemargin['top']*mm - headerheight*mm, pagewidth - pagemargin['right']*mm, pageheight - pagemargin['top']*mm, pdfcolour, None, 0, None, roundedcorners)
	DrawText(pdffont['Bold'], headlinefontsize, headlinefontcolour, 2*mm + pagemargin['left']*mm, 2.2*mm + pageheight - pagemargin['top']*mm - headerheight*mm, text)

def DrawMetrics(f, glyph, xoffset, yoffset, ratio):
	global myDialog
	#g = Glyph(glyph)
	g = glyph.layers[0]
	mywidth = g.width
	if mywidth == 0:
		mywidth = g.bounds.size.width
		
	# Draw metrics
	if Glyphs.defaults["com_yanone_Autopsy_drawmetrics"] == 1:
		# Versalhöhe
		drawline(xoffset*mm, yoffset*mm + capheight(f) * ratio, xoffset*mm + mywidth*ratio, yoffset*mm + capheight(f) * ratio, metricscolour, metricslinewidth, None)
		# x-Höhe
		drawline(xoffset*mm, yoffset*mm + xheight(f) * ratio,   xoffset*mm + mywidth*ratio, yoffset*mm + xheight(f) * ratio, metricscolour, metricslinewidth, None)
		# Grundlinie
		drawline(xoffset*mm, yoffset*mm,                        xoffset*mm + mywidth*ratio, yoffset*mm, metricscolour, metricslinewidth, None)

		# Bounding Box
		drawrect(xoffset*mm, yoffset*mm + descender(f)*ratio,   xoffset*mm + mywidth*ratio, yoffset*mm + ascender(f)*ratio, '', metricscolour, metricslinewidth, None, 0)

	# Draw guidelines
	if Glyphs.boolDefaults["com_yanone_Autopsy_drawguidelines"] == 1 and False: #GSNotImplemented

		# Local vertical guides
		for guide in g.vguides:
			try:
				a = (ascender(f)) * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = guide.position / mm * ratio
			y1 = (0 - descender(f)) / mm * ratio
			x2 = (guide.position + a) / mm * ratio
			y2 = (ascender(f) - descender(f)) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourguides, metricslinewidth, guidelinedashed)

		# Global vertical guides
		for guide in f.vguides:
			try:
				a = (ascender(f)) * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = guide.position / mm * ratio
			y1 = (0 - descender(f)) / mm * ratio
			x2 = (guide.position + a) / mm * ratio
			y2 = (ascender(f) - descender(f)) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourglobalguides, metricslinewidth, guidelinedashed)

		# Local horizontal guides
		for guide in g.hguides:
			try:
				a = g.width * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = 0
			y1 = (guide.position - descender(f)) / mm * ratio
			x2 = g.width / mm * ratio
			y2 = (guide.position - descender(f) + a) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourguides, metricslinewidth, guidelinedashed)

		# Global horizontal guides
		for guide in f.hguides:
			try:
				a = g.width * math.tan(math.radians(guide.angle))
			except:
				a = 0
			x1 = 0
			y1 = (guide.position - descender(f)) / mm * ratio
			x2 = g.width / mm * ratio
			y2 = (guide.position - descender(f) + a) / mm * ratio
			drawline(xoffset*mm + x1*mm, yoffset*mm + y1*mm, xoffset*mm + x2*mm, yoffset*mm + y2*mm, colourglobalguides, metricslinewidth, guidelinedashed)

	# Draw font names under box
	if Glyphs.defaults["com_yanone_Autopsy_fontnamesunderglyph"] == 1:
		DrawText(pdffont['Regular'], pointsvaluefontsize, glyphcolour, xoffset*mm + 2, yoffset*mm - 8, f.full_name)
#		output(f)


def PSCommandsFromGlyph(glyph):

	CommandsList = []

	for path in glyph.paths:
		lastNode = None
		if path.closed:
			lastNode = path.nodes[-1]
		else:
			lastNode = path.nodes[0]
		CommandsList.append(('moveTo', (lastNode.x, lastNode.y)))
		for i, node in enumerate(path.nodes):
			
			if node.type == GSOFFCURVE:
				CommandsList.append(('close', (node.x, node.y)))
			
			#if node.type == nMOVE:
			#	CommandsList.append(('moveTo', (node.x, node.y)))

			if node.type == GSLINE:
				CommandsList.append(('lineTo', (node.x, node.y)))

			if node.type == GSCURVE:
				CurveCommandsList = []
				CurveCommandsList.append('curveTo')
				
				#for point in node.points:
				CurveCommandsList.append( (node.x, node.y) )
				point = path.nodes[i-2]
				CurveCommandsList.append( (point.x, point.y) )
				point = path.nodes[i-1]
				CurveCommandsList.append( (point.x, point.y) )
				
				CommandsList.append(CurveCommandsList)

	return CommandsList

def DrawGlyph(f, glyph, PSCommands, xoffset, yoffset, ratio, fillcolour, strokecolour, strokewidth, dashed):
	
	if not PSCommands:
		
		type = "glyph"
		
		# Copy glyph into memory (so remove overlap won't affect the current font)
		g = glyph.layers[0]
		if len(g.components) > 0:
			for component in g.components:
				position = component.position
				DrawGlyph(f, component.component, None, xoffset+(position.x*ratio/mm), yoffset+(position.y*ratio/mm), ratio, fillcolour, strokecolour, strokewidth, dashed)
	
		# Glyph has nodes of its own
		if len(g.paths):
			PSCommands = PSCommandsFromGlyph(g)
			#print PSCommands
		else:
			PSCommands = ()
		
	else:
		type = "PScommands"


	if PSCommands:
		p = NSBezierPath.bezierPath()
		
		for command in PSCommands:
		
			if command[0] == 'moveTo':
				try:
					p.close()
				except:
					pass
	
				x = xoffset*mm + command[1][0] * ratio
				y = yoffset*mm + command[1][1] * ratio
				p.moveToPoint_((x, y))
				#print "('moveTo', (%s, %s))," % (command[1][0], command[1][1])
	
			if command[0] == 'lineTo':
				x = xoffset*mm + command[1][0] * ratio
				y = yoffset*mm + command[1][1] * ratio
				p.lineToPoint_((x, y))
				#print "('lineTo', (%s, %s))," % (command[1][0], command[1][1])
	
			if command[0] == 'curveTo':
	
				points = []
				
				for point in command[1:]:
					points.append( (xoffset*mm + point[0] * ratio, yoffset*mm + point[1] * ratio) )
				
				p.curveToPoint_controlPoint1_controlPoint2_(points[0], points[1], points[2])
	
		p.closePath()
		if fillcolour:
			NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(fillcolour[0], fillcolour[1], fillcolour[2], fillcolour[3], 1).set()
			p.fill()
		if strokecolour:
			NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(strokecolour[0], strokecolour[1], strokecolour[2], strokecolour[3], 1).set()
			if dashed:
				p.setLineDash_count_phase_(dashed, 2, 0.0)
			p.setLineWidth_(strokewidth)
			p.stroke()




######### draw primitives

def drawline(x1, y1, x2, y2, colour, strokewidth, dashed):

	NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(colour[0], colour[1], colour[2], colour[3], 1).set()
	Path = NSBezierPath.bezierPath()
	Path.moveToPoint_((x1, y1))
	Path.lineToPoint_((x2, y2))
	Path.setLineWidth_(strokewidth)
	
	if dashed:
		Path.setLineDash_count_phase_(dashed, 2, 0.0)
	Path.stroke()

def drawrect(x1, y1, x2, y2, fillcolour, strokecolour, strokewidth, dashed, rounded):
	Rect = NSMakeRect(x1, y1, x2 - x1, y2 - y1)
	Path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(Rect, rounded, rounded)
	if fillcolour:
		NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(fillcolour[0], fillcolour[1], fillcolour[2], fillcolour[3], 1).set()
		Path.fill()
	if strokecolour:
		Path.setLineWidth_(strokewidth)
		if dashed:
			Path.setLineDash_count_phase_(dashed, 2, 0.0)
		NSColor.colorWithDeviceCyan_magenta_yellow_black_alpha_(strokecolour[0], strokecolour[1], strokecolour[2], strokecolour[3], 1).set()
		Path.stroke()

# collects the glyphs that should be displayed
# and returns list of glyph names
def collectglyphnames():
	
	glyphlist = []
	Font = Glyphs.orderedDocuments()[0].font
	for Layer in Font.selectedLayers:
		glyphlist.append(Layer.parent.name)
	
	return glyphlist

def capheight(f):
	return f.masters[0].capHeight

def xheight(f):
	return f.masters[0].xHeight

def descender(f):
	return f.masters[0].descender

def ascender(f):
	return f.masters[0].ascender

def unicode2hex(u):
	return string.zfill(string.upper(hex(u)[2:]), 4)

errortexts = []
errors = 0

def raiseerror(text):
	global errors, errorslist
	errortexts.append(text)
	try:
		errors += 1
	except:
		errors = 1


def CheckForUpdates():
	return
	if Defaults['com_yanone_Autopsy_checkforupdates']:
		import webbrowser, urllib
		try:
			if int(releasedate) < int(urllib.urlopen('http://www.yanone.de/typedesign/autopsy/latestreleasedate.txt').read()):
				x = fl.Message('Hey, I was reincarnated as a newer version.\nDo you want to connect to my download page on the internet?')
				if x == 1:
					webbrowser.open('http://www.yanone.de/typedesign/autopsy/download.php', 1, 1)
		except:
			pass # No network connection

##### MAIN

def main():

	global ratio
	global myDialog
	global errors, errorstexts
	global glyphs
	global reports

	CheckForUpdates()
	
	# Clear console
	if verbose:
		Glyphs.clearLog()
	output('-- main --')
	
  # Dialog stuff
	result = None
	NameList = []

	# Check, if fonts are present
	if len(Glyphs.fonts) < 1:
		raiseerror("No fonts open in Glyphs.")
	else:
		# Check, if fonts have a full_name
		# full_name_missing = 0
		# for f in Glyphs.fonts:
		# 	if not f.full_name:
		# 		full_name_missing += 1
		# if full_name_missing:
		# 	raiseerror("Some fonts don't have a 'Full Name'. Autopsy uses the 'Full Name' for handling fonts.\nPlease fill it out in the 'Font Info' window.")

		# Collect glyph names
		glyphs = collectglyphnames()
		if not glyphs:
			raiseerror("No glyphs selected.")
		
	
	# Initial sorting of fonts by width, weight

	widths_plain = '''Ultra-condensed	1
Compressed	1
Extra-condensed	2
Condensed	3
Semi-condensed	4
Narrow	4
Compact	4
Medium (normal)	5
Normal	5
Regular	5
Medium	5
Semi-extended	6
Wide	6
Semi-expanded	6
Expanded	7
Extended	7
Extra-extended	8
Extra-expanded	8
Ultra-expanded	9
Ultra-extended	9'''

	weights_plain = '''Thin	250
Hairline	250
Ultra Light	250
Micro	300
Extra Light	300
Fine	300
Slim	300
Dry	300
Clair	300
Skinny	300
Light	350
Semi Light	375
Plain	400
Gamma	400
Normal (Regular)	400
Regular	400
Book	450
News	450
Text	500
Medium	500
Beta	500
Median	500
DemiBold	500
SemiBold	500
Semi Bold	600
Alpha	600
Demi Bold	600
Bold	700
Boiled	700
Noir	700
Fett	700
Not That Fat	700
Extra Boiled	750
Extra Bold	750
Heavy	800
Mega	800
ExtraBold	800
Black	900
UltraBlack	900
Ultra Black	900
Fat	950
Ultra	1000
Super	1000
ExtraBlack	1000
Extra Black	1000'''
	
	# Normal mode
	if not errors:

		# Add fonts to NameList
		if len(Glyphs.fonts[0].masters) == 1:
			mode = 'normal'
		
			widths = Ddict(dict)
			for width in widths_plain.split("\n"):
				tmp = width.split("\t")
				widths[tmp[0]] = tmp[1]
					
			weights = Ddict(dict)
			for weight in weights_plain.split("\n"):
				tmp = weight.split("\t")
				weights[tmp[0]] = tmp[1]
		
			FontList = []
			for f in Glyphs.fonts:
				# exclude MM
				if len(f.masters) == 1:
					
					# width
					if f.masters[0].width and f.masters[0].width in widths:
						width = widths[f.masters[0].width]
					else:
						width = 500
					
					# weights
					#print "__weights", weights
					weight = 0
					try:
						weight = weights[f.masters[0].weight]
					except:
						pass
					
					if weight < 10:
						weight = 400
					
					# # familyname
					# if f.family_name:
					# 	familyname = f.family_name
					# else:
					# 	familyname = '__default__'
					familyname = f.familyName
					if len(f.instances) > 0:
						familyname += " "+f.instances[0].name
					
					FontList.append((width, weight, familyname))
			
			FontList.sort()
			
			for listentry in FontList:
				NameList.append(listentry[2])
	
		# MM-mode
		elif len(Glyphs.fonts[0].masters) > 1:
			mode = 'MM'
			familyname = f.familyName+" "+f.masters[0].name
			NameList.append(f)

	# Some error handling
#	if not NameList:
#		raiseerror("No fonts open in FontLab.")

	
	# Call Dialog
	if NameList and not errors:
		myDialog = _listMultiSelect(mode, NameList)
		Result = myDialog.Run()
		if Result == NSOKButton:
			NameList = myDialog.selection
			if NameList:
				result = []
				for anyName in NameList:
					if mode == 'normal':
						result.append(getFontByFullname(anyName))
					elif mode == 'MM':
						__list = anyName.split("/")
						_InstanceList = []
						for l in __list:
							try:
								_InstanceList.append(int(l))
							except:
								pass
						instance = Font(Font, _InstanceList)
						instance.full_name += ' ' + anyName
						result.append(instance)

			else: raiseerror("No fonts have been selected. I can't work like that.")
		#else: raiseerror("Canceled by user (That's you).")
		#del myDialog
#	elif not NameList:
#		raiseerror("No fonts open in FontLab.")

		try:
			fonts = result
		except:
			fonts = []
				
		#if not myDialog.filename:
		#print "No file name specified. Where do you expect me to save the file?."



	
	if not errors and fonts and glyphs:
	
		starttime = time.time()

		
		global pagewidth, pageheight
		#global myDialog

		if not Glyphs.defaults["com_yanone_Autopsy_PageOrientation_landscape"]:
			if not Glyphs.defaults["com_yanone_Autopsy_PageSize_a4"]:
				pagewidth = letter[0]
				pageheight = letter[1]
			else:
				pagewidth = A4[0]
				pageheight = A4[1]
		else:
			if not Glyphs.defaults["com_yanone_Autopsy_PageSize_a4"]:
				pagewidth = letter[1]
				pageheight = letter[0]
			else:
				pagewidth = A4[1]
				pageheight = A4[0]
		
		#############
		#
		# Collect information about the glyphs
		#
	
		# Dimensions
		reports = Ddict(dict)
	
		glyphwidth = Ddict(dict)
		maxwidthperglyph = Ddict(dict)
		maxwidth = 0
		maxsinglewidth = 0
		glyphheight = Ddict(dict)
		maxheightperglyph = Ddict(dict)
		maxheight = 0
		maxsingleheight = 0
		
		for glyph in glyphs:
	
			glyphwidth[glyph] = 0
			glyphheight[glyph] = 0
			maxwidthperglyph[glyph] = 0
			maxheightperglyph[glyph] = 0
			reports[glyph]['width'] = Report()
			reports[glyph]['height'] = Report()
			reports[glyph]['bboxwidth'] = Report()
			reports[glyph]['bboxheight'] = Report()
			reports[glyph]['highestpoint'] = Report()
			reports[glyph]['lowestpoint'] = Report()
			reports[glyph]['leftsidebearing'] = Report()
			reports[glyph]['rightsidebearing'] = Report()
			
			for i_f, font in enumerate(fonts):
				FontMaster = font.masters[0]
				if font.glyphs.has_key(glyph):
					g = font.glyphs[glyph].layers[FontMaster.id]
					#print "__g", g
					glyphwidth[glyph] = g.width
					height = ascender(font) - descender(font)

					widthforgraph = glyphwidth[glyph]
					if widthforgraph == 0:
						widthforgraph = g.bounds.size.width
					heightforgraph = height
	
					# width of kegel
					reports[glyph]['width'].addvalue((glyphwidth[glyph], widthforgraph, heightforgraph))
					# sum of widths per glyph
					if reports[glyph]['width'].sum > maxwidth:
						maxwidth = reports[glyph]['width'].sum
					if reports[glyph]['width'].max > maxsinglewidth:
						maxsinglewidth = reports[glyph]['width'].max
						
					# height of kegel
					glyphheight[glyph] = height
					reports[glyph]['height'].addvalue((glyphheight[glyph], widthforgraph, heightforgraph))
					# sum of heights per glyph
					if reports[glyph]['height'].sum > maxheight:
						maxheight = reports[glyph]['height'].sum
					if reports[glyph]['height'].max > maxsingleheight:
						maxsingleheight = reports[glyph]['height'].max
					
					# BBox
					overthetop = 20000
					
					bbox = g.bounds
					
					if bbox.size.width < -1*overthetop or bbox.size.width > overthetop:
						reports[glyph]['bboxwidth'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['bboxwidth'].addvalue((bbox.size.width, widthforgraph, heightforgraph))
					
					if bbox.size.height < -1*overthetop or bbox.size.height > overthetop:
						reports[glyph]['bboxheight'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['bboxheight'].addvalue((bbox.size.height, widthforgraph, heightforgraph))
					
					
					if (bbox.origin.y + bbox.size.height) < -1*overthetop or (bbox.origin.y + bbox.size.height) > overthetop:
						reports[glyph]['highestpoint'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['highestpoint'].addvalue((bbox.origin.y + bbox.size.height, widthforgraph, heightforgraph))
					
					if bbox.origin.y < -1*overthetop or bbox.origin.y > overthetop:
						reports[glyph]['lowestpoint'].addvalue((0, widthforgraph, heightforgraph))
					else:
						reports[glyph]['lowestpoint'].addvalue((bbox.origin.y, widthforgraph, heightforgraph))
					
					# L + R sidebearing
					reports[glyph]['leftsidebearing'].addvalue((g.LSB, widthforgraph, heightforgraph))
					reports[glyph]['rightsidebearing'].addvalue((g.RSB, widthforgraph, heightforgraph))

		

		# Recalculate drawing boards
		numberoftables = 0
		# GSNotImplemented
		# for table in availablegraphs:
		# 	if eval('myDialog.graph_' + table):
		# 		numberoftables += 1

		if numberoftables < 3:
			numberoftables = 3
		try:
			r = 2.0 / numberoftables
		except:
			r = .8
		SetScrapBoard(r)

			
		# Calculate ratio
		if not NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_PageOrientation_landscape"]:
			ratio = (scrapboard['top'] - scrapboard['bottom']) / maxheight * mm
			ratio2 = (scrapboard['right'] - scrapboard['left']) / maxsinglewidth * mm
			maxratio = 0.3
			if ratio > maxratio:
				ratio = maxratio
			if ratio > ratio2:
				ratio = ratio2
		else:
			ratio = (scrapboard['right'] - scrapboard['left']) / maxwidth * mm
			ratio2 = (scrapboard['top'] - scrapboard['bottom']) / maxsingleheight * mm
			maxratio = 0.3
			if ratio > maxratio:
				ratio = maxratio
			if ratio > ratio2:
				ratio = ratio2
		
		
		xoffset = pagewidth/mm * 1/1.61
		yoffset = pageheight/mm * 1.61
		
		# PDF Init stuff
		filename = NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_filename"]
		tempFileName = NSTemporaryDirectory()+"%d.pdf"%random.randint(1000,100000)
		
		pageRect = CGRectMake (0, 0, pagewidth, pageheight)
		
		fileURL = NSURL.fileURLWithPath_(tempFileName)
		pdfContext = CGPDFContextCreateWithURL(fileURL, pageRect, None)
		
		CGPDFContextBeginPage(pdfContext, None)
		pdfNSGraphicsContext = NSGraphicsContext.graphicsContextWithGraphicsPort_flipped_(pdfContext, False)
		NSGraphicsContext.saveGraphicsState()
		NSGraphicsContext.setCurrentContext_(pdfNSGraphicsContext)
		
		NSRectFill(((-100, -100), (200, 200)))
		
		
		# Draw front page
		output('-- font page --')
		
		drawrect(-3*mm, -3*mm, pagewidth + 3*mm, pageheight + 3*mm, pdfcolour, None, None, None, 0)



		# Try to get a random glyph from a random font with nodes
		# try not more than 10000 times
		glyphfound = False

		randomfont = fonts[random.randint(0, len(fonts) - 1)]
		randomglyphindex = random.randint(0, len(randomfont) - 1)
		g = randomfont.glyphs[randomglyphindex]

		if g is not None:
			glyphfound = True
		tries = 0
		while glyphfound == False and tries < 10000:
			randomfont = fonts[random.randint(0, len(fonts) - 1)]
			randomglyphindex = random.randint(0, len(randomfont) - 1)
			g = randomfont[randomglyphindex]
			if (g.nodes_number or g.components):
				glyphfound = True
			tries += 1
#		if (g.nodes or g.components):
#			glyphfound = True

		# if random didn't help, get first glyph with nodes
		if not glyphfound:
			for gi in range(len(fonts[0])):
				if fonts[0][gi].nodes_number or fonts[0][gi].components:
					g = fonts[0][gi]
			
		
		bbox = g.layers[0].bounds
		if bbox.size.height > 1:
			localratio = .65 / bbox.size.height * (pageheight - yoffset)
		else:
			print "____NO height____"
			localratio = .65 / 300


		# draw logo and name
		logoyoffset = -5

		## YN
		ynlogo = [('moveTo', (350, 700)), ['curveTo', (0, 350), (138, 700), (0, 562)], ['curveTo', (350, 0), (0, 138), (138, 0)], ['curveTo', (700, 350), (562, 0), (700, 138)], ['curveTo', (350, 700), (700, 562), (562, 700)], ('moveTo', (548, 297)), ('lineTo', (542, 297)), ['curveTo', (536, 286), (536, 297), (536, 288)], ('lineTo', (536, 174)), ['curveTo', (510, 132), (536, 153), (531, 132)], ['curveTo', (481, 155), (496, 132), (489, 140)], ['curveTo', (416, 272), (481, 155), (435, 237)], ('lineTo', (416, 180)), ['curveTo', (422, 168), (416, 168), (420, 168)], ['curveTo', (434, 169), (425, 168), (430, 169)], ['curveTo', (451, 152), (444, 169), (451, 163)], ['curveTo', (430, 136), (451, 144), (445, 136)], ['curveTo', (399, 139), (421, 136), (413, 139)], ['curveTo', (365, 136), (386, 139), (374, 136)], ['curveTo', (345, 153), (350, 136), (345, 144)], ['curveTo', (362, 169), (345, 163), (352, 169)], ['curveTo', (374, 168), (366, 169), (371, 168)], ['curveTo', (380, 179), (376, 168), (380, 168)], ('lineTo', (380, 286)), ['curveTo', (374, 298), (380, 297), (376, 298)], ['curveTo', (362, 297), (371, 298), (368, 297)], ['curveTo', (347, 306), (355, 297), (350, 302)], ['curveTo', (332, 297), (345, 302), (340, 297)], ['curveTo', (320, 298), (326, 297), (326, 298)], ['curveTo', (316, 295), (319, 298), (318, 298)], ('lineTo', (261, 209)), ('lineTo', (261, 175)), ['curveTo', (267, 168), (261, 170), (263, 168)], ['curveTo', (281, 170), (270, 168), (274, 170)], ['curveTo', (296, 153), (291, 170), (296, 163)], ['curveTo', (275, 136), (296, 144), (291, 136)], ['curveTo', (241, 139), (262, 136), (254, 139)], ['curveTo', (208, 136), (228, 139), (221, 136)], ['curveTo', (188, 152), (194, 136), (188, 144)], ['curveTo', (205, 170), (188, 163), (195, 170)], ['curveTo', (217, 168), (211, 170), (212, 168)], ['curveTo', (223, 175), (219, 168), (223, 170)], ('lineTo', (223, 207)), ('lineTo', (168, 296)), ['curveTo', (164, 297), (167, 297), (165, 297)], ['curveTo', (153, 296), (160, 297), (158, 296)], ['curveTo', (134, 313), (139, 296), (134, 304)], ['curveTo', (152, 331), (134, 324), (141, 331)], ['curveTo', (186, 327), (165, 331), (175, 327)], ['curveTo', (215, 331), (197, 327), (203, 331)], ['curveTo', (234, 313), (229, 331), (234, 322)], ['curveTo', (213, 297), (234, 306), (230, 297)], ('lineTo', (212, 297)), ('lineTo', (243, 245)), ['curveTo', (273, 297), (251, 260), (267, 285)], ['curveTo', (268, 296), (270, 296), (268, 296)], ['curveTo', (249, 313), (254, 296), (249, 304)], ['curveTo', (268, 331), (249, 324), (256, 331)], ['curveTo', (298, 328), (275, 331), (287, 328)], ['curveTo', (332, 331), (308, 328), (322, 331)], ['curveTo', (348, 321), (339, 331), (345, 326)], ['curveTo', (365, 331), (350, 326), (356, 331)], ['curveTo', (389, 329), (369, 331), (378, 329)], ['curveTo', (413, 331), (399, 329), (406, 331)], ['curveTo', (431, 320), (428, 331), (430, 324)], ('lineTo', (433, 314)), ('lineTo', (500, 193)), ('lineTo', (500, 286)), ['curveTo', (490, 297), (500, 289), (500, 297)], ('lineTo', (482, 297)), ['curveTo', (465, 313), (472, 297), (465, 305)], ['curveTo', (486, 331), (465, 321), (471, 331)], ['curveTo', (516, 328), (496, 331), (504, 328)], ['curveTo', (547, 331), (526, 328), (536, 331)], ['curveTo', (566, 313), (561, 331), (566, 322)], ['curveTo', (548, 297), (566, 305), (561, 297)], ('moveTo', (359, 568)), ['curveTo', (422, 525), (385, 568), (408, 552)], ['curveTo', (486, 568), (436, 552), (459, 568)], ['curveTo', (544, 508), (518, 568), (544, 546)], ['curveTo', (422, 356), (544, 441), (472, 420)], ['curveTo', (301, 508), (372, 420), (301, 441)], ['curveTo', (359, 568), (301, 546), (326, 568)], ('moveTo', (206, 530)), ['curveTo', (193, 529), (202, 530), (197, 529)], ['curveTo', (176, 546), (183, 529), (176, 538)], ['curveTo', (197, 563), (176, 555), (182, 563)], ['curveTo', (231, 560), (209, 563), (216, 560)], ['curveTo', (264, 563), (244, 560), (252, 563)], ['curveTo', (284, 546), (278, 563), (284, 555)], ['curveTo', (268, 529), (284, 536), (275, 529)], ['curveTo', (255, 530), (263, 529), (260, 530)], ['curveTo', (249, 519), (253, 530), (249, 530)], ('lineTo', (249, 413)), ['curveTo', (255, 401), (249, 401), (253, 401)], ['curveTo', (268, 402), (259, 401), (263, 402)], ['curveTo', (284, 386), (277, 402), (284, 396)], ['curveTo', (264, 368), (284, 377), (278, 368)], ['curveTo', (232, 372), (248, 368), (244, 372)], ['curveTo', (196, 368), (217, 372), (215, 368)], ['curveTo', (176, 386), (182, 368), (176, 377)], ['curveTo', (193, 402), (176, 396), (183, 402)], ['curveTo', (206, 401), (198, 402), (201, 401)], ['curveTo', (211, 413), (207, 401), (211, 401)], ('lineTo', (211, 519)), ['curveTo', (206, 530), (211, 530), (207, 530)]]
		ynlogoring = [('moveTo', (350, 700)), ['curveTo', (0, 350), (138, 700), (0, 562)], ['curveTo', (350, 0), (0, 138), (138, 0)], ['curveTo', (700, 350), (562, 0), (700, 138)], ['curveTo', (350, 700), (700, 562), (562, 700)]]
		textyoffset = 0
		textxoffset = 0
		DrawGlyph(None, None, ynlogo, xoffset/mm - .5, 14.5 + logoyoffset, .05, headlinefontcolour, None, None, 1)
		DrawGlyph(None, None, ynlogoring, xoffset/mm - .5, 14.5 + logoyoffset, .05, None, (0,0,0,0), 3, (6,4))
		DrawText(pdffont['Regular'], 9, headlinefontcolour, textxoffset + xoffset + 15*mm, 22*mm + textyoffset + logoyoffset*mm, programname + ' ' + programversion + ' by Yanone')
		DrawText(pdffont['Regular'], 9, headlinefontcolour, textxoffset + xoffset + 15*mm, 18.4*mm + textyoffset + logoyoffset*mm, 'www.yanone.de/typedesign/autopsy/')

		## FSI
#		fsiwhite = [('moveTo', (483, 15)), ('lineTo', (1300, 15)), ('lineTo', (1300, 684)), ('lineTo', (483, 684))]
#		fsiyellow = [('moveTo', (17, 15)), ('lineTo', (479, 15)), ('lineTo', (479, 684)), ('lineTo', (17, 684))]
#		fsiblack = [('moveTo', (30, 671)), ('lineTo', (30, 29)), ('lineTo', (464, 29)), ('lineTo', (464, 671)), ('moveTo', (0, 700)), ('lineTo', (1322, 700)), ('lineTo', (1322, 0)), ('lineTo', (0, 0)), ('lineTo', (0, 700)), ('moveTo', (181, 225)), ['curveTo', (171, 183), (179, 215), (171, 191)], ['curveTo', (221, 162), (171, 159), (201, 162)], ('lineTo', (218, 150)), ['curveTo', (134, 152), (190, 150), (162, 152)], ['curveTo', (55, 150), (108, 152), (82, 150)], ('lineTo', (60, 162)), ['curveTo', (124, 220), (110, 159), (111, 179)], ('lineTo', (190, 446)), ['curveTo', (199, 490), (193, 455), (199, 480)], ['curveTo', (150, 509), (199, 513), (163, 509)], ('lineTo', (153, 522)), ['curveTo', (227, 519), (177, 521), (203, 519)], ['curveTo', (410, 522), (290, 519), (350, 521)], ('lineTo', (420, 431)), ('lineTo', (408, 431)), ['curveTo', (304, 509), (393, 497), (366, 510)], ['curveTo', (259, 506), (289, 509), (273, 508)], ('lineTo', (217, 358)), ('lineTo', (263, 358)), ['curveTo', (330, 416), (295, 358), (310, 370)], ('lineTo', (339, 416)), ('lineTo', (311, 274)), ('lineTo', (300, 274)), ['curveTo', (258, 346), (300, 310), (304, 346)], ('lineTo', (213, 346)), ('moveTo', (811, 508)), ['curveTo', (692, 545), (772, 531), (735, 545)], ['curveTo', (570, 433), (619, 545), (570, 500)], ['curveTo', (592, 370), (570, 409), (576, 388)], ['curveTo', (661, 337), (609, 354), (626, 348)], ('lineTo', (700, 325)), ['curveTo', (770, 253), (747, 311), (770, 288)], ['curveTo', (742, 198), (770, 231), (761, 212)], ['curveTo', (681, 181), (726, 186), (711, 181)], ['curveTo', (577, 215), (642, 181), (609, 191)], ('lineTo', (556, 178)), ['curveTo', (681, 143), (595, 155), (634, 143)], ['curveTo', (768, 169), (716, 143), (742, 151)], ['curveTo', (821, 260), (802, 190), (821, 225)], ['curveTo', (796, 329), (821, 284), (811, 311)], ['curveTo', (728, 367), (780, 347), (761, 356)], ('lineTo', (683, 381)), ['curveTo', (619, 444), (637, 395), (619, 413)], ['curveTo', (695, 508), (619, 482), (648, 508)], ['curveTo', (791, 473), (729, 508), (752, 499)], ('lineTo', (811, 508)), ('moveTo', (1017, 159)), ('lineTo', (1205, 159)), ('lineTo', (1205, 252)), ('lineTo', (1159, 252)), ('lineTo', (1159, 439)), ('lineTo', (1205, 439)), ('lineTo', (1205, 533)), ('lineTo', (1017, 533)), ('lineTo', (1017, 439)), ('lineTo', (1063, 439)), ('lineTo', (1063, 252)), ('lineTo', (1017, 252)), ('lineTo', (1017, 159)), ('moveTo', (1281, 667)), ('lineTo', (888, 667)), ('lineTo', (888, 33)), ('lineTo', (1281, 33)), ('lineTo', (1281, 667))]
#		textyoffset = 5
#		textxoffset = 30
#		DrawGlyph(None, None, fsiwhite, xoffset/mm - .5, 14.5 + logoyoffset, .05, (0,0,0,0), None, None, 1)
#		DrawGlyph(None, None, fsiyellow, xoffset/mm - .5, 14.5 + logoyoffset, .05, (0,.05,1,0), None, None, 1)
#		DrawGlyph(None, None, fsiblack, xoffset/mm - .5, 14.5 + logoyoffset, .05, (0,0,0,1), None, None, 1)
#		DrawText(pdffont['Regular'], 9, headlinefontcolour, xoffset + textxoffset + 15*mm, 22*mm + textyoffset + logoyoffset*mm, programname + ' ' + programversion + ' by Yanone')
#		DrawText(pdffont['Regular'], 9, headlinefontcolour, xoffset + textxoffset + 15*mm, 18.4*mm + textyoffset + logoyoffset*mm, 'www.yanone.de/typedesign/autopsy/')
#		DrawText(pdffont['Regular'], 9, headlinefontcolour, xoffset + textxoffset + 15*mm, 14.8*mm + textyoffset + logoyoffset*mm, 'Licensed for FSI FontShop International GmbH')

		# Sample glyph
		DrawGlyph(fonts[0], g, None, xoffset/mm - bbox.origin.x/mm*localratio, yoffset/mm - bbox.origin.y/mm*localratio + 18, localratio, (0,0,0,0), headlinefontcolour, 3, (6, 4))

		# Autopsy Report
		DrawText(pdffont['Bold'], 48, headlinefontcolour, xoffset, yoffset, "Autopsy Report")

		# Other infos
		if NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_PageOrientation_landscape"]:
			textmaxratio = 16000
		else:
			textmaxratio = 10000
		lines = []
		if len(fonts) > 1:
			patient = "Patients"
		else:
			patient = "Patient"
		lines.append((pdffont['Regular'], 18, headlinefontcolour, xoffset, 30, patient + ':'))
		yoffset -= 5
		for myfont in fonts:
			lines.append((pdffont['Bold'], 18, headlinefontcolour, xoffset, 20, str(myfont.familyName))) # + ' v' + str(myfont.version)))
		# get designers(s)
		designers = Ddict(dict)
		for f in fonts:
			if f.manufacturer:
				designers[f.manufacturer] = 1
			elif f.designer:
				designers[f.designer] = 1
			else:
				designers['Anonymous'] = 1
		if len(designers) > 1:
			doctor = 'Doctors'
		else:
			doctor = 'Doctor'
		fontinfos = {
		doctor : ", ".join(designers),
#		doctor : 'TypeDepartment of FontShop International',
		'Time' : time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()),
		}
		for fontinfo in fontinfos:
			lines.append((pdffont['Regular'], 18, headlinefontcolour, xoffset, 30, fontinfo + ':'))
			lines.append((pdffont['Bold'], 18, headlinefontcolour, xoffset, 20, fontinfos[fontinfo]))
		linesratio = 1.0/len(lines) * textmaxratio / pageheight/mm * 1.61
		if linesratio > 1:
			linesratio = 1
		for line in lines:
			yoffset -= line[4] * linesratio
			DrawText(line[0], line[1] * linesratio, line[2], line[3], yoffset, line[5])

		CGPDFContextEndPage(pdfContext)
		
		### MAIN PAGES ###
		
		
		for i, glyph in enumerate(glyphs):
			CGPDFContextBeginPage(pdfContext, None)
			output('-- ' + glyph + ' --')
	
			# if not tick:
			# 	raiseerror('Aborted by user.')
			# 	break
		
			#glyphindex = fonts[0].glyphs[glyph)
	
			# Draw scrapboard into page
			if drawboards:
				drawrect(scrapboard['left']*mm, scrapboard['bottom']*mm, scrapboard['right']*mm, scrapboard['top']*mm, '', scrapboardcolour, metricslinewidth, None, 0)
				drawrect(graphcoords['left']*mm, graphcoords['bottom']*mm, graphcoords['right']*mm, graphcoords['top']*mm, '', scrapboardcolour, metricslinewidth, None, 0)
			
			try:
				unicodes = 'u' + string.join(map(unicode2hex, fonts[0].glyphs[glyph.name].unicodes), "u u") + 'u'
			except:
				unicodes = ''
#			print '-', fonts[0][glyphindex], '-'
			DrawHeadlineIntoPage("/%s/ #%d# %s" % (glyph, i, unicodes))
	
			# Initial offset
	
			if not NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_PageOrientation_landscape"]:
				xoffsetinitial = scrapboard['left']
				yoffsetinitial = scrapboard['top'] - (ascender(fonts[0]) - descender(fonts[0])) / mm * ratio
			else:
				xoffsetinitial = scrapboard['left']
				yoffsetinitial = scrapboard['bottom']
	


			# Draw Metrics

			xoffset = xoffsetinitial
			yoffset = yoffsetinitial - descender(fonts[0])*ratio/mm


			for i_f, font in enumerate(fonts):

				if font.glyphs.has_key(glyph):
					g = font.glyphs[glyph]
				elif not font.glyphs.has_key(glyph) and fonts[i_f-1].glyphs.has_key(glyph):
					g = fonts[i_f-1].glyphs[glyph]
				
				DrawMetrics(font, g, xoffset, yoffset, ratio)
	
				# increase offset
				if not NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_PageOrientation_landscape"]:
					yoffset -= (ascender(font) - descender(font)) / mm * ratio
				else:
					if g.layers[0].width == 0:
						xoffset += g.layers[0].bounds.size.width / mm * ratio
					else:
						xoffset += g.layers[0].width / mm * ratio
					


			# Draw Glyphs

			xoffset = xoffsetinitial
			yoffset = yoffsetinitial - descender(fonts[0])*ratio/mm
			# Defaults
			myglyphfillcolour = glyphcolour
			myglyphstrokecolour = None
			myglyphstrokewidth = 0
			myglyphdashed = None
			
			for i_f, font in enumerate(fonts):

				# Glyph is in font
				if font.glyphs.has_key(glyph):
					g = font.glyphs[glyph]

					if Glyphs.defaults["com_yanone_Autopsy_outline_filled"]:
						myglyphfillcolour = glyphcolour
						myglyphstrokecolour = None
						myglyphstrokewidth = 0
						myglyphdashed = None
					else:
						myglyphfillcolour = xrayfillcolour
						myglyphstrokecolour = glyphcolour
						myglyphstrokewidth = 1.5
						myglyphdashed = None
				
				# Glyph is missing in font, draw replacement glyph
				elif not font.glyphs.has_key(glyph) and fonts[i_f-1].glyphs.has_key(glyph):
					g = fonts[i_f-1].glyphs[glyph]
					myglyphfillcolour = None
					myglyphstrokecolour = glyphcolour
					myglyphstrokewidth = 1
					myglyphdashed = (3, 3)

				DrawGlyph(font, g, None, xoffset, yoffset, ratio, myglyphfillcolour, myglyphstrokecolour, myglyphstrokewidth, myglyphdashed)


	
				# increase offset
				if not Glyphs.defaults["com_yanone_Autopsy_PageOrientation_landscape"]:
					yoffset -= (ascender(font) - descender(font)) / mm * ratio
				else:
					if g.layers[0].width == 0:
						xoffset += g.layers[0].bounds.size.width / mm * ratio
					else:
						xoffset += g.layers[0].width / mm * ratio

				#tick = fl.TickProgress((i) * len(fonts) + i_f + 1)
	
			# Aggregate graph objects into a list
	
			tableobjects = []
			for table in availablegraphs:
				if Glyphs.boolDefaults["com_yanone_Autopsy_graph_"+table]:
				#if eval('myDialog.graph_' + table):
					reports[glyph][table].glyphname = glyph
					reports[glyph][table].graphname = table
					reports[glyph][table].drawpointsvalues = Glyphs.boolDefaults["com_yanone_Autopsy_drawpointsvalues"]
					
					reports[glyph][table].scope = Glyphs.defaults["com_yanone_Autopsy_graph_"+table + '_scope']
					
					if graphcolour.has_key(table):
						reports[glyph][table].strokecolour = graphcolour[table]
					else:
						reports[glyph][table].strokecolour = graphcolour['__default__']
					tableobjects.append(reports[glyph][table])
		
			# Calculate bbox for graphs an draw them

			for t, table in enumerate(tableobjects):
	
				if not Glyphs.defaults["com_yanone_Autopsy_PageOrientation_landscape"]:
					tablewidth = ((graphcoords['right'] - graphcoords['left']) - (tableseparator * (len(tableobjects) - 1))) / len(tableobjects)
					tableheight = reports[glyph]['height'].sum/mm*ratio
					table.left = graphcoords['left'] + t * (tablewidth + tableseparator)
					table.right = table.left + tablewidth
					table.top = graphcoords['top']
					table.bottom = table.top - tableheight
				else:
					if reports[glyph]['width']:
						tablewidth = reports[glyph]['width'].sum/mm*ratio
					else:
						tablewidth = reports[glyph]['bboxwidth'].sum/mm*ratio
					tableheight = ((graphcoords['top'] - graphcoords['bottom']) - (tableseparator * (len(tableobjects) - 1))) / len(tableobjects)
					table.left = graphcoords['left']
					table.right = table.left + tablewidth
					table.top = graphcoords['top'] - t * (tableheight + tableseparator)
					table.bottom = table.top - tableheight
				
				table.draw()

			# PDF Bookmarks
#			pdf.bookmarkPage(glyph)
#			pdf.addOutlineEntry(None, glyph, 0, 0)

			# End page
			CGPDFContextEndPage(pdfContext)
	
	
		# close PDF
		NSGraphicsContext.restoreGraphicsState()
		CGPDFContextClose(pdfContext)
		
		output("time: " + str(time.time() - starttime) + "sec, ca." + str((time.time() - starttime) / len(glyphs)) + "sec per glyph")


	if errors:
		for error in errortexts:
			#print "__Message", error, programname
			dlg = message(error)
			
	# if not errors and fonts and myDialog.openPDF:
	if not errors and fonts:
		try:
			os.rename(tempFileName, filename)
		except:
			dlg = message("Problem copying final pdf")
		if Glyphs.defaults["com_yanone_Autopsy_openPDF"]:
			launchfile(filename)
	


def launchfile(path):
	if os.path.exists(path):
		if os.name == 'posix':
			os.system('open "%s"' % path)
		elif os.name == 'nt':
			os.startfile('"' + path + '"')

# def findFlsPath(*requestedPath):
# 	requestedPath = os.path.join(*requestedPath)
# 	try:    folders = [fl.path, fl.commonpath, fl.userpath, fl.usercommonpath]
# 	except: folders = [fl.path]
# 	for folder in folders:
# 		thePath = os.path.join(folder,requestedPath)
# 		if os.path.exists(thePath):
# 			return thePath
# 	return None


# Settings

def LoadSettings():
	global preferences

		# Default values, if plist does not yet exist
	defaultpreferences = Ddict(dict)

	# # User path
	defaultpdf = ''
	if os.path.exists(os.path.join(os.path.expanduser('~'), 'Desktop')):
		defaultpdf = os.path.join(os.path.expanduser('~'), 'Desktop', 'Autopsy.pdf')
	
	defaultpreferences = {
		'com_yanone_Autopsy_PageOrientation_landscape' : True,
		'com_yanone_Autopsy_PageSize_a4' : True,
		'com_yanone_Autopsy_outline_filled' : True,
		# Other
		'com_yanone_Autopsy_drawpointsvalues': True,
		'com_yanone_Autopsy_drawmetrics': True,
		'com_yanone_Autopsy_drawguidelines': True,
		'com_yanone_Autopsy_fontnamesunderglyph': False,
		'com_yanone_Autopsy_filename': defaultpdf,
		'com_yanone_Autopsy_openPDF': True,
		'com_yanone_Autopsy_checkforupdates': True,
		# Graphs
		'com_yanone_Autopsy_graph_width': True,
		'com_yanone_Autopsy_graph_width_scope_local': True,
		'com_yanone_Autopsy_graph_bboxwidth': False,
		'com_yanone_Autopsy_graph_bboxwidth_scope_local' : True,
		'com_yanone_Autopsy_graph_bboxheight': False,
		'com_yanone_Autopsy_graph_bboxheight_scope_local' : True,
		'com_yanone_Autopsy_graph_highestpoint': False,
		'com_yanone_Autopsy_graph_highestpoint_scope_local': False,
		'com_yanone_Autopsy_graph_lowestpoint': False,
		'com_yanone_Autopsy_graph_lowestpoint_scope_local': False,
		'com_yanone_Autopsy_graph_leftsidebearing': True,
		'com_yanone_Autopsy_graph_leftsidebearing_scope_local' : True,
		'com_yanone_Autopsy_graph_rightsidebearing': True,
		'com_yanone_Autopsy_graph_rightsidebearing_scope_local' : True,
	}
	
	NSUserDefaults.standardUserDefaults().registerDefaults_(defaultpreferences)
	
	
	# # Load Custom fonts
	# if preferences.has_key('appearance'):
	# 
	# 	# Set Custom fonts
	# 	if preferences['appearance'].has_key('customfontfolder') and preferences['appearance'].has_key('customfontRegularAFM') and preferences['appearance'].has_key('customfontRegularPFB') and preferences['appearance'].has_key('customfontBoldAFM') and preferences['appearance'].has_key('customfontBoldPFB'):
	# 		if preferences['appearance']['customfontRegularName'] == preferences['appearance']['customfontBoldName']:
	# 			RegisterPFBFont('CustomRegular', preferences['appearance']['customfontRegularName'], preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularAFM'], preferences['appearance']['customfontRegularPFB'])
	# 			pdffont['Regular'] = 'CustomRegular'
	# 			pdffont['Bold'] = 'CustomRegular'
	# 		else:
	# 			RegisterPFBFont('CustomRegular', preferences['appearance']['customfontRegularName'], preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularAFM'], preferences['appearance']['customfontRegularPFB'])
	# 			RegisterPFBFont('CustomBold', preferences['appearance']['customfontBoldName'], preferences['appearance']['customfontfolder'], preferences['appearance']['customfontBoldAFM'], preferences['appearance']['customfontBoldPFB'])
	# 			pdffont['Regular'] = 'CustomRegular'
	# 			pdffont['Bold'] = 'CustomBold'
	# 	elif preferences['appearance'].has_key('customfontfolder') and preferences['appearance'].has_key('customfontRegularTTF') and preferences['appearance'].has_key('customfontBoldTTF'):
	# 		if preferences['appearance']['customfontRegularTTF'] == preferences['appearance']['customfontBoldTTF']:
	# 			RegisterTTFont('CustomRegular', preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularTTF'])
	# 			pdffont['Regular'] = 'CustomRegular'
	# 			pdffont['Bold'] = 'CustomRegular'
	# 		else:
	# 			RegisterTTFont('CustomRegular', preferences['appearance']['customfontfolder'], preferences['appearance']['customfontRegularTTF'])
	# 			RegisterTTFont('CustomBold', preferences['appearance']['customfontfolder'], preferences['appearance']['customfontBoldTTF'])
	# 			pdffont['Regular'] = 'CustomRegular'
	# 			pdffont['Bold'] = 'CustomBold'
	# 
	# 	# Set custom colour	
	# 	if preferences['appearance'].has_key('colour'):
	# 		global pdfcolour
	# 		pdfcolour = preferences['appearance']['colour']
	
#	preferences['appearance']['colour'] = (0,0.05,1,0)

# def RegisterTTFont(internalname, folder, ttf):
# 	from reportlab.pdfbase import pdfmetrics
# 	from reportlab.pdfbase.ttfonts import TTFont
# 	pdfmetrics.registerFont(TTFont(internalname, os.path.join(folder, ttf)))
# 
# def RegisterPFBFont(internalname, fullname, folder, afm, pfb):
# 	from reportlab.pdfbase import pdfmetrics
# 	newfontface = pdfmetrics.EmbeddedType1Face(os.path.join(folder, afm), os.path.join(folder, pfb))
# 	pdfmetrics.registerTypeFace(newfontface)
# 	newfont = pdfmetrics.Font(internalname, fullname, 'WinAnsiEncoding')
# 	pdfmetrics.registerFont(newfont)




#####################
#
#  Dialogs
#

def Orientation_Radio_Callback(sender):
	print "__sender", sender
	Defaults = NSUserDefaults.standardUserDefaults()
	Defaults.setBool_forKey_(not sender.get(), 'com_yanone_Autopsy_PageOrientation_landscape')
def outline_filled_Radio_Callback(sender):
	print "__sender", sender
	Defaults = NSUserDefaults.standardUserDefaults()
	Defaults.setBool_forKey_(not sender.get(), 'com_yanone_Autopsy_outline_filled')
def PageSize_Radio_Callback(sender):
	print "__sender", sender
	Defaults = NSUserDefaults.standardUserDefaults()
	Defaults.setBool_forKey_(not sender.get(), 'com_yanone_Autopsy_PageSize_a4')

class _listMultiSelect:
	def __init__(self, mode, OptList=None):
		
		title = programname + ' ' + programversion
		self.mode = mode
		self.OptList = OptList
		
		Defaults = NSUserDefaults.standardUserDefaults()
		DefaultsController = NSUserDefaultsController.sharedUserDefaultsController()
		### Start auto-generated code ###
		# The main dialog window
		
		self.returnValue = NSCancelButton
		
		self.d = Window((621, 610))
		self.d.ok_button = Button((510,  567,  90,  22), "Autopsy", callback=self.on_ok)
		self.d.ok_button.bind("\r", [])
		self.d.cancel_button = Button((410,  567,  90,  22), "Cancel", callback=self.on_cancel)
		self.d.cancel_button.bind(chr(0x1B), [])
		self.d.center()
		self.d.title = title
		if mode == 'normal':
			self.d.Label3 = TextBox(( 15,  213,  191,  22),'Open Fonts')
			self.d.List_opt = List(( 15,  231,  224,  217), [])
			self.d.List_sel = List(( 311,  231,  224,  217), [])
			self.d.Label4 = TextBox(( 311,  213,  191,  22), 'Use these fonts')
			self.d.add_one = Button(( 247,  231,  55,  22), '>', callback=self.on_add_one)
			self.d.add_all = Button(( 247,  261,  55,  22), '>>', callback=self.on_add_all)
			self.d.rem_one = Button(( 247,  291,  55,  22), '<', callback=self.on_rem_one)
			self.d.rem_all = Button(( 247,  321,  55,  22), '<<', callback=self.on_rem_all)
#			self.d.Button(( 247,  391,  303,  423), 'addfonts', STYLE_BUTTON, 'R')
			self.d.move_dn = Button(( 543,  272,  55,  22), 'down')
			self.d.move_up = Button(( 543,  231,  55,  22), 'up')
		elif mode == 'MM':
			self.d.Label3 = TextBox(( 15,  15,  559,  231), 'Values for ' + str(OptList[0]) + ' Multiple Master instances')
			self.d.MMvalues = EditText(( 15,  31,  559,  22), "")
		
		self.d.Label5 = TextBox(( 15,  499,  287,  22), 'Path to PDF (will overwrite without asking)')
		self.d.filename = EditText(( 15,  516,  523,  22), '')
		self.d.filename.binding(DefaultsController, 'com_yanone_Autopsy_filename')
		self.d.browse_file = Button(( 543,  516,  55,  22), '...', callback=self.on_browse_file)
		self.d._label2 = TextBox(( 15,  454,  191,  22), 'Page size')
		self.d.pagesize_letter = RadioGroup(( 107,  454,  72,  40), ['A4', 'Letter'], callback=PageSize_Radio_Callback)
		self.d.pagesize_letter.set(not Defaults.boolForKey_('com_yanone_Autopsy_PageSize_a4'))
		# self.d.pagesize_a4 = CheckBox(( 15,  471,  72,  22), 'A4')
		# self.d.pagesize_a4.binding(DefaultsController, 'com_yanone_Autopsy_PageSize_a4')
		# Page Orientation
#		self.d. = TextBox(( 15,  15,  191,  31), 'Label1', STYLE_LABEL, 'Page Orientation')
#		self.d.CheckBox(( 15,  31,  100,  50), 'orientation_portrait', STYLE_CHECKBOX, 'Portrait')
#		self.d.CheckBox(( 107,  31,  200,  50), 'orientation_landscape', STYLE_CHECKBOX, 'Landscape')
		self.d.Label1 = TextBox(( 15,  21,  90,  22), 'Orientation')
		self.d.orientation_portrait = RadioGroup(( 107,  21,  90,  40), ['Landscape', 'Portrait'], callback=Orientation_Radio_Callback)
		self.d.orientation_portrait.set(not Defaults.boolForKey_('com_yanone_Autopsy_PageOrientation_landscape'))
		
		# self.d.orientation_portrait.binding(DefaultsController, 'com_yanone_Autopsy_PageOrientation_landscape', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		# self.d.orientation_landscape = CheckBox(( 190,  31,  90,  22), 'Landscape')
		# self.d.orientation_landscape.binding(DefaultsController, 'com_yanone_Autopsy_PageOrientation_landscape')
		# Outline mode
		self.d.Label1_ = TextBox(( 15,  71,  191,  22), 'Glyph outline')
		self.d.outline_filled = RadioGroup(( 107,  71,  180,  40), ['filled', 'X-RAY'], callback=outline_filled_Radio_Callback)
		self.d.outline_filled.set(not Defaults.boolForKey_('com_yanone_Autopsy_outline_filled'))
		# self.d.outline_xray = CheckBox(( 190,  79,  300,  98), 'X-RAY')
		# self.d.outline_xray.binding(DefaultsController, 'com_yanone_Autopsy_outline_filled', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		
		
		self.d.drawmetrics = CheckBox(( 15,  113,  230,  22), 'Draw metrics')
		self.d.drawmetrics.binding(DefaultsController, 'com_yanone_Autopsy_drawmetrics')
		self.d.drawguidelines = CheckBox(( 15,  137,  230,  22), 'Draw guidelines')
		self.d.drawguidelines.binding(DefaultsController, 'com_yanone_Autopsy_drawguidelines')
		self.d.drawpointsvalues = CheckBox(( 15,  161,  230,  22), 'Draw graph values')
		self.d.drawpointsvalues.binding(DefaultsController, 'com_yanone_Autopsy_drawpointsvalues')
		self.d.fontnamesunderglyph = CheckBox(( 15,  185,  230,  22), 'Fontnames under glyph')
		self.d.fontnamesunderglyph.binding(DefaultsController, 'com_yanone_Autopsy_fontnamesunderglyph')

		self.d.openPDF = CheckBox(( 15,  538,  206,  557), 'Open PDF in Reader')
		self.d.openPDF.binding(DefaultsController, 'com_yanone_Autopsy_openPDF')
#		self.d.checkforupdates = CheckBox(( 311,  538,  580,  557), 'Check online for updates (on start)')
		
		# if findFlsPath('Macros', 'Autopsy User Guide.pdf'):
		# #if os.path.exists(os.path.join(fl.path, 'Macros', 'Autopsy User Guide.pdf')):
		# 	self.d.Button(( 543,  15,  599,  47), 'user_guide', STYLE_BUTTON, '?')
		
		self.d.Label7 = TextBox(( 413,  13,  456,  22), 'Local')
		self.d.Label8 = TextBox(( 452,  13,  495,  22), 'Global')
		
		self.d.graph_width_scope_local = CheckBox(( 431,  31,  22,  22), '')
		self.d.graph_width_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_width_scope_local')
		self.d.graph_width_scope_global = CheckBox(( 455,  31,  22,  22), '')
		self.d.graph_width_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_width_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.graph_width = CheckBox(( 311,  31,  110,  22), 'Width')
		self.d.graph_width.binding(DefaultsController, "com_yanone_Autopsy_graph_width")
		self.d.graph_bboxwidth = CheckBox(( 311,  55,  110,  22), 'BBox Width')
		self.d.graph_bboxwidth.binding(DefaultsController, "com_yanone_Autopsy_graph_bboxwidth")
		self.d.graph_bboxwidth_scope_local = CheckBox(( 431,  55,  22,  22), '')
		self.d.graph_bboxwidth_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_bboxwidth_scope_local')
		self.d.graph_bboxwidth_scope_global = CheckBox(( 455,  55,  22,  22), '')
		self.d.graph_bboxwidth_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_bboxwidth_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.graph_bboxheight = CheckBox(( 311,  79,  110,  22), 'BBox Height')
		self.d.graph_bboxheight.binding(DefaultsController, 'com_yanone_Autopsy_graph_bboxheight')
		self.d.graph_bboxheight_scope_local = CheckBox(( 431,  79,  22,  22), '')
		self.d.graph_bboxheight_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_bboxheight_scope_local')
		self.d.graph_bboxheight_scope_global = CheckBox(( 455,  79,  22,  22), '')
		self.d.graph_bboxheight_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_bboxheight_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.Label9 = TextBox(( 308,  13,  90,  22), 'Graphs')
		self.d.graph_lowestpoint = CheckBox(( 311,  127,  110,  22), 'BBox Lowest')
		self.d.graph_lowestpoint.binding(DefaultsController, 'com_yanone_Autopsy_graph_lowestpoint')
		self.d.graph_highestpoint = CheckBox(( 311,  103,  110,  22), 'BBox Highest')
		self.d.graph_highestpoint.binding(DefaultsController, 'com_yanone_Autopsy_graph_highestpoint')
		self.d.graph_highestpoint_scope_local = CheckBox(( 431,  103,  22,  22), '')
		self.d.graph_highestpoint_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_highestpoint_scope_local')
		self.d.graph_highestpoint_scope_global = CheckBox(( 455,  103,  22,  22), '')
		self.d.graph_highestpoint_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_highestpoint_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.graph_lowestpoint_scope_local = CheckBox(( 431,  127,  22,  22), '')
		self.d.graph_lowestpoint_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_lowestpoint_scope_local')
		self.d.graph_lowestpoint_scope_global = CheckBox(( 455,  127,  22,  22), '')
		self.d.graph_lowestpoint_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_lowestpoint_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.graph_rightsidebearing = CheckBox(( 311,  175,  110,  22), 'R Sidebearing')
		self.d.graph_rightsidebearing.binding(DefaultsController, 'com_yanone_Autopsy_graph_rightsidebearing')
		self.d.graph_leftsidebearing = CheckBox(( 311,  151,  110,  22), 'L Sidebearing')
		self.d.graph_leftsidebearing.binding(DefaultsController, 'com_yanone_Autopsy_graph_leftsidebearing')
		self.d.graph_leftsidebearing_scope_local = CheckBox(( 431,  151,  22,  22), '')
		self.d.graph_leftsidebearing_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_leftsidebearing_scope_local')
		self.d.graph_leftsidebearing_scope_global = CheckBox(( 455,  151,  22,  22), '')
		self.d.graph_leftsidebearing_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_leftsidebearing_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.graph_rightsidebearing_scope_local = CheckBox(( 431,  175,  22,  22), '')
		self.d.graph_rightsidebearing_scope_local.binding(DefaultsController, 'com_yanone_Autopsy_graph_rightsidebearing_scope_local')
		self.d.graph_rightsidebearing_scope_global = CheckBox(( 455,  175,  22,  22), '')
		self.d.graph_rightsidebearing_scope_global.binding(DefaultsController, 'com_yanone_Autopsy_graph_rightsidebearing_scope_local', {NSValueTransformerNameBindingOption:"NSNegateBoolean"})
		self.d.Label10 = TextBox(( 15,  567,  209,  22), 'Autopsy 1.2 by Yanone.')

		if mode == 'MM': 
			self.customdata = Ddict(dict)
			self.MMvalues = ''
			self.MMfont = getFontByFullname(OptList[0])
			if self.MMfont.glyphs.has_key('.notdef'):
				if self.MMfont['.notdef'].customdata:
					self.customdata = readPlistFromString(self.MMfont['.notdef'].customdata)
					self.MMvalues = self.customdata['MMinstances']
		
		self.addfonts()

		# Check for previously loaded fonts and append to the option list
		try:
			if mode == 'normal' and Defaults['com_yanone_Autopsy_fontselection'] is not None:
				for i, sel in enumerate(NSUserDefaults.standardUserDefaults()['com_yanone_Autopsy_fontselection']):
					if sel in self.d.List_opt:
						self.d.List_sel.append(sel)
						self.d.List_opt.remove(sel)
				self.checkLists()
		except:
			pass
		
		
	def addfonts(self):
		self.d.List_opt.set(self.OptList)
		self.d.List_sel.set([])
		self.selection = []
		self.List_opt_index = 0
		self.List_sel_index = -1
		self.checkLists()
	
	### End auto-generated code ###
	
	def checkLists(self):
		if len(self.d.List_opt) > 0:
			self.d.add_one.enable(True)
			self.d.add_all.enable(True)
			if self.List_opt_index == -1:
				self.List_opt_index = len(self.List_opt) - 1
		else:
			self.d.add_one.enable(False)
			self.d.add_all.enable(False)
		if len(self.d.List_sel) > 0:
			self.d.rem_one.enable(True)
			self.d.rem_all.enable(True)
			if self.List_sel_index == -1:
				self.List_sel_index = len(self.d.List_sel) - 1
			self.d.move_up.enable(True)
			self.d.move_dn.enable(True)
		else:
			self.d.rem_one.enable(False)
			self.d.rem_all.enable(False)
			self.d.move_up.enable(False)
			self.d.move_dn.enable(False)

	def on_List_opt(self, code):
		self.d.GetValue('List_opt')
#		log.debug('_listMultiSelect.on_List_opt %d', self.List_opt_index)

	def on_List_opt_index(self, code):
		self.d.GetValue('List_opt')
#		log.debug('_listMultiSelect.List_opt_index %d', self.List_opt_index)

	def on_add_one(self, code):
		if self.d.List_opt:
			item = self.d.List_opt[self.List_opt_index]
			sel_Items = self.d.List_sel.get()
			sel_Items.append(item)
			self.d.List_sel.set(sel_Items)
			del self.d.List_opt[self.List_opt_index]
		self.checkLists()
	
	def on_add_all(self, code):
		if self.d.List_opt:
			sel_Items = self.d.List_sel.get()
			sel_Items += self.d.List_opt.get()
			self.d.List_sel.set(sel_Items)
			self.d.List_opt.set([])
		self.checkLists()

	def on_rem_one(self, code):
		if self.d.List_sel:
			item = self.d.List_sel[self.List_sel_index]
			sel_Items = self.d.List_opt.get()
			sel_Items.append(item)
			self.d.List_opt.set(sel_Items)
			del self.d.List_sel[self.List_sel_index]
		self.checkLists()

	def on_rem_all(self, code):
		if self.d.List_sel:
			sel_Items = self.d.List_opt.get()
			sel_Items += self.d.List_sel.get()
			self.d.List_opt.set(sel_Items)
			self.d.List_sel.set([])
			# self.List_opt += self.d.List_sel
			# self.d.List_sel.set([])
		self.checkLists()

	def on_move_up(self, code):
		items = self.d.List_sel.get()
		myItem = items.pop(self.List_sel_index)
		items.insert(self.List_sel_index - 1, myItem)
		self.d.List_sel.set(items)
	
	def on_move_dn(self, code):
		items = self.d.List_sel.get()
		myItem = items.pop(self.List_sel_index)
		items.insert(self.List_sel_index + 1, myItem)
		self.d.List_sel.set(items)
	
	def on_browse_file(self, code):
		Directory = NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_filename"]
		FileName = os.path.basename(Directory)
		file = putFile('', title='pdf', directory=Directory, fileName=FileName, fileTypes=['pdf'])
		if file:
			NSUserDefaults.standardUserDefaults()["com_yanone_Autopsy_filename"] = file
	
	def on_ok(self, code):
		self.returnValue = NSOKButton
		if self.mode == 'normal':
			#self.d.GetValue('List_sel')
			self.selection = self.d.List_sel

		elif self.mode == 'MM':
			#self.d.GetValue('MMvalues')
			myMMvalues = string.replace(self.MMvalues, ' ', '')
			self.selection = myMMvalues.split(",")

			# Save instances into customdata of VFB
			if self.MMvalues != self.customdata['MMinstances']:
				self.MMfont.modified = 1
			self.customdata['MMinstances'] = self.MMvalues
			if self.MMfont.glyphs.has_key('.notdef'):
				self.MMfont['.notdef'].customdata = writePlistToString(self.customdata)
				
		NSUserDefaults.standardUserDefaults()['com_yanone_Autopsy_fontselection'] = self.d.List_sel.get()
		NSApp().stopModal()
		self.cleanup()
	
	def on_cancel(self, code):
		NSApp().stopModal()
		self.returnValue = NSCancelButton
		self.cleanup()
	
	def on_user_guide(self, code):
		launchfile(findFlsPath('Macros', 'Autopsy User Guide.pdf'))

	def Run(self):
		self.d.show()
		NSApp().runModalForWindow_(self.d.getNSWindow())
		self.d.getNSWindow().orderOut_(self)
		return self.returnValue
	def cleanup(self):
		DefaultsController = NSUserDefaultsController.sharedUserDefaultsController()
		self.d.graph_bboxwidth.unbind(DefaultsController, "com_yanone_Autopsy_graph_bboxwidth")


def getFontByFullname(TheName):
	result = None
	for f in Glyphs.fonts:
		familyname = f.familyName
		if len(f.instances) > 0:
			familyname += " "+f.instances[0].name
		if familyname == TheName:
			result = f
	return result


# Output to console
def output(text):
	if verbose:
		print "> " + str(text) + " <"




'''

TODO

- error message if full_name is empty.

- custom presets for GUI

for better handling of missing glyphs and zero-width glyphs:
- add a class for single graph values, that contain info about width and height of drawing space,
  and whether or not a point should be drawn there.

'''


LoadSettings()
main()
