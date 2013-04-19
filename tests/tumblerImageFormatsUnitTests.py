#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import unittest
from TumblerTestTools.Utils import *
from TumblerTestTools.ImagesHandling import *

from TumblerService.Tumbler import Tumbler


class TumblerImageFormatsTests(unittest.TestCase):

	def deleteAllData(self):
		''' delete all images created during all previous potential test cases '''
		try:
			deleteFiles(os.listdir(self.dataDir))
		except OSError:
			#print "No files to delete!"
			return

	def setUp(self):
		''' run BEFORE each test '''
		self.dataDir = homeDir() + "MyDocs/.images/tumbler-tests/"
		#print "Deleting all thumbnails..."
		deleteAllThumbnails()
		#print "Deleting all images..."
		self.deleteAllData();

	def tearDown(self):
		''' run AFTER each test '''
		# the same cleanup as before test
		self.setUp()

	def test_01_jpeg_format(self):
		''' check if JPEG images are properly thumbnailed '''
		flavor = "normal"
		data = [   [
		               addFileSchema(self.dataDir + "image_01.jpeg"),
		               addFileSchema(self.dataDir + "image_02.jpeg"),
		               addFileSchema(self.dataDir + "image_03.jpeg"),
		               addFileSchema(self.dataDir + "image_04.jpeg"),
		           ],
		           [
		               "image/jpeg",
		               "image/jpeg",
		               "image/jpeg",
		               "image/jpeg",
		           ],
		           [
		               (100, 100),
		               (450, 450),
		               (800, 480),
		               (15, 15),
		           ],
		       ]
		for i in range(len(data[0])):
			# creating images
			createImageExt(name=data[0][i], mime=data[1][i], width=data[2][i][0], height=data[2][i][1], strings=["test_01_jpeg_format"])

		# ask for thumbnails
		tumbler = Tumbler()
		tumbler.simple_Queue(data[0], data[1], flavor=flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(data[0], flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for JPEG images!')
		# check if files are 'readable' as a image and do not have zero size
		self.assertEqual(areFilesProperImages( thumbnails ), True, 'Not all thumbnails are proper image files!')

	def test_02_png_format(self):
		''' check if PNG images are properly thumbnailed '''
		flavor = "normal"
		data = [   [
		               addFileSchema(self.dataDir + "image_01.png"),
		               addFileSchema(self.dataDir + "image_02.png"),
		               addFileSchema(self.dataDir + "image_03.png"),
		               addFileSchema(self.dataDir + "image_04.png"),
		           ],
		           [
		               "image/png",
		               "image/png",
		               "image/png",
		               "image/png",
		           ],
		           [
		               (100, 100),
		               (450, 450),
		               (800, 480),
		               (15, 15),
		           ],
		       ]
		for i in range(len(data[0])):
			# creating images
			createImageExt(name=data[0][i], mime=data[1][i], width=data[2][i][0], height=data[2][i][1], strings=["test_02_png_format"])

		# ask for thumbnails
		tumbler = Tumbler()
		tumbler.simple_Queue(data[0], data[1], flavor=flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(data[0], flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for PNG images!')
		# check if files are 'readable' as a image and do not have zero size
		self.assertEqual(areFilesProperImages( thumbnails ), True, 'Not all thumbnails are proper image files!')

	def test_03_gif_format(self):
		''' check if GIF images are properly thumbnailed '''
		flavor = "normal"
		data = [   [
		               addFileSchema(self.dataDir + "image_01.gif"),
		               addFileSchema(self.dataDir + "image_02.gif"),
		               addFileSchema(self.dataDir + "image_03.gif"),
		               addFileSchema(self.dataDir + "image_04.gif"),
		           ],
		           [
		               "image/gif",
		               "image/gif",
		               "image/gif",
		               "image/gif",
		           ],
		           [
		               (100, 100),
		               (450, 450),
		               (800, 480),
		               (15, 15),
		           ],
		       ]
		for i in range(len(data[0])):
			# creating images
			createImageExt(name=data[0][i], mime=data[1][i], width=data[2][i][0], height=data[2][i][1], strings=["test_03_gif_format"])

		# ask for thumbnails
		tumbler = Tumbler()
		tumbler.simple_Queue(data[0], data[1], flavor=flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(data[0], flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for GIF images!')
		# check if files are 'readable' as a image and do not have zero size
		self.assertEqual(areFilesProperImages( thumbnails ), True, 'Not all thumbnails are proper image files!')

	def test_04_bmp_format(self):
		''' check if BMP images are properly thumbnailed '''
		flavor = "normal"
		data = [   [
		               addFileSchema(self.dataDir + "image_01.bmp"),
		               addFileSchema(self.dataDir + "image_02.bmp"),
		               addFileSchema(self.dataDir + "image_03.bmp"),
		               addFileSchema(self.dataDir + "image_04.bmp"),
		           ],
		           [
		               "image/gif",
		               "image/gif",
		               "image/gif",
		               "image/gif",
		           ],
		           [
		               (100, 100),
		               (450, 450),
		               (800, 480),
		               (15, 15),
		           ],
		       ]
		for i in range(len(data[0])):
			# creating images
			createImageExt(name=data[0][i], mime=data[1][i], width=data[2][i][0], height=data[2][i][1], strings=["test_04_bmp_format"])

		# ask for thumbnails
		tumbler = Tumbler()
		tumbler.simple_Queue(data[0], data[1], flavor=flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(data[0], flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for BMP images!')
		# check if files are 'readable' as a image and do not have zero size
		self.assertEqual(areFilesProperImages( thumbnails ), True, 'Not all thumbnails are proper image files!')

	def test_05_tiff_format(self):
		''' check if TIFF images are properly thumbnailed '''
		flavor = "normal"
		data = [   [
		               addFileSchema(self.dataDir + "image_01.tiff"),
		               addFileSchema(self.dataDir + "image_02.tiff"),
		               addFileSchema(self.dataDir + "image_03.tiff"),
		               addFileSchema(self.dataDir + "image_04.tiff"),
		           ],
		           [
		               "image/tiff",
		               "image/tiff",
		               "image/tiff",
		               "image/tiff",
		           ],
		           [
		               (100, 100),
		               (450, 450),
		               (800, 480),
		               (15, 15),
		           ],
		       ]
		for i in range(len(data[0])):
			# creating images
			createImageExt(name=data[0][i], mime=data[1][i], width=data[2][i][0], height=data[2][i][1], strings=["test_05_tiff_format"])

		# ask for thumbnails
		tumbler = Tumbler()
		tumbler.simple_Queue(data[0], data[1], flavor=flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(data[0], flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for TIFF images!')
		# check if files are 'readable' as a image and do not have zero size
		self.assertEqual(areFilesProperImages( thumbnails ), True, 'Not all thumbnails are proper image files!')

if __name__ == "__main__":
	''' entry point for cache tests '''
	print "Tumbler Unit Tests Suite, Nokia (C) 2010\n"
	# run all tests
	unittest.main()
