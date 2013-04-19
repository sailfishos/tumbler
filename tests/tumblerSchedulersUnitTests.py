#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import unittest
from TumblerTestTools.Utils import *
from TumblerTestTools.ImagesHandling import *

from TumblerService.Tumbler import Tumbler


class TumblerSchedulersTests(unittest.TestCase):
	def setUp(self):
		''' run before test '''

	def test_01_check_default(self):
		''' check if thumbnails are generated for standard scheduler '''

		uri = "file:///home/" + user() + "/MyDocs/.images/image.jpeg"
		mime = "image/jpeg"
		deleteFiles(uri)
		thumb_name = createImageExt(name=uri, width=200, height=200, strings=["test_01_check_default"])
		all_thumbs = getThumbnailFilepaths(uri)

		# cleanup before test
		deleteFiles(all_thumbs)

		for flavor in getFlavorsList():
			''' '''
			# this thumbnail should be created
			thumb_path = getThumbnailFlavorPath(uri, flavor)[0]
			deleteFiles(all_thumbs)

			tumbler = Tumbler()
			tumbler.simple_Queue([uri], [mime], flavor, "default")

			self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for scheduler default was not created!')
			self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal')
			self.assertEqual(tumbler.errorSignalCount(), 0, 'Wrong number of Error signal')
			self.assertEqual(tumbler.readyItemsCount(), 1, 'Wrong number of Ready items')
			deleteFiles(thumb_path)

		# cleanup
		deleteFiles(all_thumbs)
		deleteFiles(uri)


	def test_02_check_foreground(self):
		''' check if thumbnails are generated for foreground scheduler '''
		uri = "file:///home/" + user() + "/MyDocs/.images/image.jpeg"
		mime = "image/jpeg"
		deleteFiles(uri)
		thumb_name = createImageExt(name=uri, width=200, height=200, strings=["test_02_check_foreground"])

		all_thumbs = getThumbnailFilepaths(uri)

		# cleanup before test
		deleteFiles(all_thumbs)

		for flavor in getFlavorsList():
			''' '''
			# this thumbnail should be created
			thumb_path = getThumbnailFlavorPath(uri, flavor)[0]
			deleteFiles(all_thumbs)

			tumbler = Tumbler()
			tumbler.simple_Queue([uri], [mime], flavor, "foreground")

			self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for scheduler foreground was not created!')
			self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal')
			self.assertEqual(tumbler.errorSignalCount(), 0, 'Wrong number of Error signal')
			self.assertEqual(tumbler.readyItemsCount(), 1, 'Wrong number of Ready items')
			deleteFiles(thumb_path)

		# cleanup
		deleteFiles(all_thumbs)
		deleteFiles(uri)

	def test_03_check_background(self):
		''' check if thumbnails are generated for background scheduler '''
		uri = "file:///home/" + user() + "/MyDocs/.images/image.jpeg"
		mime = "image/jpeg"
		deleteFiles(uri)
		thumb_name = createImageExt(name=uri, width=200, height=200, strings=["test_03_check_background"])

		all_thumbs = getThumbnailFilepaths(uri)

		# cleanup before test
		deleteFiles(all_thumbs)

		for flavor in getFlavorsList():
			''' '''
			# this thumbnail should be created
			thumb_path = getThumbnailFlavorPath(uri, flavor)[0]
			deleteFiles(all_thumbs)

			tumbler = Tumbler()
			tumbler.simple_Queue([uri], [mime], flavor, "background")

			self.assertEqual(areFilesExist(thumb_path), True, 'Thumbnail for scheduler background was not created!')
			self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal: ' + str(tumbler.readySignalCount()))
			self.assertEqual(tumbler.errorSignalCount(), 0, 'Wrong number of Error signal: ' + str(tumbler.errorSignalCount()))
			self.assertEqual(tumbler.readyItemsCount(), 1, 'Wrong number of Ready items: ' + str(tumbler.readyItemsCount()) + ' Items: ' + str(tumbler.signal_ready))
			deleteFiles(thumb_path)

		# cleanup
		deleteFiles(all_thumbs)
		deleteFiles(uri)

	def test_04_check_background_signal_count(self):
		''' check if Tumbler sends only one Ready signal for background scheduler '''
		# first create lots of images to pass to Tumbler
		flavor = "normal"
		uris = []
		thumbs = []
		mimes = []
		for i in range(100):
			uri = "file:///home/" + user() + "/MyDocs/.images/image_" + str(i) + ".jpeg"
			uris.append(uri)
			mimes.append("image/jpeg")
			deleteFiles(uri)
			createImageExt(name=uri, width=110, height=110, strings=["test_04_check_background_signal_count("+str(i)+")"])
			thumbs.append(getThumbnailFlavorPath(uri, flavor)[0])

		# make sure that thumbnails do not exist
		deleteFiles(thumbs)

		# make a request with backround scheduler
		tumbler = Tumbler()
		tumbler.setLogLevel(2)
		tumbler.simple_Queue(uris, mimes, flavor, "background")

		self.assertEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal: ' + str(tumbler.readySignalCount()))
		self.assertEqual(tumbler.readyItemsCount(), 100, 'Wrong number of Ready items: ' + str(tumbler.readyItemsCount()))

		# clean up
		deleteFiles(uris)
		deleteFiles(thumbs)

	def test_05_check_foreground_signal_count(self):
		''' check if Tumbler sends more than one one Ready signal for foreground scheduler '''
		# first create lots of images to pass to Tumbler
		flavor = "normal"
		uris = []
		thumbs = []
		mimes = []
		for i in range(100):
			uri = "file:///home/" + user() + "/MyDocs/.images/image_" + str(i) + ".jpeg"
			uris.append(uri)
			mimes.append("image/jpeg")
			deleteFiles(uri)
			createImageExt(name=uri, width=110, height=110, strings=["test_04_check_background_signal_count("+str(i)+")"])
			thumbs.append(getThumbnailFlavorPath(uri, flavor)[0])

		# make sure that thumbnails do not exist
		deleteFiles(thumbs)

		# make a request with backround scheduler
		tumbler = Tumbler()
		tumbler.setLogLevel(2)
		tumbler.simple_Queue(uris, mimes, flavor, "foreground")

		self.assertNotEqual(tumbler.readySignalCount(), 1, 'Wrong number of Ready signal: ' + str(tumbler.readySignalCount()))
		self.assertEqual(tumbler.readyItemsCount(), 100, 'Wrong number of Ready items: ' + str(tumbler.readyItemsCount()))

		# clean up
		deleteFiles(uris)
		deleteFiles(thumbs)

if __name__ == "__main__":
	''' entry point for cache tests '''
	print "Tumbler Unit Tests Suite, Nokia (C) 2010\n"
	# run all tests
	unittest.main()
