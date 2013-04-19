#!/usr/bin/python
# -*- coding: utf-8 -*-

from Utils import *

def getThumbnailsList(uri):
	''' build all filenames for thumbnails of that uri '''
	filename = getThumbnailName(uri)
	thumbnails = []
	# for every flavor create a thumbnail
	for flavor in getThumbnailFlavorPaths():
		thumbnails.append(flavor + filename)	
	return thumbnails

def createFakeThumbnail(uri):
	''' create a list of fake thumbnails '''
	files = getThumbnailsList(uri)
	# create every file
	for tmp in files:
		createFile(tmp)
	# returns all thumbnails created
	return files

def createFakeThumbnails(uris):
	files = []
	for uri in uris:
		files.extend(createFakeThumbnail(uri))
	return files
