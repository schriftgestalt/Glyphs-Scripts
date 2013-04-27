#MenuTitle: Delete Images
''' Deletes background images from selected layers.'''

Font = Glyphs.font
Font.disableUpdateInterface()
layers = Font.selectedLayers
for l in layers:
	l.setBackgroundImage_(None)

Font.enableUpdateInterface()