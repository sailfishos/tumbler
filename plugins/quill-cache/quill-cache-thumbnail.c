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

#include <stdlib.h>

#include <glib.h>
#include <glib/gi18n.h>
#include <glib/gstdio.h>
#include <glib-object.h>
#include <gio/gio.h>

#include <tumbler/tumbler.h>

#include <quill-cache/quill-cache-cache.h>
#include <quill-cache/quill-cache-thumbnail.h>



/* Property identifiers */
enum
{
  PROP_0,
  PROP_CACHE,
  PROP_URI,
  PROP_FLAVOR,
};



static void     quill_cache_thumbnail_thumbnail_init  (TumblerThumbnailIface  *iface);
static void     quill_cache_thumbnail_finalize        (GObject                *object);
static void     quill_cache_thumbnail_get_property    (GObject                *object,
                                                       guint                   prop_id,
                                                       GValue                 *value,
                                                       GParamSpec             *pspec);
static void     quill_cache_thumbnail_set_property    (GObject                *object,
                                                       guint                   prop_id,
                                                       const GValue           *value,
                                                       GParamSpec             *pspec);
static gboolean quill_cache_thumbnail_load            (TumblerThumbnail       *thumbnail,
                                                       GCancellable           *cancellable,
                                                       GError                **error);
static gboolean quill_cache_thumbnail_needs_update    (TumblerThumbnail       *thumbnail,
                                                       const gchar            *uri,
                                                       guint64                 mtime);
static gboolean quill_cache_thumbnail_save_image_data (TumblerThumbnail       *thumbnail,
                                                       TumblerImageData       *data,
                                                       guint64                 mtime,
                                                       GCancellable           *cancellable,
                                                       GError                **error);



struct _QUILLCacheThumbnailClass
{
  GObjectClass __parent__;
};

struct _QUILLCacheThumbnail
{
  GObject __parent__;

  TumblerThumbnailFlavor *flavor;
  QUILLCacheCache        *cache;
  gchar                  *uri;
  gchar                  *cached_uri;
  guint64                 cached_mtime;
};



G_DEFINE_DYNAMIC_TYPE_EXTENDED (QUILLCacheThumbnail,
                                quill_cache_thumbnail,
                                G_TYPE_OBJECT,
                                0,
                                TUMBLER_ADD_INTERFACE (TUMBLER_TYPE_THUMBNAIL,
                                                       quill_cache_thumbnail_thumbnail_init));



void
quill_cache_thumbnail_register (TumblerCachePlugin *plugin)
{
  quill_cache_thumbnail_register_type (G_TYPE_MODULE (plugin));
}



static void
quill_cache_thumbnail_class_init (QUILLCacheThumbnailClass *klass)
{
  GObjectClass *gobject_class;

  gobject_class = G_OBJECT_CLASS (klass);
  gobject_class->finalize = quill_cache_thumbnail_finalize; 
  gobject_class->get_property = quill_cache_thumbnail_get_property;
  gobject_class->set_property = quill_cache_thumbnail_set_property;

  g_object_class_override_property (gobject_class, PROP_CACHE, "cache");
  g_object_class_override_property (gobject_class, PROP_URI, "uri");
  g_object_class_override_property (gobject_class, PROP_FLAVOR, "flavor");
}



static void
quill_cache_thumbnail_class_finalize (QUILLCacheThumbnailClass *klass)
{
}



static void
quill_cache_thumbnail_thumbnail_init (TumblerThumbnailIface *iface)
{
  iface->load = quill_cache_thumbnail_load;
  iface->needs_update = quill_cache_thumbnail_needs_update;
  iface->save_image_data = quill_cache_thumbnail_save_image_data;
}



static void
quill_cache_thumbnail_init (QUILLCacheThumbnail *thumbnail)
{
}



static void
quill_cache_thumbnail_finalize (GObject *object)
{
  QUILLCacheThumbnail *thumbnail = QUILL_CACHE_THUMBNAIL (object);
  
  g_free (thumbnail->uri);
  g_free (thumbnail->cached_uri);

  g_object_unref (thumbnail->cache);

  (*G_OBJECT_CLASS (quill_cache_thumbnail_parent_class)->finalize) (object);
}



static void
quill_cache_thumbnail_get_property (GObject    *object,
                                    guint       prop_id,
                                    GValue     *value,
                                    GParamSpec *pspec)
{
  QUILLCacheThumbnail *thumbnail = QUILL_CACHE_THUMBNAIL (object);

  switch (prop_id)
    {
    case PROP_CACHE:
      g_value_set_object (value, TUMBLER_CACHE (thumbnail->cache));
      break;
    case PROP_URI:
      g_value_set_string (value, thumbnail->uri);
      break;
    case PROP_FLAVOR:
      g_value_set_object (value, thumbnail->flavor);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}



static void
quill_cache_thumbnail_set_property (GObject      *object,
                                    guint         prop_id,
                                    const GValue *value,
                                    GParamSpec   *pspec)
{
  QUILLCacheThumbnail *thumbnail = QUILL_CACHE_THUMBNAIL (object);

  switch (prop_id)
    {
    case PROP_CACHE:
      thumbnail->cache = QUILL_CACHE_CACHE (g_value_dup_object (value));
      break;
    case PROP_URI:
      thumbnail->uri = g_value_dup_string (value);
      break;
    case PROP_FLAVOR:
      thumbnail->flavor = g_value_dup_object (value);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}



static gboolean
quill_cache_thumbnail_load (TumblerThumbnail *thumbnail,
                            GCancellable     *cancellable,
                            GError          **error)
{
  QUILLCacheThumbnail *cache_thumbnail = QUILL_CACHE_THUMBNAIL (thumbnail);
  GError              *err = NULL;
  GFile               *file;
  gchar               *path;

  g_return_val_if_fail (QUILL_CACHE_IS_THUMBNAIL (thumbnail), FALSE);
  g_return_val_if_fail (cancellable == NULL || G_IS_CANCELLABLE (cancellable), FALSE);
  g_return_val_if_fail (error == NULL || *error == NULL, FALSE);
  g_return_val_if_fail (cache_thumbnail->uri != NULL, FALSE);
  g_return_val_if_fail (QUILL_CACHE_IS_CACHE (cache_thumbnail->cache), FALSE);

  file = quill_cache_cache_get_file (cache_thumbnail->uri, 
                                     cache_thumbnail->flavor);
  path = g_file_get_path (file);
  g_object_unref (file);

  g_free (cache_thumbnail->cached_uri);
  cache_thumbnail->cached_uri = NULL;
  cache_thumbnail->cached_mtime = 0;

  quill_cache_cache_read_thumbnail_info (path, 
                                         &cache_thumbnail->cached_uri,
                                         &cache_thumbnail->cached_mtime,
                                         cancellable, &err);

  /* free the filename */
  g_free (path);

  if (err != NULL)
    {
      g_propagate_error (error, err);
      return FALSE;
    }
  else
    {
      return TRUE;
    }
}

static gboolean
is_matching_timestamp (guint64 stamp1, guint64 stamp2)
{
  /* On VFAT the mtime of a file can vary a second up and down */

  if (stamp1 > stamp2)
	{
      return (((gint64)stamp1) - ((gint64)stamp2) <= 1);
	}

  return (((gint64)stamp2) - ((gint64)stamp1) <= 1);
}

static gboolean
quill_cache_thumbnail_needs_update (TumblerThumbnail *thumbnail,
                                    const gchar      *uri,
                                    guint64           mtime)
{
  QUILLCacheThumbnail *cache_thumbnail = QUILL_CACHE_THUMBNAIL (thumbnail);

  g_return_val_if_fail (QUILL_CACHE_IS_THUMBNAIL (thumbnail), FALSE);
  g_return_val_if_fail (uri != NULL && *uri != '\0', FALSE);

  if (cache_thumbnail->cached_uri == NULL)
    return TRUE;

  if (cache_thumbnail->cached_mtime == 0)
    return TRUE;

  return g_utf8_collate (cache_thumbnail->uri, uri) != 0 
    || !is_matching_timestamp (cache_thumbnail->cached_mtime, mtime);
}



static gboolean
quill_cache_thumbnail_save_image_data (TumblerThumbnail *thumbnail,
                                       TumblerImageData *data,
                                       guint64           mtime,
                                       GCancellable     *cancellable,
                                       GError          **error)
{
  QUILLCacheThumbnail *cache_thumbnail = QUILL_CACHE_THUMBNAIL (thumbnail);
  GFile               *dest_file;
  gchar               *dest_path;
  GError              *error_n = NULL;

  dest_file = quill_cache_cache_get_file (cache_thumbnail->uri, 
                                          cache_thumbnail->flavor);

  dest_path = g_file_get_path (dest_file);

  quill_cache_cache_write_thumbnail_info (dest_path,
                                          cache_thumbnail->uri,
                                          mtime,
                                          cancellable,
                                          &error_n);

  if (!error_n) 
    {
      g_free (cache_thumbnail->cached_uri);
      cache_thumbnail->cached_uri = g_strdup (cache_thumbnail->uri);
      cache_thumbnail->cached_mtime = mtime;
    }
  else
    g_propagate_error (error, error_n);

  g_free (dest_path);
  g_object_unref (dest_file);

  return TRUE;
}
