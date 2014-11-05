#MenuTitle: Remove Layer specific Metrics Keys


def FilterLayerKey(Key):
	if Key and Key.startswith("==") and Key.find("+") == -1 and Key.find("-") == -1 and Key.find("*") == -1 and Key.find("/") == -1:
		Key = Key[2:]
		return Key
	return None

def FilterGlyphKey(Key):
	if Key and Key.startswith("=") and Key.find("+") == -1 and Key.find("-") == -1 and Key.find("*") == -1 and Key.find("/") == -1:
		Key = Key[1:]
		return Key
	return None


def remove():
	for glyph in Glyphs.font.glyphs:
		for layer in glyph.layers:
			Key = FilterLayerKey(layer.leftMetricsKey())
			if Key is not None:
				layer.setLeftMetricsKey_(Key)
			Key = FilterLayerKey(layer.rightMetricsKey())
			if Key is not None:
				layer.setRightMetricsKey_(Key)
		Key = FilterGlyphKey(glyph.leftMetricsKey)
		if Key is not None:
			glyph.setLeftMetricsKey_(Key)
		Key = FilterGlyphKey(glyph.rightMetricsKey)
		if Key is not None:
			glyph.setRightMetricsKey_(Key)
		
remove()