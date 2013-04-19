#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import unittest
from TumblerTestTools.Utils import *
from TumblerTestTools.FakeThumbnails import *

# import test sets:
from tumblerCacheUnitTests import TumblerCacheTests
from tumblerFlavorsUnitTests import TumblerFlavorsTests
from tumblerSchedulersUnitTests import TumblerSchedulersTests
from tumblerImageFormatsUnitTests import TumblerImageFormatsTests
from tumblerVideoFormatsUnitTests import TumblerVideoFormatsTests


def test_unit_test():
	#some tests of utils etc. connected with testing infrastructure:
	print "    md5(' ') : ", md5()
	print "        User : ", user()
	print "        Home : ", homeDir()
	print " Current Dir : ", currentDir()
	print " Add Cur Dir : ", addCurrentPath("test-file.txt")
	print "Add Home Dir : ", addHomePath("test-file.txt")
	print "  Add Schema : ", addFileSchema("test-file.txt")
	print " URI to file : ", uriToFilepath("file:///home/user/test-file.txt")
	print "  URI to Dir : ", uriToAbsoluteContainerDir("file:///home/user/test-file.txt")
	print "  URI to Dir : ", uriToAbsoluteContainerDir("file:///home/user/")
	print "     Flavors : ", getThumbnailFlavorPaths()
	print "  Thumbnails : ", getThumbnailsList("file:///home/user/MyDocs/.image/DSC_001.jpeg")

	createFile(currentDir() + "test.file")
	deleteFile(currentDir() + "test.file")
	deleteFile(currentDir() + "tmp")

	thumbs = createFakeThumbnail("file:///home/user/MyDocs/.image/DSC_001.jpeg")
	print "   Thumbnail : ", thumbs
	thumbs = createFakeThumbnails( ["file:///home/user/MyDocs/.image/DSC_001.jpeg", "file:///home/user/MyDocs/.image/DSC_002.jpeg"])
	print "  Thumbnails : ", thumbs

# get all suites and run tests
if __name__ == "__main__":
	''' entry point for tests '''
	#test_unit_test()
	# run tests
	unittest.main()
