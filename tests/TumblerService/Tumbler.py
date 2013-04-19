#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import sys

# log Levels:
# 0 - all logs (information also)
# 1 - debug and higher
# 2 - warnings and higher
# 3 - errors and higher
# 4 - criticial
# 5 - none

DBusGMainLoop(set_as_default=True)

class Tumbler:
	def __init__(self):
		self.logLevel = 5;
		try:
			self.bus = dbus.SessionBus()
		except:
			print "Error while trying to access DBus Session Bus!"
			sys.exit(101)

		self.tumbler = self.bus.get_object('org.freedesktop.thumbnails.Thumbnailer1','/org/freedesktop/thumbnails/Thumbnailer1')
		self.tumbler_iface = dbus.Interface(self.tumbler, 'org.freedesktop.thumbnails.Thumbnailer1')
		self.cache = self.bus.get_object('org.freedesktop.thumbnails.Cache1','/org/freedesktop/thumbnails/Cache1')
		self.cache_iface = dbus.Interface(self.cache, 'org.freedesktop.thumbnails.Cache1')

		try:
			self.loop = gobject.MainLoop()
		except:
			print "Could not initialize dbus and glib main loops!"
			sys.exit(102)

		self.bus.add_signal_receiver (self.Finished_cb,
		                              signal_name="Finished",
		                              dbus_interface="org.freedesktop.thumbnails.Thumbnailer1",
		                              path="/org/freedesktop/thumbnails/Thumbnailer1")
		self.bus.add_signal_receiver (self.Started_cb,
		                              signal_name="Started",
		                              dbus_interface="org.freedesktop.thumbnails.Thumbnailer1",
		                              path="/org/freedesktop/thumbnails/Thumbnailer1")
		self.bus.add_signal_receiver (self.Ready_cb,
		                              signal_name="Ready",
		                              dbus_interface="org.freedesktop.thumbnails.Thumbnailer1",
		                              path="/org/freedesktop/thumbnails/Thumbnailer1")
		self.bus.add_signal_receiver (self.Error_cb,
		                              signal_name="Error",
		                              dbus_interface="org.freedesktop.thumbnails.Thumbnailer1",
		                              path="/org/freedesktop/thumbnails/Thumbnailer1")

		self.signal_ready = []
		self.signal_error = []
		self.signal_started = 0
		self.signal_finished = 0
		self.quitOnFinish = False
		self.quitOnError = False

	def setLogLevel(self, newLevel):
		self.logLevel = newLevel
		self.log(1, "-- Setting new logging level to " + str(newLevel))

	def setQuitOnError(self, value=True):
		self.quitOnError = value

	def log(self, level, msg):
		if(level >= self.logLevel):
			print "TumblerLogs(" + str(level) + "):", msg

	def resetState(self):
		self.log(1, "[-- Clearing Tumbler state")
		self.signal_ready = []
		self.signal_error = []
		self.signal_started = 0
		self.signal_finished = 0
		self.quitOnFinish = False

	def Started_cb(self, handle):
		''' handle Started signal from Tumbler '''
		self.log(1, "---- - Started_cb callback called")
		self.signal_started += 1

	def Finished_cb(self, handle):
		''' handle Finished signal from Tumbler '''
		self.log(1, "---- - Finished_cb callback called")
		self.signal_finished += 1
		if(self.quitOnFinish):
			self.log(1, "      quiting main loop")
			self.loop.quit()

	def Ready_cb(self, handle, uris):
		''' handle Ready signal from Tumbler '''
		self.log(1, "---- - Ready_cb callback called")
		self.signal_ready.append(uris)

	def Error_cb(self, handle, uris, code, message):
		''' handle Error signal from Tumbler '''
		self.log(1, "---- - Error_cb callback called. MSG:"+message)
		self.signal_error.append([code, message, uris])
		if(self.quitOnError):
			self.log(1, "      quiting main loop")
			self.loop.quit()

	def Cache_delete(self, uris):
		''' notify tumbler that some files were deleted '''
		self.log(1, "[-- Calling Delete operation on:" + str(uris))
		self.cache_iface.Delete(uris)

	def Cache_move(self, uris_src, uris_dst):
		''' notify tumbler that some files were deleted '''
		self.log(1, "[-- Calling Move operation on:" + str(uris_src) + "->" + str(uris_dst))
		self.cache_iface.Move(uris_src, uris_dst)

	def Cache_copy(self, uris_src, uris_dst):
		''' notify tumbler that some files were deleted '''
		self.log(1, "[-- Calling Copy operation on:" + str(uris_src) + "->" + str(uris_dst))
		self.cache_iface.Copy(uris_src, uris_dst)

	def simple_Queue(self, uris=[], mimes=[], flavor="normal", scheduler="default"):
		''' make a request and wait for Finished signal '''
		self.log(1, "[-- Calling Queue operation on:" + str(uris) + " for flavor:" + flavor + " and scheduler:" + scheduler)
		self.quitOnFinish = True
		self.tumbler_iface.Queue(uris, mimes, flavor, scheduler, 0)
		self.log(1, "[----- Starting loop for receiving signals from Tumbler.")
		self.loop.run()
		self.log(0, "----- simple_Queue finished --]")

	def finishedSignalCount(self):
		return self.signal_finished

	def startedSignalCount(self):
		return self.signal_started

	def readySignalCount(self):
		return len(self.signal_ready)

	def errorSignalCount(self):
		return len(self.signal_error)

	def readyItemsCount(self):
		ret = 0
		for items in self.signal_ready:
			ret = ret + len(items)
		return ret

	def errorItemsCount(self):
		ret = 0
		for items in self.signal_error:
			ret = ret + len(items[2])
		return ret

	def noErrors(self):
		return (0 == self.errorItemsCount())

	def wasCreated(self, name):
		for items in self.signal_ready:
			for item in items:
				if(item == name):
					return True
		return False
