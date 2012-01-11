#MenuTitle: import SVGs to Glyphs
# encoding: utf-8
"""
Import SVG.py

Created by Georg Seifert on 2010-11-28.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""
from objectsGS import *
from vanilla.dialogs import getFile
from xml.dom import minidom
from os.path import basename, splitext

Bounds = None
def stringToFloatList(String):
	points = String.replace(",", " ").strip(" ").split(" ")
	newPoints = []
	for value in points:
		try:
			value = float(value)
			newPoints.append(value)
		except:
			pass
	return newPoints
	
def drawSVGNode(pen, node, Transform):
	global Bounds
	if node.localName:
		if node.localName == "rect":
			X = float(node.getAttribute('x'))
			Y = Bounds[3] - float(node.getAttribute('y')) 
			W = float(node.getAttribute('width'))
			H = float(node.getAttribute('height'))
			pen.moveTo( Transform.transformPoint_((X, Y)) )
			pen.lineTo( Transform.transformPoint_((X + W, Y)))
			pen.lineTo( Transform.transformPoint_((X + W, Y - H)))
			pen.lineTo( Transform.transformPoint_((X, Y - H)))
			pen.closePath()
		if node.localName == "circle":
			CX = float(node.getAttribute('cx'))
			CY = Bounds[3] - float(node.getAttribute('cy'))
			R = float(node.getAttribute('r'))
			pen.moveTo((CX, CY - R))
			pen.curveTo( (CX + (R * 0.5523), CY - R), (CX + R, CY - (R * 0.5523)), (CX + R , CY) )
			pen.curveTo( (CX + R, CY + (R * 0.5523)), (CX + (R * 0.5523), CY + R), (CX, CY + R) )
			pen.curveTo( (CX - (R * 0.5523), CY + R), (CX - R, CY + (R * 0.5523)), (CX - R , CY) )
			pen.curveTo( (CX - R, CY - (R * 0.5523)), (CX - (R * 0.5523), CY - R),  (CX, CY - R) )
			pen.closePath()
			
		if node.localName == "path":
			D = node.getAttribute('d')
			parts = []
			start = -1
			length = -1
			for i in range(len(D)):
				if D[i] in ("C", "c", "L", "l", "M", "m", "s", "z", "H", "h", "V", "v"):
					if start >= 0 and length > 0:
						part = D[start:start+length]
						part = part.replace(" ", ",")
						part = part.replace("-", ",-")
						part = part.replace(",,", ",")
						parts.append(part)
					start = i
					length = 0
				length += 1
			if start >= 0 and length > 0:
				part = D[start:start+length]
				part = part.replace("-", ",-")
				parts.append(part)
			lastPoint = None
			for part in parts:
				if part[0] == "M":
					point = points = stringToFloatList(part[1:])
					assert(len(point) == 2)
					point[1] = Bounds[3] - point[1]
					pen.moveTo(Transform.transformPoint_(point))
					lastPoint = point
				elif part[0] == "m":
					point = points = stringToFloatList(part[1:])
					assert(len(point) == 2)
					point[1] = - point[1]
					point[0] += lastPoint[0]
					point[1] += lastPoint[1]
					pen.moveTo(Transform.transformPoint_(point))
					lastPoint = point
			
				elif part[0] == "C":
					points = stringToFloatList(part[1:])
					assert(len(points) == 6)
					points = [float(Value) for Value in points]
					for i in range(0, len(points), 6):
						P1 = points[i:i+2]
						P2 = points[i+2:i+4]
						P3 = points[i+4:i+6]
						P1[1] = Bounds[3] - P1[1]
						P2[1] = Bounds[3] - P2[1]
						P3[1] = Bounds[3] - P3[1]
						pen.curveTo(Transform.transformPoint_(P1), Transform.transformPoint_(P2), Transform.transformPoint_(P3))
						lastPoint = P3
				elif part[0] == "c":
					points = part[1:].strip(",").split(",")
					points = [float(Value) for Value in points]
					for i in range(0, len(points), 6):
						P1 = points[i:i+2]
						P2 = points[i+2:i+4]
						P3 = points[i+4:i+6]
						P1[0] += lastPoint[0]
						P1[1] = -P1[1]
						P1[1] += lastPoint[1]
				
						P2[0] += lastPoint[0]
						P2[1] = -P2[1]
						P2[1] += lastPoint[1]
				
						P3[0] += lastPoint[0]
						P3[1] = -P3[1]
						P3[1] += lastPoint[1]
						pen.curveTo(Transform.transformPoint_(P1), Transform.transformPoint_(P2), Transform.transformPoint_(P3))
						lastPoint = P3
				elif part[0] == "S":
					points = part[1:].strip(",").split(",")
					points = [float(Value) for Value in points]
					if (pen.contour[-1][1] == 'curve'):
						P1 = list(pen.contour[-2][0])
						P1[0] = lastPoint[0] - (P1[0] - lastPoint[0])
						P1[1] = lastPoint[1] - (P1[1] - lastPoint[1])
					else:
						P1 = list(lastPoint)
					P2 = points[0:2]
					P3 = points[2:4]
					P2[1] = Bounds[3] - P2[1]
					P3[1] = Bounds[3] - P3[1]
					pen.curveTo(Transform.transformPoint_(P1), Transform.transformPoint_(P2), Transform.transformPoint_(P3))
					lastPoint = P3
				elif part[0] == "s":
					points = part[1:].strip(",").split(",")
					points = [float(Value) for Value in points]
					if (pen.contour[-1][1] == 'curve'):
						P1 = list(pen.contour[-2][0])
						P1[0] = lastPoint[0] - (P1[0] - lastPoint[0])
						P1[1] = lastPoint[1] - (P1[1] - lastPoint[1])
					else:
						P1 = list(lastPoint)
					P2 = points[0:2]
					P3 = points[2:4]
					
					P2[0] += lastPoint[0]
					P2[1] = -P2[1]
					P2[1] += lastPoint[1]
					
					P3[0] += lastPoint[0]
					P3[1] = -P3[1]
					P3[1] += lastPoint[1]
					pen.curveTo(Transform.transformPoint_(P1), Transform.transformPoint_(P2), Transform.transformPoint_(P3))
					lastPoint = P3
				elif part[0] == "L":
					points = stringToFloatList(part[1:])
					for i in range(0, len(points), 2):
						points[i+1] = Bounds[3] - points[i+1]
						pen.lineTo(points[i:i+2])
						lastPoint = points[i:i+2]
				elif part[0] == "l":
					points = part[1:].strip(",").split(",")
					points = [float(Value) for Value in points]
					for i in range(0, len(points), 2):
						points[i] += lastPoint[0]
						points[i+1] = -points[i+1]
						points[i+1] += lastPoint[1]
						pen.lineTo(Transform.transformPoint_(points[i:i+2]))
						lastPoint = points[i:i+2]
				elif part[0] == "H":
					point = float(part[1:].strip(","))
					points = []
					points.append(point)
					points.append(lastPoint[1])
					pen.lineTo(Transform.transformPoint_(points))
					lastPoint = points
				elif part[0] == "h":
					point = float(part[1:].strip(","))
					points = []
					points.append(point + lastPoint[0])
					points.append(lastPoint[1])
					pen.lineTo(Transform.transformPoint_(points))
					lastPoint = points
				elif part[0] == "V":
					point = float(part[1:].strip(","))
					points = []
					points.append(lastPoint[0])
					points.append(Bounds[3] - point)
					pen.lineTo(Transform.transformPoint_(points))
					lastPoint = points
				
				elif part[0] == "v":
					point = float(part[1:].strip(","))
					points = []
					points.append(lastPoint[0])
					points.append(-point + lastPoint[1])
					pen.lineTo(Transform.transformPoint_(points))
					lastPoint = points
				
				elif part[0] == "z":
					pen.closePath()
			if parts[-1] != "z":
				pen.endPath()
		if node.localName == "polygon":
			points = node.getAttribute('points').strip(" ")
			points = points.split(" ")
			point = points[0].split(",")
			point = [float(Value) for Value in point]
			point[1] = Bounds[3] - point[1]
			pen.moveTo(point)
			for i in range(1, len(points), 1):
				point = stringToFloatList(points[i])
				if len(point) == 2:
					point[1] = Bounds[3] - point[1]
					pen.lineTo(Transform.transformPoint_(point))
			pen.closePath()
		if node.localName == "g":
			TransformString = node.getAttribute('transform')
			Transform = NSAffineTransform.alloc().init()
			if TransformString:
				TransformStrings = TransformString.split(" ")
				TransformStrings.reverse()
				for TransformStringElement in TransformStrings:
					if TransformStringElement.startswith("matrix"):
						Values = stringToFloatList(TransformStringElement[7:-1])
						Transform.setTransformStruct_(Values)
					elif TransformStringElement.startswith("translate"):
						Values = stringToFloatList(TransformStringElement[10:-1])
						if len(Values) == 2:
							Values[1] = Bounds[3] - Values[1]
							Transform.translateXBy_yBy_(Values[0], Values[1])
						else:
							Transform.translateXBy_yBy_(Values[0], Values[0])
					
					elif TransformStringElement.startswith("scale"):
						Values = stringToFloatList(TransformStringElement[6:-1])
						if len(Values) == 2:
							Transform.scaleXBy_yBy_(Values[0], Values[1])
						else:
							Transform.scaleBy_(Values[0])
					# else if ([TransformStringElement hasPrefix:@"rotate"]) {
					# 
					# }
					# else if ([TransformStringElement hasPrefix:@"skewX"]) {
					# 
					# }
					# else if ([TransformStringElement hasPrefix:@"skewY"]) {
					# 
					# }
			for subNode in node.childNodes:
				drawSVGNode(pen, subNode, Transform)
	
def main():
	global Bounds
	paths = getFile(title="Please select .svg files", allowsMultipleSelection=True, fileTypes=["svg"])
	
	if paths is None:
		return
	for path in  paths:
		name = basename(path)
		name = splitext(name)[0]
		f = CurrentFont()
		g = f[name]
		if g is None:
			g = f.newGlyph(name)
		pen = g.getPen()
		dom = minidom.parse(path)
		SVG = dom.getElementsByTagName("svg")[0]
		Bounds = SVG.getAttribute('viewBox').split(" ")
		if (len(Bounds) == 4):
			Bounds = [float(Value) for Value in Bounds]
		else:
			Width = SVG.getAttribute("width")
			Height = SVG.getAttribute("height")
			if Width and Height:
				Bounds = [0, 0, float(Width), float(Height) ]
		for node in dom.getElementsByTagName("svg")[0].childNodes:
			drawSVGNode(pen, node, NSAffineTransform.alloc().init())

if __name__ == '__main__':
	main()
