#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from TumblerTestTools.Utils import *
from TumblerTestTools.FakeThumbnails import *

from TumblerService.Tumbler import Tumbler

class TumblerCacheTests(unittest.TestCase):
	def setUp(self):
		''' run before test '''

	def test_01_delete_single_file(self):
		''' test if thumbnails are deleted together with file '''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		thumbs = createFakeThumbnail(uri)
		# check if all flavors exist
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')

		# call tumbler delete cache function
		tumbler = Tumbler()
		tumbler.Cache_delete( [uri] )

		delay = 0
		while(not areFilesDeleted(thumbs) and delay < 4000):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) was deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of thumbnail were deleted!')

	def test_02_delete_multiple_files(self):
		''' test if thumbnails are deleted together with deletiion of more than one file '''
		# create a thumbnails (every flavor will get one thumbnail)
		uris = ["file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg", "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg", "file:///home/" + user() + "/MyDocs/.image/DSC_003.jpeg"]
		thumbs = createFakeThumbnails(uris)
		# check if all flavors exist
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')

		# call tumbler delete cache function
		tumbler = Tumbler()
		tumbler.Cache_delete( uris )

		delay = 0
		while(not areFilesDeleted(thumbs) and delay < 4000):
			wait(200)
			delay += 200

		# check if thumbnails (all flavors) were deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of thumbnail were deleted!')

	def test_03_delete_non_existing_file(self):
		''' test if requesting for delete of non existing thumbnail does not crash the tumbler'''

		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		thumbs = getThumbnailFilepaths(uri)
		deleteFiles(thumbs)
		self.assertEqual(areFilesDeleted(thumbs), True, 'Thumbnail could not be deleted for test.')

		# call tumbler delete cache function
		tumbler = Tumbler()
		tumbler.Cache_delete( [uri] )

		wait(200.0)

		self.assertEqual(isTumblerRunning(), True, 'Tumbler crashed after request of move of non existing thumbnail.')

	def test_04_delete_file_when_tumbler_is_not_running(self):
		''' test if thumbnails are deleted together with file - when tumbler is not running yet '''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		thumbs = createFakeThumbnail(uri)
		# check if all flavors exist
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# kill Tumbler
		killTumblerProcess()
		self.assertEqual(isTumblerRunning(), False, 'Could not kill the Tumbler daemon.')

		# call tumbler delete cache function
		tumbler = Tumbler()
		tumbler.Cache_delete( [uri] )

		wait(800)

		# check if thumbnail (all flavors) was deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of thumbnail were deleted!')

	def test_05_delete_wrong_uri(self):
		''' test if requesting for delete of not properly formated URI does not end up with Tumbler crash '''
		startTumblerProcess();
		self.assertEqual(isTumblerRunning(), True, 'Tumbler could not be started!')

		# no schema, no path, empty string, only space, trash
		uri = ["/home/" + user() + "/MyDocs/.image/DSC_001.jpeg", "DSC_001.jpeg", "", " ", "#!@$:;<>?/.,"]
		thumbs = getThumbnailFilepaths(uri[0])
		deleteFiles(thumbs)
		self.assertEqual(areFilesDeleted(thumbs), True, 'Thumbnails could not be deleted for test.')

		# call tumbler delete cache function
		tumbler = Tumbler()
		tumbler.Cache_delete( uri )
		wait(200.0)

		self.assertEqual(isTumblerRunning(), True, 'Tumbler crashed after request of move of non existing thumbnail.')

	def test_06_move_single_file(self):
		''' test if thumbnails are moved together with file '''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		uri_dst = "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"
		thumbs = createFakeThumbnail(uri)
		thumbs_dst = getThumbnailFilepaths(uri_dst)
		createFiles(uri_dst)
		# check if all target files exist
		self.assertEqual(areFilesExist(uri_dst), True, 'not all target uris were created!')
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler move cache function
		tumbler = Tumbler()
		tumbler.Cache_move( [uri], [uri_dst] )

		delay = 0
		while((not areFilesExist(thumbs_dst)) and (delay < 4000)):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of old thumbnail were deleted after move operation!')
		# .. and if new thumbnails exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after move operation!')
		deleteFiles(uri_dst)

	def test_07_move_multiple_files(self):
		''' test if thumbnails are moved together with more than one file '''
		# create a thumbnails (every flavor will get one thumbnail)
		uris = ["file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg", "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"]
		uris_dst = ["file:///home/" + user() + "/MyDocs/.image2/DSC_003.jpeg", "file:///home/" + user() + "/MyDocs/.image2/DSC_004.jpeg"]
		thumbs = createFakeThumbnails(uris)
		thumbs_dst = getThumbnailFilepaths(uris_dst)
		createFiles(uris_dst)
		# check if all target files exist
		self.assertEqual(areFilesExist(uris_dst), True, 'not all target could be created!')
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler move cache function
		tumbler = Tumbler()
		tumbler.Cache_move( uris, uris_dst )

		delay = 0
		while((not areFilesExist(thumbs_dst)) and (delay < 4000)):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of old thumbnail were deleted after move operation!')
		# .. and if new thumbnails exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after move operation!')
		deleteFiles(uris_dst)

	# according to Phillip's comments this test case is INVALID - commenting out
	def _test_08_move_one_non_file_resource(self):
		''' test if thumbnails are moved together with file if file is not a local resource'''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "http://www.imagegallery.com/DSC_001.jpeg"
		uri_dst = "http://www.imagegallery.com/DSC_002.jpeg"
		thumbs = createFakeThumbnail(uri)
		thumbs_dst = getThumbnailFilepaths(uri_dst)
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler move cache function
		tumbler = Tumbler()
		tumbler.Cache_move( [uri], [uri_dst] )

		delay = 0
		while((not areFilesExist(thumbs_dst)) and (delay < 4000)):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of old thumbnail were deleted after move operation!')
		# .. and if new thumbnails exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after move operation!')
		deleteFiles(uri_dst)


	def test_09_move_single_file_when_tumbler_is_not_running(self):
		''' test if thumbnails are moved together with file - in situation when tumbler is not running on request time'''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		uri_dst = "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"
		thumbs = createFakeThumbnail(uri)
		thumbs_dst = getThumbnailFilepaths(uri_dst)
		createFiles(uri_dst)
		# check if all target files exist
		self.assertEqual(areFilesExist(uri_dst), True, 'not all target uris were created!')
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		killTumblerProcess()
		self.assertEqual(isTumblerRunning(), False, 'Could not kill the Tumbler daemon.')

		# call tumbler move cache function
		tumbler = Tumbler()
		tumbler.Cache_move( [uri], [uri_dst] )

		wait(800)

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(areFilesDeleted(thumbs), True, 'not all flavors of old thumbnail were deleted after move operation!')
		# .. and if new thumbnails exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after move operation!')
		deleteFiles(uri_dst)

	def test_10_move_multiple_files_bad_uris(self):
		''' test if Tumbler is working properly with bad uris in parameters '''
		# create a thumbnails (every flavor will get one thumbnail)
		uris = ["file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg", "foo", ""]
		uris_dst = ["bar", "file:///home/" + user() + "/MyDocs/.image2/DSC_004.jpeg", "234@#$@!$:;[}.<"]

		# call tumbler move cache function
		tumbler = Tumbler()
		tumbler.Cache_move( uris, uris_dst )

		delay = 0
		while(isTumblerRunning() and (delay < 1000)):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(isTumblerRunning(), True, 'Tumbler crashed after wrong request')

	def test_11_move_different_arrays_length(self):
		''' test if Tumbler is working properly with different length of arrays in parameters '''
		# create a thumbnails (every flavor will get one thumbnail)
		uris = ["file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg", "file:///home/" + user() + "/MyDocs/.image2/DSC_004.jpeg"]
		uris_dst = ["file:///home/user" + user() + "/MyDocs/.image/DSC_003.jpeg"]

		# call tumbler move cache function
		tumbler = Tumbler()
		try:
			tumbler.Cache_move( uris, uris_dst )
		except:
			''' do nothing '''

		delay = 0
		while(isTumblerRunning() and (delay < 1000)):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(isTumblerRunning(), True, 'Tumbler crashed after wrong request: different length of arrays')

	def test_12_move_multiple_files_some_bad(self):
		''' test if thumbnails are moved together with more than one file when some parameters are wrong '''
		# create a thumbnails (every flavor will get one thumbnail)
		one_src_uri  = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		two_src_uri  = "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"
		good_dst_uri = "file:///home/" + user() + "/MyDocs/.image2/DSC_003.jpeg"
		bad_dst_uri  = "file:///home/" + user() + "/MyDocs/.image2/non_existing_image.jpeg"
		uris = [one_src_uri, two_src_uri ]
		uris_dst = [good_dst_uri, bad_dst_uri]
		thumbs = createFakeThumbnails(uris)
		thumbs_dst = getThumbnailFilepaths(uris_dst)
		createFiles(good_dst_uri)
		# check if all target files exist
		self.assertEqual(areFilesExist(good_dst_uri), True, 'target image could not be created!')
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler move cache function
		tumbler = Tumbler()
		tumbler.Cache_move( uris, uris_dst )

		thumbs_should_exists = getThumbnailFilepaths([two_src_uri, good_dst_uri])
		thumbs_should_not_exists = getThumbnailFilepaths([one_src_uri, bad_dst_uri])

		delay = 0
		while((not areFilesExist(thumbs_should_exists)) and (delay < 4000)):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file was deleted also
		self.assertEqual(areFilesDeleted(thumbs_should_not_exists), True, 'not all flavors of old thumbnail were deleted after move operation!')
		# .. and if new thumbnails exist
		self.assertEqual(areFilesExist(thumbs_should_exists), True, 'not all flavors of new thumbnail were created after move operation!')
		deleteFiles(thumbs_should_exists)

	def test_13_copy_single_file(self):
		''' test if thumbnails are copied together with file '''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		uri_dst = "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"
		createFiles(uri_dst)
		thumbs = createFakeThumbnail(uri)
		thumbs_dst = getThumbnailFilepaths(uri_dst)
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler copy cache function
		tumbler = Tumbler()
		tumbler.Cache_copy( [uri], [uri_dst] )

		delay = 0
		while(not areFilesExist(thumbs_dst) and delay < 4000):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file is kept
		self.assertEqual(areFilesExist(thumbs), True, 'some old thumbnail was deleted during copy operation!')
		# .. and also if new thumbnail exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after copy operation!')
		deleteFiles(uri_dst)

	def test_14_copy_multiple_file(self):
		''' test if thumbnails are copied together with multiple files '''
		# create a thumbnails (every flavor will get one thumbnail)
		uris = ["file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg", "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"]
		uris_dst = ["file:///home/" + user() + "/MyDocs/.image/DSC_003.jpeg", "file:///home/" + user() + "/MyDocs/.image/DSC_004.jpeg"]
		createFiles(uris_dst)
		thumbs = createFakeThumbnails(uris)
		thumbs_dst = getThumbnailFilepaths(uris_dst)
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler copy cache function
		tumbler = Tumbler()
		tumbler.Cache_copy( uris, uris_dst )

		delay = 0
		while(not areFilesExist(thumbs_dst) and delay < 4000):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file is kept
		self.assertEqual(areFilesExist(thumbs), True, 'some old thumbnail was deleted during copy operation!')
		# .. and also if new thumbnail exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after copy operation!')
		deleteFiles(uris_dst)

	# according to Phillip's comments this test case is INVALID - commenting out
	def _test_15_copy_multiple_file_non_local_resources(self):
		''' test if thumbnails are copied together with multiple files which source or destination are not local resource '''
		# create a thumbnails (every flavor will get one thumbnail)
		uris = ["http://www.imagegallery.com/DSC_001.jpeg", "file:///home/user/MyDocs/.image/DSC_002.jpeg"]
		uris_dst = ["file:///home/" + user() + "/MyDocs/.image/DSC_003.jpeg", "http://www.imagegallery.com/DSC_004.jpeg"]
		createFiles(uris_dst[0])
		thumbs = createFakeThumbnails(uris)
		thumbs_dst = getThumbnailFilepaths(uris_dst)
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')

		# call tumbler copy cache function
		tumbler = Tumbler()
		tumbler.Cache_copy( uris, uris_dst )

		delay = 0
		while(not areFilesExist(thumbs_dst) and delay < 4000):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file is kept
		self.assertEqual(areFilesExist(thumbs), True, 'some old thumbnail was deleted during copy operation!')
		# .. and also if new thumbnail exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all thumbnails were created after copy operation!')
		deleteFiles(uris_dst)

	def test_16_copy_single_file_when_tumbler_is_not_running(self):
		''' test if thumbnails are copied together with file if tumbler is not running on request time '''
		# create a thumbnails (every flavor will get one thumbnail)
		uri = "file:///home/" + user() + "/MyDocs/.image/DSC_001.jpeg"
		uri_dst = "file:///home/" + user() + "/MyDocs/.image/DSC_002.jpeg"
		createFiles(uri_dst)
		thumbs = createFakeThumbnail(uri)
		thumbs_dst = getThumbnailFilepaths(uri_dst)
		# check if all flavors exist for src
		self.assertEqual(areFilesExist(thumbs), True, 'not all flavors of thumbnail were created!')
		# check if any flavor exist for dst (should NOT - we delete them before)
		deleteFiles(thumbs_dst)
		self.assertEqual(areFilesDeleted(thumbs_dst), True, 'some destination thumbnails exists!')
		killTumblerProcess()

		# call tumbler copy cache function
		tumbler = Tumbler()
		tumbler.Cache_copy( [uri], [uri_dst] )

		delay = 0
		while(not areFilesExist(thumbs_dst) and delay < 4000):
			wait(200)
			delay += 200

		# check if thumbnail (all flavors) for old file is kept
		self.assertEqual(areFilesExist(thumbs), True, 'some old thumbnail was deleted during copy operation!')
		# .. and also if new thumbnail exist
		self.assertEqual(areFilesExist(thumbs_dst), True, 'not all flavors of new thumbnail were created after copy operation!')
		deleteFiles(uri_dst)


if __name__ == "__main__":
	''' entry point for cache tests '''
	print "Tumbler Unit Tests Suite, Nokia (C) 2010\n"
	# run all tests
	unittest.main()
