#MenuTitle: Delete Hints

Layers = Glyphs.currentDocument.selectedLayers()
for Layer in Layers:
	print Layer.parent.name
	if len(Layer.hints) > 0:
		Layer.hints = None