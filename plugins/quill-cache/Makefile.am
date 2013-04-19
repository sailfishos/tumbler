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

if TUMBLER_QUILL_THUMBNAILER

tumbler_plugindir = $(libdir)/tumbler-$(TUMBLER_VERSION_API)/plugins/cache
tumbler_plugin_LTLIBRARIES =						\
	tumbler-quill-cache.la

tumbler_quill_cache_la_SOURCES =					\
	quill-cache-cache.c						\
	quill-cache-cache.h						\
	quill-cache-plugin.c						\
	quill-cache-thumbnail.c						\
	quill-cache-thumbnail.h

tumbler_quill_cache_la_CFLAGS =						\
	-I$(top_builddir)						\
	-I$(top_builddir)/plugins					\
	-I$(top_srcdir)							\
	-I$(top_srcdir)/plugins						\
	-DG_LOG_DOMAIN=\"tumbler-quill-cache\"				\
	-DPACKAGE_LOCALE_DIR=\"$(localedir)\"				\
	$(GIO_CFLAGS)							\
	$(GLIB_CFLAGS)							\
	$(PLATFORM_CPPFLAGS)						

tumbler_quill_cache_la_LDFLAGS =					\
	-avoid-version							\
	-export-dynamic							\
	-module								\
	$(PLATFORM_LDFLAGS)

tumbler_quill_cache_la_LIBADD =						\
	$(GIO_LIBS)							\
	$(GLIB_LIBS)							

# install symlink to 'tumbler-cache-plugin.so'
install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(tumbler_plugindir)
	-( cd $(DESTDIR)$(tumbler_plugindir) ; \
		test -x tumbler-quill-cache.so || \
		ln -sf tumbler-quill-cache.so tumbler-cache-plugin.so )

endif
