# -*- coding: utf-8 -*-
""" This script converts the hold documentation (saved in markdown files) in a python file with a list of strings to translate it using gettext."""

def prepare_documentation_in_file(fileSource, fileDest):
	""" This takes documentation written in a markdown file and put all the contents in a python file, to create a internationalized documentation.
	 @fileSource str: A markdown(.md) file.
	 @fileDest str: A file where this will put the new strings"""

	f1 = open(fileSource, "r")
	f2 = open(fileDest, "w")
	lns = f1.readlines()
	f2.write("# -*- coding: utf-8 -*-\n")
	f2.write("documentation = [\n")
	for i in lns:
		if "\n" == i:
			newvar = "\"\","
		elif "\n" == i[-1]:
			newvar = "_(u\"\"\"%s\"\"\"),\n" % (i[:-1])
		else:
			newvar = "_(u\"\"\"%s\"\"\"),\n" % (i)
#		print i[-1:]
		f2.write(newvar)
	f1.close()
	f2.write("]")
	f2.close()


prepare_documentation_in_file("manual.md", "strings.py")