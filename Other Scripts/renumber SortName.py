'''
Put the lines from the data file in a xml file called "Numbering.xml" next to script. Then run the script and put the output of the script into the original glpyhData file.

Change the names suffix to something related to the glyphs. e.g. the script tag or "num", "symb". 
'''

nameSuffix = "ar"

f = open("Numbering.xml", "r")
i = 0

for line in f:
	if len(line) > 40:
		if line.find("sortName=") > 0:
			begin = line.find("sortName=\"")
			end = line.find("\" ", begin)
			line = line[:begin] + line[end+2:]
		pos = line.find("name=\"")
		pos = line.find("\" ", pos)
		print line[:pos+2] + "sortName=\"%s%.3d\" " % (nameSuffix, i) + line[pos+2:],
		i+=1

	else:
		print line,