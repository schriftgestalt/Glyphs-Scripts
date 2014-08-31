#MenuTitle: Make Unicase Font
# encoding: utf-8

Font = Glyphs.font
masterCount = len(Font.masters)
allGlyphs = list(Font.glyphs)
for upperGlyph in allGlyphs:
	if upperGlyph.category == "Letter" and upperGlyph.subCategory == "Uppercase":
		lowerName = upperGlyph.name.lower()
		print "Lower", lowerName
		lowerGlyph = Font.glyphs[lowerName]
		if not lowerGlyph:
			lowerGlyph = GSGlyph(lowerName)
			Font.glyphs.append(lowerGlyph)
		for master in Font.masters:
			layer = lowerGlyph.layers[master.id]
			layer.paths = []
			for k in layer.anchors.keys():
				del(layer.anchors[str(k)])
			layer.components = [GSComponent(upperGlyph.name)]
		lowerGlyph.leftKerningGroup = upperGlyph.leftKerningGroup
		lowerGlyph.rightKerningGroup = upperGlyph.rightKerningGroup