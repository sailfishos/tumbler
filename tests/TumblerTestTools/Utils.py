#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import os
import time
from subprocess import Popen, PIPE
import ConfigParser
from PIL import Image


def md5(string=" "):
	''' Calculates MD5 hash for a given string '''
	_md5 = hashlib.md5()
	_md5.update(string)
	return _md5.hexdigest()

def isRunningAsRoot():
	if("root" ==  os.environ['USER']):
		return True
	return False

def user():
	''' Returns current user name '''
	return os.environ['USER']

def currentDir():
	''' Returns current directory '''
	return os.getcwd() + "/"

def homeDir():
	''' Returns current users home path '''
	return os.environ['HOME'] + "/"

def addHomePath(filepath):
	''' if given filepath is not absolute, adds home path to it'''
	if(not filepath.startswith("/")):
		filepath = homeDir() + filepath
	return filepath

def addCurrentPath(filepath):
	''' if given given filepath is not absolute, adds current path to it'''
	if(not filepath.startswith("/")):
		filepath = currentDir() + filepath
	return filepath

def addFileSchema(filepath):
	''' Adds file:// at the begining of string if it does not exists '''
	filepath = addHomePath(filepath)
	if(not filepath.startswith("file://")):
		filepath = "file://" + filepath
	return filepath

def uriToFilepath(uri):
	''' remove schema from the uri - returns filepath '''
	if(uri.startswith("file://")):
		uri = uri.replace("file://", "")
	return uri

def uriToAbsoluteContainerDir(uri):
	''' gives path to directory where the file is placed '''
	uri = uriToFilepath(uri);
	uri = os.path.dirname(uri)
	if(not uri.endswith("/")):
		uri = uri + "/"
	return uri

def fixPermissions(directory):
	os.system("chmod a+x " + directory)
	os.system("chmod a+w " + directory)

def createFile(filepath):
	''' create a particular file - file will be empty '''
	filepath = uriToFilepath(filepath)
	directory = uriToAbsoluteContainerDir(filepath)

	if(not os.path.isdir(directory)):
		os.makedirs(directory)
		fixPermissions(directory)

	# "touch" file if needed
	if((not os.path.isfile(filepath)) and (os.path.isdir(directory))):
		f = open(filepath, "w")
		f.close();

def createFiles(files):
	# check if input is an single string
	if(type(files) == type("string")):
		files = [files]
	for f in files:
		createFile(f)

def areFilesExist(files):
	if(type(files) == type("string")):
		files = [files]
	for f in files:
		f = uriToFilepath(f)
		if(not os.path.exists(f)):
			#print "->Missing File: ", f
			return False
	return True

def areFilesDeleted(files):
	if(type(files) == type("string")):
		files = [ files ]
	for f in files:
		f = uriToFilepath(f)
		if(os.path.exists(f)):
			#print "->File exists: ", f
			return False
	return True

def deleteFile(filepath):
	filepath = uriToFilepath(filepath)
	if(os.path.isdir(filepath)):
		os.rmdir(filepath)
	elif(os.path.isfile(filepath)):
		os.remove(filepath)

def deleteFiles(filepaths):
	if(type(filepaths) == type("string")):
		filepaths = [ filepaths ]
	for filepath in filepaths:
		deleteFile(filepath)

def getFlavorsList():
	config = ConfigParser.RawConfigParser()
	config.read('/etc/xdg/thumbnails/flavors.conf')
	return config.sections()

def getFlavorSize(flavor):
	config = ConfigParser.RawConfigParser()
	config.read('/etc/xdg/thumbnails/flavors.conf')
	for current in config.sections():
		if(current == flavor):
			return config.getint(flavor, "Width"), config.getint(flavor, "Height")
	return -1, -1

def getFlavorMinSize(flavor):
	config = ConfigParser.RawConfigParser()
	config.read('/etc/xdg/thumbnails/flavors.conf')
	x = 0
	y = 0
	for current in config.sections():
		if(current == flavor):
			try:
				x = config.getint(flavor, "MinimumWidth")
			except:
				x = 0
			try:
				y = config.getint(flavor, "MinimumHeight")
			except:
				y = 0
			break
	return x, y

def calculateSizeSrcFlavor((src_w, src_h), flavor="normal"):
	# if wrong flavor is given return error
	if(flavor not in getFlavorsList()):
		return -1, -1
	# else get target and minimum sizes
	dstSize = getFlavorSize(flavor)
	minSize = getFlavorMinSize(flavor)
	# check if src is smaller than destination size
	if(src_w < dstSize[0] and src_h < dstSize[1]):
		return src_w, src_h
	#if(src_w < dstSize[0] and src_h >= dstSize[1]):
	#	return src_w, dstSize[1]
	#if(src_h < dstSize[1] and src_w >= dstSize[0]):
	#	return dstSize[0], src_h
	# now lets make calculation...
	# proportion of scalling down (to destination size)
	xprop = float(dstSize[0]) / float(src_w)
	yprop = float(dstSize[1]) / float(src_h)
	prop = min(xprop, yprop)

	# lets check potential size for that scaling
	potx = int(round(float(src_w) * prop))
	poty = int(round(float(src_h) * prop))
	# if those are bigger than minimum size lets return that
	if(potx >= minSize[0] and poty >= minSize[1]):
		if(potx <= 0):
			potx = 1
		if(poty <= 0):
			poty = 1
		return potx, poty
	# else we need to scale down a little bit less and then cropp
	# proportion of scalling down (to minimum size)
	xminprop = float(minSize[0]) / float(src_w)
	yminprop = float(minSize[1]) / float(src_h)
	# choose scale direction which is closer to original size
	minprop = max(xminprop, yminprop)
	# no scaling up, so 1 is the max value!
	minprop = min(minprop, 1)
	potx = int(round(float(src_w) * minprop))
	poty = int(round(float(src_h) * minprop))
	# cropp at one of the direction
	potx = min(potx, dstSize[0])
	poty = min(poty, dstSize[1])
	if(potx <= 0):
		potx = 1
	if(poty <= 0):
		poty = 1
	return potx, poty


def getThumbnailFlavorPath(uri="", flavor="normal"):
	if(type(uri) == type("string")):
		uri = [ uri ]
	thumbpath = homeDir() + ".thumbnails/"
	if(not os.path.isdir(thumbpath)):
		os.makedirs(thumbpath)
		fixPermissions(thumbpath)
	if(not flavor.endswith("/")):
		flavor = flavor + "/"
	if(not os.path.isdir(thumbpath + flavor)):
		os.makedirs(thumbpath + flavor)
		fixPermissions(thumbpath + flavor)
	ret = []
	for u in uri:
		ret.append(thumbpath + flavor + getThumbnailName(u))
	return ret

def areFilesProperImages( uris ):
	if(type(uris) == type("string")):
		uris = [ uris ]
	for uri in uris:
		im = 0
		uri = uriToFilepath(uri)
		try:
			im = Image.open(uri)
			im.load()
		except:
			return False
		if(im.size == (0, 0)):
			return False
	return True

def getThumbnailFlavorPaths():
	thumbpath = homeDir() + ".thumbnails/"
	if(not os.path.isdir(thumbpath)):
		os.makedirs(thumbpath)
		fixPermissions(thumbpath)

	flavorlist = getFlavorsList()

	ret = []
	for flavor in flavorlist:
		if(not os.path.isdir(thumbpath + flavor)):
			os.makedirs(thumbpath + flavor)
			fixPermissions(thumbpath + flavor)
		# add only those who finally exist
		if(os.path.isdir(thumbpath + flavor)):
			ret.append(thumbpath + flavor + "/")
	return ret

def deleteAllThumbnails():
	for path in getThumbnailFlavorPaths():
		try:
			deleteFiles(os.listdir(path))
		except OSError:
			continue

def getThumbnailName(uri):
	return md5(uri) + ".jpeg"

def getThumbnailFilepaths(uri):
	ret = []
	if(type(uri) == type("string")):
		filename = getThumbnailName(uri)
		for flavor in getThumbnailFlavorPaths():
			ret.append(flavor + filename)
	elif(type(uri) == type(["list", "of", "strings"])):
		for sinle_uri in uri:
			ret.extend(getThumbnailFilepaths(sinle_uri))
	return ret

def wait(ms):
	time.sleep(ms / 1000.0)

def isAppRunning(appName):
	ret = os.system("ps aux | grep -v grep | grep -v defunc | grep "+appName+" > /dev/null")
	return (0 == ret)

def isTumblerRunning():
	return isAppRunning("tumblerd")

def killProcess(procName):
	output = Popen("ps ax | grep " + procName + " | grep -v grep | awk '{print $1}'", stdout=PIPE, shell=True).communicate()[0]
	for pid in output.split():
		try:
			os.kill(int(pid), 9)
		except OSError, e:
			if(not e.errno == 3):
				raise e
	wait(200.0)

def killTumblerProcess():
	if(isTumblerRunning()):
		killProcess("tumblerd")

def killVideoThumbnailerProcess():
	if(isAppRunning("gst-video-thumbnailerd")):
		killProcess("gst-video-thumbnailerd")

def useTestFlavorsConf():
	if(areFilesExist(["/etc/xdg/thumbnails/_flavors.conf"])):
		os.system("rm -fr /etc/xdg/thumbnails/_flavors.conf")
	if(areFilesExist(["/etc/xdg/thumbnails/flavors.conf"])):
		os.system("mv /etc/xdg/thumbnails/flavors.conf /etc/xdg/thumbnails/_flavors.conf")
	os.system("cp /usr/share/tumbler-tests/data/flavors.conf /etc/xdg/thumbnails/flavors.conf")
	killVideoThumbnailerProcess()
	killTumblerProcess()

def useStandardFlavorsConf():
	if(areFilesExist(["/etc/xdg/thumbnails/flavors.conf"]) and areFilesExist(["/etc/xdg/thumbnails/_flavors.conf"])):
		os.system("rm -fr /etc/xdg/thumbnails/flavors.conf")
	if(areFilesExist(["/etc/xdg/thumbnails/_flavors.conf"])):
		os.system("mv /etc/xdg/thumbnails/_flavors.conf /etc/xdg/thumbnails/flavors.conf")
	killVideoThumbnailerProcess()
	killTumblerProcess()

def startTumblerProcess():
	if(not isTumblerRunning()):
		os.spawnl(os.P_NOWAITO, "/usr/lib/tumbler-1/tumblerd", "/usr/lib/tumbler-1/tumblerd")
		wait(200.0)

def restartTumblerProcess():
	if(isTumblerRunning()):
		killTumblerProcess()
	startTumblerProcess()
