# vi:set ts=8 sw=8 noet ai nocindent:
# -
# Copyright (c) 2009 Nokia, 
#   written by Philip Van Hoof <philip@codeminded.be>
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of 
# the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public 
# License along with this program; if not, write to the Free 
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.
#
# Author: Philip Van Hoof <philip@codeminded.be>

if TUMBLER_QUILL_THUMBNAILER

tumbler_plugindir = $(libdir)/tumbler-$(TUMBLER_VERSION_API)/plugins
tumbler_plugin_LTLIBRARIES =						\
	tumbler-quill-thumbnailer.la

tumbler_quill_thumbnailer_la_SOURCES =					\
	quill-thumbnailer-plugin.c					\
	quill-thumbnailer-provider.c					\
	quill-thumbnailer-provider.h					\
	quill-thumbnailer.cpp						\
	quill-thumbnailer.h

tumbler_quill_thumbnailer_la_CFLAGS =					\
	-I$(top_builddir)						\
	-I$(top_builddir)/plugins					\
	-I$(top_srcdir)							\
	-I$(top_srcdir)/plugins						\
	-DG_LOG_DOMAIN=\"tumbler-quill-thumbnailer\"			\
	-DPACKAGE_LOCALE_DIR=\"$(localedir)\"				\
	$(GIO_CFLAGS)							\
	$(GLIB_CFLAGS)							\
	$(PLATFORM_CPPFLAGS)						\
	$(QUILL_CFLAGS)							

tumbler_quill_thumbnailer_la_CPPFLAGS =					\
	$(tumbler_quill_thumbnailer_la_CFLAGS)				\
	-std=c++11

tumbler_quill_thumbnailer_la_LDFLAGS =					\
	-avoid-version							\
	-export-dynamic							\
	-module								\
	$(PLATFORM_LDFLAGS)

tumbler_quill_thumbnailer_la_LIBADD =					\
	$(GIO_LIBS)							\
	$(GLIB_LIBS)							\
	$(QUILL_LIBS)

if TUMBLER_PIXBUF_THUMBNAILER
tumbler_quill_thumbnailer_la_CFLAGS += $(GDK_PIXBUF_CFLAGS)
tumbler_quill_thumbnailer_la_LIBADD += $(GDK_PIXBUF_LIBS)
endif

endif
