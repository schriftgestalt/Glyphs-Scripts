#MenuTitle: Delete Extra Layers

Layers = Glyphs.font.selectedLayers
for Layer in Layers:
	Glyph = Layer.parent
	NewLayers = {}
	for m in Glyphs.font.masters:
		NewLayers[m.id] = Glyph.layers[m.id]
	Glyph.setLayers_(NewLayers)
