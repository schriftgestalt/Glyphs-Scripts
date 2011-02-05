#MenuTitle: import SVG
# encoding: utf-8
"""
Import SVG.py

Created by Georg Seifert on 2010-11-28.
Copyright (c) 2010 schriftgestaltung.de. All rights reserved.
"""
from objectsGS import *
from GlyphsApp import GetFile
from xml.dom import minidom

Bounds = None
def stringToFloatList(String):
	
	points = String.replace(",", " ").strip(" ").split(" ")
	newPoints = []
	print "- points", points
	for value in points:
		try:
			value = float(value)
			newPoints.append(value)
		except:
			pass
	print "f points", newPoints
	return newPoints
	
def drawSVGNode(pen, node):
	global Bounds
	if node.localName:
		if node.localName == "rect":
			X = float(node.getAttribute('x'))
			Y = Bounds[3] - float(node.getAttribute('y')) 
			W = float(node.getAttribute('width'))
			H = float(node.getAttribute('height'))
			pen.moveTo((X, Y))
			pen.lineTo((X + W, Y))
			pen.lineTo((X + W, Y - H))
			pen.lineTo((X, Y - H))
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
			# print "Path"
			D = node.getAttribute('d')
			parts = []
			start = -1
			length = -1
			for i in range(len(D)):
				if D[i] in ("C", "c", "L", "l", "M", "s", "z"):
					if start >= 0 and length > 0:
						part = D[start:start+length]
						part = part.replace("-", ",-")
						parts.append(part)
					start = i
					length = 0
				length += 1
			if start >= 0 and length > 0:
				part = D[start:start+length]
				part = part.replace("-", ",-")
				parts.append(part)
			#print "parts", parts
			lastPoint = None
			for part in parts:
				# print "part", part
				if part[0] == "M":
					# print "__M"
					#if len(pen.contour) > 0:
					#	pen.
						
					# point = part[1:].strip(",").split(",")
					# newPoint = []
					# print "point", point
					# for value in point:
					# 	try:
					# 		value = float(value)
					# 		newPoint.append(value)
					# 	except:
					# 		pass
					point = points = stringToFloatList(part[1:])
					print "point", point
					assert(len(point) == 2)
					point[1] = Bounds[3] - point[1]
					pen.moveTo(point)
					lastPoint = point
				elif part[0] == "C":
					print "__C", part
					# points = part[1:].replace(",", " ").strip(" ").split(" ")
					# newPoints = []
					# print "- points c", points
					# for value in points:
					# 	try:
					# 		value = float(value)
					# 		newPoints.append(value)
					# 	except:
					# 		pass
					points = stringToFloatList(part[1:])
					print "+ points c", points
					assert(len(points) == 6)
					
					#points = [float(Value) for Value in points]
					P1 = points[0:2]
					P2 = points[2:4]
					P3 = points[4:6]
					P1[1] = Bounds[3] - P1[1]
					P2[1] = Bounds[3] - P2[1]
					P3[1] = Bounds[3] - P3[1]
					pen.curveTo(P1, P2, P3)
					lastPoint = P3
				elif part[0] == "c":
					# print "__c"
					points = part[1:].strip(",").split(",")
					points = [float(Value) for Value in points]
					P1 = points[0:2]
					P2 = points[2:4]
					P3 = points[4:6]
					P1[0] += lastPoint[0]
					P1[1] = -P1[1]
					P1[1] += lastPoint[1]
					
					P2[0] += lastPoint[0]
					P2[1] = -P2[1]
					P2[1] += lastPoint[1]
					
					P3[0] += lastPoint[0]
					P3[1] = -P3[1]
					P3[1] += lastPoint[1]
					pen.curveTo(P1, P2, P3)
					lastPoint = P3
				elif part[0] == "S":
					# print "__S"
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
					#P1[1] = Bounds[3] - P1[1]
					P2[1] = Bounds[3] - P2[1]
					P3[1] = Bounds[3] - P3[1]
					pen.curveTo(P1, P2, P3)
					lastPoint = P3
				elif part[0] == "s":
					# print "__s", pen.contour[-1][1]
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
					#P1[0] += lastPoint[0]
					#P1[1] = -P1[1]
					#P1[1] += lastPoint[1]
					
					P2[0] += lastPoint[0]
					P2[1] = -P2[1]
					P2[1] += lastPoint[1]
					
					P3[0] += lastPoint[0]
					P3[1] = -P3[1]
					P3[1] += lastPoint[1]
					pen.curveTo(P1, P2, P3)
					lastPoint = P3
				elif part[0] == "L":
					# print "__l", part[1:].strip(",")
					#points = part[1:].strip(",").split(",")
					# print "1 L points", points
					points = stringToFloatList(part[1:])
					# print "2 L points", points
					for i in range(0, len(points), 2):
						#point[1] = Bounds[3] - point[1]
						points[i+1] = Bounds[3] - points[i+1]
						pen.lineTo(points[i:i+2])
						# print "l lastPoint", lastPoint, " result ", points[i:i+2]
						lastPoint = points[i:i+2]
				elif part[0] == "l":
					# print "__l", part[1:].strip(",")
					points = part[1:].strip(",").split(",")
					# print "1 L points", points
					points = [float(Value) for Value in points]
					# print "2 L points", points
					for i in range(0, len(points), 2):
						#point[1] = Bounds[3] - point[1]
						points[i] += lastPoint[0]
						points[i+1] = -points[i+1]
						points[i+1] += lastPoint[1]
						pen.lineTo(points[i:i+2])
						# print "l lastPoint", lastPoint, " result ", points[i:i+2]
						lastPoint = points[i:i+2]
				elif part[0] == "z":
					pen.closePath()
			if parts[-1] != "z":
				pen.endPath()
		if node.localName == "polygon":
			# print "Poly"
			points = node.getAttribute('points').strip(" ")
			# print "1 points", points
			points = points.split(" ")
			# print "2 points", points
			point = points[0].split(",")
			point = [float(Value) for Value in point]
			point[1] = Bounds[3] - point[1]
			pen.moveTo(point)
			print "1 points", points
			for i in range(1, len(points), 1):
				#point = points[i].split(",")
				point = stringToFloatList(points[i])
				if len(point) == 2:
					#point = [float(Value) for Value in point]
					point[1] = Bounds[3] - point[1]
					pen.lineTo(point)
			pen.closePath()
		if node.localName == "g":
			for subNode in node.childNodes:
				drawSVGNode(pen, subNode)
	
def main():
	global Bounds
	
	g = CurrentGlyph()
	print g
	pen = g.getPen()
	
	path = GetFile("Please select a .svg", ["svg"], False, True)
	# print path
	if path:
		dom = minidom.parse(path)
		SVG = dom.getElementsByTagName("svg")[0]
		Bounds = SVG.getAttribute('viewBox').split(" ")
		if (len(Bounds) == 4):
			print Bounds
			Bounds = [float(Value) for Value in Bounds]
		else:
			Width = SVG.getAttribute("width")
			Height = SVG.getAttribute("height")
			if Width and Height:
				Bounds = [0, 0, float(Width), float(Height) ]
		for node in dom.getElementsByTagName("svg")[0].childNodes:
			drawSVGNode(pen, node)

if __name__ == '__main__':
	main()
