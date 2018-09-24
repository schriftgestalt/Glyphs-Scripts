#MenuTitle: Separate Letters and Marks
# -*- coding: utf-8 -*-
__doc__="""
Separate Letters and Marks.
"""

tab = Font.currentTab
print ord(tab.text[0])
letters = ""
marks = ""
for c in tab.text:
	glyph = Font.glyphForCharacter_(ord(c))
	if glyph.category == "Mark":
		marks += c
	else:
		letters += c
tab.text = letters + marks