/* vi:set et ai sw=2 sts=2 ts=2: */
/*-
 * Copyright (c) 2009 Jannis Pohlmann <jannis@xfce.org>
 * Copyright (c) 2009 Nokia, 
 *   written by Philip Van Hoof <philip@codeminded.be>
 *
 * This program is free software; you can redistribute it and/or 
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of 
 * the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public 
 * License along with this program; if not, write to the Free 
 * Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <glib.h>
#include <glib-object.h>

#include <tumbler/tumbler.h>

#include <quill-thumbnailer/quill-thumbnailer-provider.h>
#include <quill-thumbnailer/quill-thumbnailer.h>



static void   quill_thumbnailer_provider_thumbnailer_provider_init (TumblerThumbnailerProviderIface *iface);
static GList *quill_thumbnailer_provider_get_thumbnailers          (TumblerThumbnailerProvider      *provider);



struct _QuillThumbnailerProviderClass
{
  GObjectClass __parent__;
};

struct _QuillThumbnailerProvider
{
  GObject __parent__;
};



G_DEFINE_DYNAMIC_TYPE_EXTENDED (QuillThumbnailerProvider,
                                quill_thumbnailer_provider,
                                G_TYPE_OBJECT,
                                0,
                                TUMBLER_ADD_INTERFACE (TUMBLER_TYPE_THUMBNAILER_PROVIDER,
                                                       quill_thumbnailer_provider_thumbnailer_provider_init));



void
quill_thumbnailer_provider_register (TumblerProviderPlugin *plugin)
{
  quill_thumbnailer_provider_register_type (G_TYPE_MODULE (plugin));
}



static void
quill_thumbnailer_provider_class_init (QuillThumbnailerProviderClass *klass)
{
  GObjectClass *gobject_class;

  gobject_class = G_OBJECT_CLASS (klass);
}



static void
quill_thumbnailer_provider_class_finalize (QuillThumbnailerProviderClass *klass)
{
}



static void
quill_thumbnailer_provider_thumbnailer_provider_init (TumblerThumbnailerProviderIface *iface)
{
  iface->get_thumbnailers = quill_thumbnailer_provider_get_thumbnailers;
}



static void
quill_thumbnailer_provider_init (QuillThumbnailerProvider *provider)
{
}



static GList *
quill_thumbnailer_provider_get_thumbnailers (TumblerThumbnailerProvider *provider)
{
  GList              *thumbnailers = NULL;
  QuillThumbnailer   *thumbnailer;

  static const gchar *uri_schemes[] = { "file", NULL };

  /* http://doc.trolltech.com/4.5/qimage.html#reading-and-writing-image-files */
  static const gchar *mime_types[]  = { "image/jpeg", 
                                        "image/png",
                                        "image/ppm",
                                        "image/xbm",
                                        "image/xpm",
                                        "image/mng",
                                        "image/tiff",
                                        "image/bmp",
                                        "image/gif",
                                        "image/svg",
                                        "image/svg+xml",
                                        "image/pgm",
                                        NULL };


  /* create the quill thumbnailer */
  thumbnailer = (QuillThumbnailer *) g_object_new (TYPE_QUILL_THUMBNAILER, 
                                                   "uri-schemes", uri_schemes, 
                                                   "mime-types", mime_types, 
                                                   NULL);

  /* add the thumbnailer to the list */
  thumbnailers = g_list_append (thumbnailers, thumbnailer);

  return thumbnailers;
}

