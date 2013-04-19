#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
#
# You need to have PIL installed to make it working:
# apt-get install python-imaging python-imaging-doc python-imaging-dbg
from PIL import Image, ImageDraw
from Utils import *

MIME_INFO = [
	["image/jpeg",      "JPEG", "jpeg"],
	["image/bmp",       "BMP" , "bmp"],
	["image/gif",       "GIF" , "gif"],
	["application/pdf", "PDF",  "pdf"],
	["image/png",       "PNG",  "png"],
	["image/tiff",      "TIFF", "tif"]
]

borderWidth = 2
leftMargin = 5

def getExtensionForMime(mime):
	for tmp in MIME_INFO:
		if(tmp[0] == mime):
			return tmp[2]
	return ""

def getPILTypeFromMime(mime):
	for tmp in MIME_INFO:
		if(tmp[0] == mime):
			return tmp[1]
	return "JPEG"

def getImageSize(name):
	name = name.replace("file://", "")
	im = Image.open(name)
	return im.size


def createImage(name, mime, width, height, strings=[]):
	global borderWidth
	global leftMargin

	try:
		im = Image.new('RGB', (width, height), (0, 0, 0, 0)) # Create a blank image
		draw = ImageDraw.Draw(im)
		draw.rectangle((borderWidth, borderWidth, width-(2*borderWidth), height-(2*borderWidth)), fill="white", outline="silver")
		topMargin = leftMargin
		for txt in strings:
			draw.text((leftMargin, topMargin), txt, fill="black")
			topMargin += 12
		# draw two black boxes in the bottom part of the image
		leftSpace = height - topMargin
		draw.rectangle((0, topMargin, width/2, topMargin+leftSpace/2), fill="black", outline="black")
		draw.rectangle((width/2, topMargin+leftSpace/2, width, height), fill="black", outline="black")
		# define finall name for the file, without the scheme
		if(name.startswith("file://")):
			name = name.replace("file://", "")
		# save the image
		im.save(name, getPILTypeFromMime(mime))
	except IOError:
		print "Cannot create na image ", name


def createImageExt(name="image", mime="image/jpeg", width=100, height=100, strings=[]):
	#print "Got parameters:  -----------------"
	#print "   Param name = ", name
	#print "   Param mime = ", mime
	#print "   Param path = ", path
	#print "  Param width = ", width
	#print " Param height = ", height
	#print "Param strings = ", strings

	md5 = getThumbnailName(name)
	path = uriToAbsoluteContainerDir(name)
	name = name.replace("file://", "")
	if(os.path.exists(name)):
		return md5

	if(not os.path.isdir(path)):
		os.makedirs(path)

	#print "Used parameters:  -----------------"
	#print "   Param name = ", name
	#print "   Param mime = ", mime
	#print "   Param path = ", path
	#print "  Param width = ", width
	#print " Param height = ", height
	#print "Param strings = ", strings

	strings.append("Filename   : " + name)
	strings.append("MIME Type  : " + mime)
	strings.append("Thumbnail  : " + md5)
	strings.append("Size       : " + str(width) + "x" + str(height) + " [px]")
	createImage(name, mime, width, height, strings)
	return md5
