#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from TumblerTestTools.Utils import *
from TumblerTestTools.ImagesHandling import *

from TumblerService.Tumbler import Tumbler


class TumblerFlavorsTests(unittest.TestCase):
	def setUp(self):
		''' run before test '''

	def test_01_check_flavors(self):
		''' check if thumbnails are generated for proper flavor '''
		uri = "file:///home/" + user() + "/MyDocs/.images/image.jpeg"
		mime = "image/jpeg"
		thumb_name = createImageExt(name=uri, width=800, height=480, strings=["test_01_check_flavors"])

		all_thumbs = getThumbnailFilepaths(uri)

		for flavor in getFlavorsList():
			''' '''
			# this thumbnail should be created
			thumb_path = getThumbnailFlavorPath(uri, flavor)[0]
			deleteFiles(all_thumbs)

			tumbler = Tumbler()
			tumbler.simple_Queue([uri], [mime], flavor)

			self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for proper flavor was not created! ' + thumb_path + ' should be created.')
			self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal')
			self.assertEqual(tumbler.errorSignalCount(), 0, 'Wrong number of Error signal')
			self.assertEqual(tumbler.readyItemsCount(), 1, 'Wrong number of Ready items')
		# cleanup
		deleteFiles(all_thumbs)
		deleteFiles(uri)

	def test_02_check_flavors_multiple_files(self):
		''' check if thumbnails are generated for proper flavor when requesting multiple files '''
		uri = [ "file:///home/" + user() + "/MyDocs/.images/image_01.jpeg",
		        "file:///home/" + user() + "/MyDocs/.images/image_02.png",
		        "file:///home/" + user() + "/MyDocs/.images/image_03.gif" ]
		mime = ["image/jpeg", "image/png", "image/gif"]

		thumb_name = [ createImageExt(name=uri[0], mime=mime[0], width=800, height=480, strings=["test_01_check_flavors_multiple"]),
		               createImageExt(name=uri[1], mime=mime[1], width=800, height=480, strings=["test_01_check_flavors_multiple"]),
		               createImageExt(name=uri[2], mime=mime[2], width=800, height=480, strings=["test_01_check_flavors_multiple"]) ]
		all_thumbs = getThumbnailFilepaths(uri)

		for flavor in getFlavorsList():
			''' '''
			# this thumbnails should be created
			thumb_path = getThumbnailFlavorPath(uri, flavor)
			deleteFiles(all_thumbs)

			tumbler = Tumbler()
			tumbler.simple_Queue(uri, mime, flavor)

			self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for proper flavor was not created!')
			self.assertEqual(tumbler.readyItemsCount(), 3, 'Wrong number of Ready items')
			self.assertEqual(tumbler.errorItemsCount(), 0, 'Wrong number of Error items')
		#cleanup
		deleteFiles(all_thumbs)
		deleteFiles(uri)

	def test_03_check_flavors_sizes(self):
		''' check if thumbnails have proper size for particular flavors '''
		uri = "file:///home/" + user() + "/MyDocs/.images/image.jpeg"
		mime = "image/jpeg"
		thumb_name = createImageExt(name=uri, width=300, height=560, strings=["test_03_check_flavors_sizes"])
		all_thumbs = getThumbnailFilepaths(uri)

		for flavor in getFlavorsList():
			''' '''
			# this thumbnail should be created
			thumb_path = getThumbnailFlavorPath(uri, flavor)[0]
			deleteFiles(all_thumbs)

			tumbler = Tumbler()
			tumbler.simple_Queue([uri], [mime], flavor)

			target_size = calculateSizeSrcFlavor((300, 560), flavor)
			self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for proper flavor was not created! ' + thumb_path + ' should be created.')
			self.assertEqual(getImageSize(thumb_path), target_size, 'Image does not have a proper size for flavor ' + flavor + ': is ' + str(getImageSize(thumb_path)) + ' and should be ' + str(target_size))
			self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal')
			self.assertEqual(tumbler.errorSignalCount(), 0, 'Wrong number of Error signal')
			self.assertEqual(tumbler.readyItemsCount(), 1, 'Wrong number of Ready items')
			deleteFiles(thumb_path)

		# cleanup
		deleteFiles(all_thumbs)
		deleteFiles(uri)

	def test_04_check_flavors_resizing(self):
		''' check if thumbnails have proper sizes for every input size of the image '''
		uri = "file:///home/" + user() + "/MyDocs/.images/image.png"
		# use png due to some problems with really small (like 1x1) jpeg images in python-imaging
		mime = "image/png"
		all_thumbs = getThumbnailFilepaths(uri)
		sizes = [ (1,1),  (2,2), (1,1000), (1000,1), (20,50), (1000, 1000), (10,10), (3000, 3000), (4000, 3000), (5,1000), (1000,5)]

		for flavor in getFlavorsList():
			for size in sizes:
				deleteFiles(uri)
				thumb_name = createImageExt(name=uri, mime=mime, width=size[0], height=size[1], strings=["test_04_check_flavors_resizing"])

				# this thumbnail should be created
				thumb_path = getThumbnailFlavorPath(uri, flavor)[0]
				deleteFiles(all_thumbs)
				deleteFiles(thumb_path)

				tumbler = Tumbler()
				tumbler.simple_Queue([uri], [mime], flavor)

				target_size = calculateSizeSrcFlavor(size, flavor)
				errorMsg = "Orig:" + str(size) + " Min:" + str(getFlavorMinSize(flavor)) + " Dst:" + str(getFlavorSize(flavor)) + " -> should_be" + str(target_size) + " == is" + str(getImageSize(thumb_path))
				self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for proper flavor was not created! ' + thumb_path + ' should be created.')
				self.assertEqual(getImageSize(thumb_path), target_size, 'Image does not have a proper size for flavor ' + flavor + ':' + errorMsg)
				self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal')
				self.assertEqual(tumbler.errorSignalCount(), 0, 'Wrong number of Error signal')
				self.assertEqual(tumbler.readyItemsCount(), 1, 'Wrong number of Ready items')
				# cleanup
				deleteFiles(all_thumbs)
				deleteFiles(uri)
				deleteFiles(thumb_path)



if __name__ == "__main__":
	''' entry point for cache tests '''
	print "Tumbler Unit Tests Suite, Nokia (C) 2010\n"
	# run all tests
	unittest.main()
