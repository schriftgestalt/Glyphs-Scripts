#MenuTitle: Delete Hints

from GlyphsApp import CORNER, CAP

for Layer in Glyphs.font.selectedLayers:
	print Layer.parent.name
	if len(Layer.hints) > 0:
		hints = list(Layer.hints)
		for idx, hint in reversed(list(enumerate(hints))):
			if hint.type not in (CORNER, CAP):
				del(Layer.hints[idx])