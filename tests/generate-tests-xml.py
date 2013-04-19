#!/usr/bin/python

import inspect
import os, sys, re
import unittest

from TumblerTestTools  import configuration as cfg

#import tumblerCacheUnitTests


def parseTestCases(module, moduleName, className, classObject, moduleFileName, testScript):
	ret = "   <suite name=\"" + moduleName + "\" domain=\"Application Framework\">\n"
	ret += "      <set name=\"" + className + "\" >\n"



	for testCase in dir(classObject):
		if(not testCase.startswith("test")):
			continue
		# decide if test is insignificant
		insignificant = "insignificant=\"true\""
		if(testCase.endswith("insignificant")):
			insignificant =  "insignificant=\"true\""
		obj = getattr(classObject, testCase)
		ret += "         <case name=\"" + className + "." + testCase + "\" " + insignificant + ">\n"
		ret += "             <description>" + obj.__doc__ + "</description>\n"

		script = os.path.join (cfg.DATADIR, "tumbler-tests", testScript)

		ret += "             <step>su - user -c \"" + script + " " + className + "." + testCase + "\"</step>\n"
		ret += "         </case>\n"

	ret += "         <environments>\n"
	ret += "            <scratchbox>true</scratchbox>\n"
	ret += "            <hardware>true</hardware>\n"
	ret += "         </environments>\n"
	ret += "      </set>\n"
	ret += "   </suite>\n"
	return ret

def getTestCases(testCases, testScript):
	ret = ""

	module = testCases.replace('.py','')
	module = re.sub(".*/", "", module)

	loc = __import__(module, globals(), locals(), [])
	# check every object in that module
	for name in dir(loc):
		obj = getattr(loc, name)
		# get only classes
		if(inspect.isclass(obj)):
			# and only those derived from unittest test case
			if(issubclass(obj, unittest.TestCase)):
				ret += parseTestCases(loc, module, name, obj, testCases, testScript)
	return ret



if __name__ == "__main__":
	if(len(sys.argv) < 4):
		print "Not enough parameters!"
		print "Use: generate-tests-xml.py TESTSCRIPT OUTPUTFILE INPUTFILE1 [INPUTFILE2 [INPUTFILE3 [...]]]"
		exit(1)

	testScript = sys.argv[1]
	outputFile = sys.argv[2]
	inputFiles = sys.argv[3:]
	print "Generating output \'" + outputFile + "\' file..."
	print "   (input files:", inputFiles, ")"



	content = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
	content +="<testdefinition version=\"1.0\">\n"
	for mod in inputFiles:
		content += getTestCases(mod, testScript)
	content += "</testdefinition>\n"

	fileHandle = open(outputFile, 'w')
	fileHandle.write(content)
	fileHandle.close()
