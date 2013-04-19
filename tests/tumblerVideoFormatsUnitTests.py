#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from TumblerTestTools.Utils import *
from TumblerTestTools.ImagesHandling import *

from TumblerService.Tumbler import Tumbler


class TumblerVideoFormatsTests(unittest.TestCase):
	def getAllVideosWithFormat(self,format="avi"):
		''' return all videos in data dir '''
		self.dataDir = "/usr/share/tumbler-tests/data/"
		ret = []
		for video in os.listdir(self.dataDir):
			if(video.endswith(format)):
				ret.append("file://" + self.dataDir + video)
		return ret

	def setUp(self):
		''' run BEFORE each test '''
		#print "Deleting all thumbnails..."
		deleteAllThumbnails()

	def tearDown(self):
		''' run AFTER each test '''
		# the same cleanup as before test
		self.setUp()
		# plus make sure that original flavors.conf was recreated
		useStandardFlavorsConf()

	def _test_01_3gp_format(self):
		''' check if 3GP videos are properly thumbnailed '''
		videos = self.getAllVideosWithFormat("3gp")
		flavor = "normal"
		mime = []
		for tmp in videos:
			mime.append("video/3gpp")

		tumbler = Tumbler()
		tumbler.setQuitOnError()
		tumbler.simple_Queue(videos, mime, flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(videos, flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for 3GP videos!')
		# cleanup
		deleteAllThumbnails()

	def _test_02_avi_format_insignificant(self):
		''' check if AVI videos are properly thumbnailed '''
		videos = self.getAllVideosWithFormat("avi")
		flavor = "normal"
		mime = []
		for tmp in videos:
			mime.append("video/x-msvideo")

		tumbler = Tumbler()
		tumbler.setQuitOnError()
		tumbler.simple_Queue(videos, mime, flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(videos, flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for AVI videos!')
		# cleanup
		deleteAllThumbnails()

	def _test_03_mp4_format_insignificant(self):
		''' check if MP4 videos are properly thumbnailed '''
		videos = self.getAllVideosWithFormat("mp4")
		flavor = "normal"
		mime = []
		for tmp in videos:
			mime.append("video/mp4")

		tumbler = Tumbler()
		tumbler.setQuitOnError()
		tumbler.simple_Queue(videos, mime, flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(videos, flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for MP4 videos!')
		# cleanup
		deleteAllThumbnails()

	def _test_04_mpeg_format_insignificant(self):
		''' check if MPEG videos are properly thumbnailed '''
		videos = self.getAllVideosWithFormat("mpeg")
		flavor = "normal"
		mime = []
		for tmp in videos:
			mime.append("video/mpeg")

		tumbler = Tumbler()
		tumbler.setQuitOnError()
		tumbler.simple_Queue(videos, mime, flavor)

		# get list of thumbnails which should be created
		thumbnails = getThumbnailFlavorPath(videos, flavor)
		# check if those thumbnails exists
		self.assertEqual(areFilesExist( thumbnails ), True, 'Not all thumbnails were created for MPEG videos!')
		# cleanup
		deleteAllThumbnails()

	def _test_05_video_resizing(self):
		''' check if videos are resized properly '''
		#useTestFlavorsConf() - had to remove that and test on standard flavors only
		deleteAllThumbnails()

		tumbler = Tumbler()
		tumbler.setQuitOnError()
		video         = [ "file:///usr/share/tumbler-tests/data/size_352x288.mp4" ]
		mime          = [ "video/mp4" ]
		flavors       = getFlavorsList()
		original_size = 352, 288

		for flavor in flavors:
			tumbler.simple_Queue(video, mime, flavor)
			# get list of thumbnails which should be created
			thumbnails = getThumbnailFlavorPath(video[0], flavor)
			#print "Should generated thumbnail:", thumbnails
			# check if those thumbnails exists
			self.assertEqual(areFilesExist( thumbnails ), True, 'Thumbnail has not been created!')
			# check if files are 'readable' as a image and do not have zero size
			self.assertEqual(areFilesProperImages( thumbnails ), True, 'Not all thumbnails are proper image files!')
			# get size of the image
			size = getImageSize(thumbnails[0])
			# calculate proper size for a thumbnail
			targetSize = calculateSizeSrcFlavor(original_size, flavor)
			#print "Orig:(", original_size, ") Min:(", getFlavorMinSize(flavor), ") Dst:(", getFlavorSize(flavor), ") -> (", targetSize, ")"
			# check if thumbnail has proper size
			self.assertEqual(size, targetSize)

		#useStandardFlavorsConf()

if __name__ == "__main__":
	''' entry point for cache tests '''
	print "Tumbler Unit Tests Suite, Nokia (C) 2010\n"
	# run all tests
	unittest.main()
