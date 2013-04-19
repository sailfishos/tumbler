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
#include <utime.h>
#include <string.h>
#include <unistd.h>
#include <sys/file.h>

#include <glib.h>
#include <glib/gstdio.h>
#include <glib/gi18n.h>
#include <glib-object.h>
#include <gio/gio.h>

#include <tumbler/tumbler.h>

#include <quill-cache/quill-cache-cache.h>
#include <quill-cache/quill-cache-thumbnail.h>


static void              quill_cache_cache_iface_init         (TumblerCacheIface      *iface);
static void              quill_cache_cache_finalize           (GObject                *object);
static TumblerThumbnail *quill_cache_cache_get_thumbnail      (TumblerCache           *cache,
                                                               const gchar            *uri,
                                                               TumblerThumbnailFlavor *flavor);
static void              quill_cache_cache_cleanup            (TumblerCache           *cache,
                                                               const gchar *const     *base_uris,
                                                               guint64                 since);
static void              quill_cache_cache_delete             (TumblerCache           *cache,
                                                               const gchar *const     *uris);
static void              quill_cache_cache_copy               (TumblerCache           *cache,
                                                               const gchar *const     *from_uris,
                                                               const gchar *const     *to_uris);
static void              quill_cache_cache_move               (TumblerCache           *cache,
                                                               const gchar *const     *from_uris,
                                                               const gchar *const     *to_uris);
static gboolean          quill_cache_cache_is_thumbnail       (TumblerCache           *cache,
                                                               const gchar            *uri);
static GList            *quill_cache_cache_get_flavors        (TumblerCache           *cache);
static const gchar      *quill_cache_cache_get_home           (void);



struct _QUILLCacheCacheClass
{
  GObjectClass __parent__;
};

struct _QUILLCacheCache
{
  GObject __parent__;

  GList  *flavors;
};


G_DEFINE_DYNAMIC_TYPE_EXTENDED (QUILLCacheCache,
                                quill_cache_cache,
                                G_TYPE_OBJECT,
                                0,
                                TUMBLER_ADD_INTERFACE (TUMBLER_TYPE_CACHE,
                                                       quill_cache_cache_iface_init));


void
quill_cache_cache_register (TumblerCachePlugin *plugin)
{
  quill_cache_cache_register_type (G_TYPE_MODULE (plugin));
}



static void
quill_cache_cache_class_init (QUILLCacheCacheClass *klass)
{
  GObjectClass *gobject_class;

  gobject_class = G_OBJECT_CLASS (klass);
  gobject_class->finalize = quill_cache_cache_finalize;
}

static void
quill_cache_cache_class_finalize (QUILLCacheCacheClass *klass)
{
}


static void
quill_cache_cache_iface_init (TumblerCacheIface *iface)
{
  iface->get_thumbnail = quill_cache_cache_get_thumbnail;
  iface->cleanup = quill_cache_cache_cleanup;
  iface->do_delete = quill_cache_cache_delete;
  iface->copy = quill_cache_cache_copy;
  iface->move = quill_cache_cache_move;
  iface->is_thumbnail = quill_cache_cache_is_thumbnail;
  iface->get_flavors = quill_cache_cache_get_flavors;
}


static void
quill_cache_load_flavors_conf (QUILLCacheCache *cache,
                               const gchar     *uri)
{
  GKeyFile               *key_file;
  TumblerThumbnailFlavor *flavor;
  GError                 *error = NULL;
  gchar                 **sections;
  gint                    width;
  gint                    height;
  gint                    min_width;
  gint                    min_height;
  gchar                  *name;
  guint                   n;

 /* allocate the key file */
  key_file = g_key_file_new ();

  /* try to load the key file from the overrides file */
  if (!g_key_file_load_from_file (key_file, uri, G_KEY_FILE_NONE, &error))
    {
      g_warning (_("Failed to load the file \"%s\": %s"), uri, error->message);
      g_clear_error (&error);
      g_key_file_free (key_file);

      flavor = tumbler_thumbnail_flavor_new_normal ();
      cache->flavors = g_list_prepend (cache->flavors, flavor);

      return;
    }

  /* determine sections in the key file */
  sections = g_key_file_get_groups (key_file, NULL);

 /* iterate over all sections */
  for (n = 0; sections != NULL && sections[n] != NULL; ++n)
    {
     
      name = g_key_file_get_string (key_file, sections[n], "Name", &error);

      if (name == NULL)
        {
          g_warning (_("Malformed section \"%s\" in file \"%s\": %s"),
                     sections[n], uri, error->message);
          g_clear_error (&error);
          continue;
        }

      width = g_key_file_get_integer (key_file, sections[n], "Width", &error);

      if (error != NULL)
        {
          g_warning (_("Malformed section \"%s\" in file \"%s\": %s"),
                     sections[n], uri, error->message);
          g_clear_error (&error);
          continue;
        }

      height = g_key_file_get_integer (key_file, sections[n], "Height", &error);

      if (error != NULL)
        {
          g_warning (_("Malformed section \"%s\" in file \"%s\": %s"),
                     sections[n], uri, error->message);
          g_clear_error (&error);
          continue;
        }

      min_width = g_key_file_get_integer (key_file, sections[n], "MinimumWidth", &error);

      if ((error != NULL) && (error->code != G_KEY_FILE_ERROR_KEY_NOT_FOUND))
        {
          g_warning (_("Malformed section \"%s\" in file \"%s\": %s"),
                     sections[n], uri, error->message);
          continue;
        }
      g_clear_error (&error);

      min_height = g_key_file_get_integer (key_file, sections[n], "MinimumHeight", &error);

      if ((error != NULL) && (error->code != G_KEY_FILE_ERROR_KEY_NOT_FOUND))
        {
          g_warning (_("Malformed section \"%s\" in file \"%s\": %s"),
                     sections[n], uri, error->message);
          continue;
        }
      g_clear_error (&error);

      flavor = tumbler_thumbnail_flavor_new_with_minimum_size (name, width, height,
                                                               min_width, min_height);
      cache->flavors = g_list_prepend (cache->flavors, flavor);

      g_free (name);
    }

  g_key_file_free (key_file);
  g_strfreev (sections);
}


static void
quill_cache_cache_init (QUILLCacheCache *cache)
{
  GError                 *error = NULL;
  guint                   n;
  const gchar * const    *config_dirs;
  const gchar            *basename;

  config_dirs = g_get_system_config_dirs ();

  for (n = 0; config_dirs[n] != NULL; n++)
    {
      gchar *filen;

      filen = g_build_filename (config_dirs[n], "thumbnails",
                                "flavors.conf", NULL);
      if (g_file_test (filen, G_FILE_TEST_IS_REGULAR))
        quill_cache_load_flavors_conf (cache, filen);

      g_free (filen);

      gchar *dir_name;
      dir_name = g_build_filename (config_dirs[n], "thumbnails",
                                   "flavors.conf.d", NULL);
      if (g_file_test (dir_name, G_FILE_TEST_IS_DIR)) {

        GDir *dir = g_dir_open(dir_name, 0, &error);
        if (error != NULL)
          {
            g_warning (_("Failed to open the dir \"%s\": %s"),
                       dir_name, error->message);
            g_clear_error (&error);
            continue;
          }

        while ((basename = g_dir_read_name (dir)) != NULL)
          {
            filen = g_build_filename (config_dirs[n], "thumbnails",
                                      "flavors.conf.d", basename, NULL);
            quill_cache_load_flavors_conf (cache, filen);
            g_free (filen);
          }

        g_dir_close (dir);
      }
    }
}

static void
quill_cache_cache_finalize (GObject *object)
{
  QUILLCacheCache *cache = QUILL_CACHE_CACHE (object);
 
  g_list_foreach (cache->flavors, (GFunc) g_object_unref, NULL);
  g_list_free (cache->flavors);
}

static TumblerThumbnail *
quill_cache_cache_get_thumbnail (TumblerCache *cache,
                                 const gchar  *uri,
                                 TumblerThumbnailFlavor *flavor)
{
  g_return_val_if_fail (QUILL_CACHE_IS_CACHE (cache), NULL);
  g_return_val_if_fail (uri != NULL && *uri != '\0', NULL);
  g_return_val_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor), NULL);

  /* TODO check if the flavor is supported */
 
  return g_object_new (QUILL_CACHE_TYPE_THUMBNAIL, "cache", cache,
                       "uri", uri, "flavor", flavor, NULL);
}



static void
quill_cache_cache_cleanup (TumblerCache        *cache,
                           const gchar *const  *base_uris,
                           guint64              since)
{
  QUILLCacheCache *quill_cache = QUILL_CACHE_CACHE (cache);
  const gchar     *file_basename;
  guint64          mtime;
  GFile           *dummy_file;
  GFile           *parent;
  GList           *iter;
  gchar           *dirname;
  gchar           *filename;
  gchar           *uri;
  GDir            *dir;

  g_return_if_fail (QUILL_CACHE_IS_CACHE (cache));
  
  for (iter = quill_cache->flavors; iter != NULL; iter = iter->next)
    {
      dummy_file = quill_cache_cache_get_file ("foo", iter->data);
      parent = g_file_get_parent (dummy_file);
      dirname = g_file_get_path (parent);
      g_object_unref (parent);
      g_object_unref (dummy_file);

      dir = g_dir_open (dirname, 0, NULL);

      if (dir != NULL)
        {
          while ((file_basename = g_dir_read_name (dir)) != NULL)
            {
              filename = g_build_filename (dirname, file_basename, NULL);

              if (quill_cache_cache_read_thumbnail_info (filename, &uri, &mtime, 
                                                         NULL, NULL))
                {
                   guint n;

                   for (n = 0; base_uris != NULL && base_uris[n] != NULL; ++n)
                     {
                       const gchar *uri_prefix = base_uris[n];

                       if ((uri_prefix == NULL || uri == NULL) 
                          || (g_str_has_prefix (uri, uri_prefix) && (mtime <= since)))
                        {
                           g_unlink (filename);
                        }
                     }
                }

              g_free (filename);
            }

          g_dir_close (dir);
        }

      g_free (dirname);
    }
}



static void
quill_cache_cache_delete (TumblerCache        *cache,
                          const gchar *const  *uris)
{
  QUILLCacheCache *quill_cache = QUILL_CACHE_CACHE (cache);
  GList           *iter;
  GFile           *file;
  gint             n;

  g_return_if_fail (QUILL_CACHE_IS_CACHE (cache));
  g_return_if_fail (uris != NULL);

  for (iter = quill_cache->flavors; iter != NULL; iter = iter->next)
    {
      for (n = 0; uris[n] != NULL; ++n)
        {
          file = quill_cache_cache_get_file (uris[n], iter->data);
          g_file_delete (file, NULL, NULL);
          g_object_unref (file);
        }
    }
}

static void
quill_cache_cache_copy (TumblerCache       *cache,
                        const gchar *const *from_uris,
                        const gchar *const *to_uris)
{
  QUILLCacheCache *quill_cache = QUILL_CACHE_CACHE (cache);
  GFileInfo       *info;
  guint64          mtime;
  GFile           *dest_file;
  GFile           *dest_source_file;
  GFile           *from_file;
  GFile           *temp_file;
  GList           *iter;
  gchar           *temp_path;
  gchar           *dest_path;
  guint            n;

  g_return_if_fail (QUILL_CACHE_IS_CACHE (cache));
  g_return_if_fail (from_uris != NULL);
  g_return_if_fail (to_uris != NULL);
  g_return_if_fail (g_strv_length ((gchar **)from_uris) == g_strv_length ((gchar **)to_uris));

  for (iter = quill_cache->flavors; iter != NULL; iter = iter->next)
    {
      for (n = 0; n < g_strv_length ((gchar **)from_uris); ++n)
        {
          dest_source_file = g_file_new_for_uri (to_uris[n]);
          info = g_file_query_info (dest_source_file, G_FILE_ATTRIBUTE_TIME_MODIFIED,
                                    G_FILE_QUERY_INFO_NONE, NULL, NULL);
          g_object_unref (dest_source_file);

          if (info == NULL)
            continue;

          mtime = g_file_info_get_attribute_uint64 (info, 
                                                    G_FILE_ATTRIBUTE_TIME_MODIFIED);
          g_object_unref (info);

          from_file = quill_cache_cache_get_file (from_uris[n], iter->data);
          temp_file = quill_cache_cache_get_temp_file (to_uris[n], iter->data);

          if (g_file_copy (from_file, temp_file, G_FILE_COPY_OVERWRITE, 
                           NULL, NULL, NULL, NULL))
            {
              temp_path = g_file_get_path (temp_file);

              if (quill_cache_cache_write_thumbnail_info (temp_path, to_uris[n], mtime,
                                                          NULL, NULL))
                {
                  dest_file = quill_cache_cache_get_file (to_uris[n], iter->data);
                  dest_path = g_file_get_path (dest_file);

                  if (g_rename (temp_path, dest_path) != 0)
                    g_unlink (temp_path);

                  g_free (dest_path);
                  g_object_unref (dest_file);
                }
              else
                {
                  g_unlink (temp_path);
                }

              g_free (temp_path);
            }

          g_object_unref (temp_file);
          g_object_unref (from_file);
        }
    }
}




static void
quill_cache_cache_move (TumblerCache       *cache,
                        const gchar *const *from_uris,
                        const gchar *const *to_uris)
{
  QUILLCacheCache *quill_cache = QUILL_CACHE_CACHE (cache);
  GFileInfo       *info;
  guint64          mtime;
  GFile           *dest_file;
  GFile           *dest_source_file;
  GFile           *from_file;
  GFile           *temp_file;
  GList           *iter;
  gchar           *from_path;
  gchar           *temp_path;
  gchar           *dest_path;
  guint            n;

  g_return_if_fail (QUILL_CACHE_IS_CACHE (cache));
  g_return_if_fail (from_uris != NULL);
  g_return_if_fail (to_uris != NULL);
  g_return_if_fail (g_strv_length ((gchar **)from_uris) == g_strv_length ((gchar **)to_uris));

  for (iter = quill_cache->flavors; iter != NULL; iter = iter->next)
    {
      for (n = 0; n < g_strv_length ((gchar **)from_uris); ++n)
        {
          dest_source_file = g_file_new_for_uri (to_uris[n]);
          info = g_file_query_info (dest_source_file, G_FILE_ATTRIBUTE_TIME_MODIFIED,
                                    G_FILE_QUERY_INFO_NONE, NULL, NULL);
          g_object_unref (dest_source_file);

          if (info == NULL)
            continue;

          mtime = g_file_info_get_attribute_uint64 (info, 
                                                    G_FILE_ATTRIBUTE_TIME_MODIFIED);
          g_object_unref (info);

          from_file = quill_cache_cache_get_file (from_uris[n], iter->data);
          temp_file = quill_cache_cache_get_temp_file (to_uris[n], iter->data);

          if (g_file_move (from_file, temp_file, G_FILE_COPY_OVERWRITE, 
                           NULL, NULL, NULL, NULL))
            {
              temp_path = g_file_get_path (temp_file);

              if (quill_cache_cache_write_thumbnail_info (temp_path, to_uris[n], mtime,
                                                          NULL, NULL))
                {
                  dest_file = quill_cache_cache_get_file (to_uris[n], iter->data);
                  dest_path = g_file_get_path (dest_file);

                  if (g_rename (temp_path, dest_path) != 0)
                    g_unlink (temp_path);

                  g_free (dest_path);
                  g_object_unref (dest_file);
                }
              else
                {
                  g_unlink (temp_path);
                }

              g_free (temp_path);
            }

          from_path = g_file_get_path (from_file);
          g_unlink (from_path);
          g_free (from_path);

          g_object_unref (temp_file);
          g_object_unref (from_file);
        }
    }
}



static gboolean
quill_cache_cache_is_thumbnail (TumblerCache *cache,
                                const gchar  *uri)
{
  QUILLCacheCache *quill_cache = QUILL_CACHE_CACHE (cache);
  const gchar   *home;
  const gchar   *dirname;
  gboolean       is_thumbnail = FALSE;
  GList         *iter;
  GFile         *flavor_dir;
  GFile         *file;
  gchar         *path;

  g_return_val_if_fail (QUILL_CACHE_IS_CACHE (cache), FALSE);
  g_return_val_if_fail (uri != NULL, FALSE);

  for (iter = quill_cache->flavors; !is_thumbnail && iter != NULL; iter = iter->next)
    {
      home = quill_cache_cache_get_home ();
      dirname = tumbler_thumbnail_flavor_get_name (iter->data);
      path = g_build_filename (home, ".thumbnails", dirname, NULL);

      flavor_dir = g_file_new_for_path (path);
      file = g_file_new_for_uri (uri);

      if (g_file_has_prefix (file, flavor_dir))
        is_thumbnail = TRUE;

      g_object_unref (file);
      g_object_unref (flavor_dir);

      g_free (path);
    }

  return is_thumbnail;
}


static GList *
quill_cache_cache_get_flavors (TumblerCache *cache)
{
  QUILLCacheCache *quill_cache = QUILL_CACHE_CACHE (cache);
  GList           *flavors = NULL;
  GList           *iter;
 
  g_return_val_if_fail (QUILL_CACHE_IS_CACHE (cache), NULL);
 
  for (iter = g_list_last (quill_cache->flavors); iter != NULL; iter = iter->prev)
    flavors = g_list_prepend (flavors, g_object_ref (iter->data));
 
  return flavors;
}

static const gchar *
quill_cache_cache_get_home (void)
{
  return g_getenv ("HOME") != NULL ? g_getenv ("HOME") : g_get_home_dir ();
}



GFile *
quill_cache_cache_get_file (const gchar            *uri,
                            TumblerThumbnailFlavor *flavor)
{
  const gchar *home;
  const gchar *dirname;
  GFile       *file;
  gchar       *filename;
  gchar       *md5_hash;
  gchar       *path;

  g_return_val_if_fail (uri != NULL && *uri != '\0', NULL);
  g_return_val_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor), NULL);
 
  home = quill_cache_cache_get_home ();
  dirname = tumbler_thumbnail_flavor_get_name (flavor);

  md5_hash = g_compute_checksum_for_string (G_CHECKSUM_MD5, uri, -1);
  filename = g_strdup_printf ("%s.jpeg", md5_hash);
  path = g_build_filename (home, ".thumbnails", dirname, filename, NULL);

  file = g_file_new_for_path (path);

  g_free (path);
  g_free (filename);
  g_free (md5_hash);

  return file;
}



GFile *
quill_cache_cache_get_temp_file (const gchar            *uri,
                                 TumblerThumbnailFlavor *flavor)
{
  const gchar *home;
  const gchar *dirname;
  GTimeVal     current_time = { 0, 0 };
  GFile       *file;
  gchar       *filename;
  gchar       *md5_hash;
  gchar       *path;

  g_return_val_if_fail (uri != NULL && *uri != '\0', NULL);
  g_return_val_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor), NULL);
 
  home = quill_cache_cache_get_home ();
  dirname = tumbler_thumbnail_flavor_get_name (flavor);
 
  g_get_current_time (&current_time);

  md5_hash = g_compute_checksum_for_string (G_CHECKSUM_MD5, uri, -1);
  filename = g_strdup_printf ("%s-%ld-%ld.jpeg", md5_hash, 
                              current_time.tv_sec, current_time.tv_usec);
  path = g_build_filename (home, ".thumbnails", dirname, filename, NULL);

  file = g_file_new_for_path (path);

  g_free (path);
  g_free (filename);
  g_free (md5_hash);

  return file;
}

gboolean
quill_cache_cache_read_thumbnail_info (const gchar  *filename,
                                       gchar       **uri,
                                       guint64      *mtime,
                                       GCancellable *cancellable,
                                       GError      **error)
{
  GFile        *file;
  GFileInfo    *file_info;
  GError       *error_n = NULL;
  gchar        *path;
  gsize         max_pos;
  gsize         next_len;
  guint         s_len;
  gchar        *cur;
  GMappedFile  *mapped;
  gboolean      have_set = FALSE;
  const gchar  *home;

  g_return_val_if_fail (filename != NULL, FALSE);
  g_return_val_if_fail (uri != NULL, FALSE);
  g_return_val_if_fail (mtime != NULL, FALSE);
  g_return_val_if_fail (cancellable == NULL || G_IS_CANCELLABLE (cancellable), FALSE);
  g_return_val_if_fail (error == NULL || *error == NULL, FALSE);

  if (g_cancellable_set_error_if_cancelled (cancellable, error))
    return FALSE;

  file = g_file_new_for_path (filename);

  /* query the modified time from the file */
  file_info = g_file_query_info (file, G_FILE_ATTRIBUTE_TIME_MODIFIED, 
                                 G_FILE_QUERY_INFO_NONE, cancellable, &error_n);

  if (error_n)
    {
      *uri = NULL;
      *mtime = 0;

      g_error_free (error_n);

      if (file_info)
        g_object_unref (file_info);
      g_object_unref (file);

      return TRUE;
    }

  /* Get original image's mtime */
  *mtime = g_file_info_get_attribute_uint64 (file_info,
                                             G_FILE_ATTRIBUTE_TIME_MODIFIED);


  if (file_info)
    g_object_unref (file_info);
  g_object_unref (file);

  home = quill_cache_cache_get_home ();
  path = g_build_filename (home, ".thumbnails", ".data", NULL);

  mapped = g_mapped_file_new (path, FALSE, &error_n);

  if (error_n || !mapped)
    {
      g_error_free (error_n);

      *uri = NULL;

      return TRUE;
    }

  cur = g_mapped_file_get_contents (mapped);
  max_pos = (gsize) (cur + g_mapped_file_get_length (mapped));
  s_len = strlen (filename);

  *uri = NULL;

  while (((gsize)cur) < max_pos) 
    {
      next_len = strnlen (cur, max_pos - ((gsize)cur)) + 2;

      if (g_strrstr_len (cur, s_len, filename) && 
          ((gsize)cur) + s_len + 3 < max_pos   &&
          (cur[s_len + 0] == ' ')              && 
          (cur[s_len + 1] == '=')              && 
          (cur[s_len + 2] == ' '))
       {
           *uri = g_strdup (cur + s_len + 3);
           have_set = TRUE;
        }

      cur += next_len;
    }

  g_mapped_file_free (mapped);

  return have_set;
}


gboolean
quill_cache_cache_write_thumbnail_info (const gchar  *filename,
                                        const gchar  *uri,
                                        guint64       mtime,
                                        GCancellable *cancellable,
                                        GError      **error)
{
  struct utimbuf  buf;
  gchar          *path;
  const gchar    *home;
  FILE           *journal;
  size_t          len;
  gsize           max_pos;
  gsize           next_len;
  guint           s_len;
  gchar          *cur;
  GMappedFile    *mapped;

  buf.actime = buf.modtime = mtime;
  utime (filename, &buf);

  home = quill_cache_cache_get_home ();
  path = g_build_filename (home, ".thumbnails", ".data", NULL);

  mapped = g_mapped_file_new (path, FALSE, NULL);

  if (mapped)
    {
      cur = g_mapped_file_get_contents (mapped);
      max_pos = (gsize) (cur + g_mapped_file_get_length (mapped));
      s_len = strlen (filename);

      while (((gsize)cur) < max_pos) 
        {

          if ((((gsize)cur) + s_len) > max_pos)
            break;

          next_len = strnlen (cur, max_pos - ((gsize)cur)) + 2;

          if (g_strrstr_len (cur, s_len, filename) && 
              ((gsize)cur) + s_len + 3 < max_pos   &&
              (cur[s_len + 0] == ' ')              && 
              (cur[s_len + 1] == '=')              && 
              (cur[s_len + 2] == ' '))
            {
               g_free (path);
               g_mapped_file_free (mapped);
               return TRUE;
            }
          cur += next_len;
        }
      g_mapped_file_free (mapped);
    }

  journal = fopen (path, "a");
  g_free (path);

  if (journal) 
    {
      flock(fileno (journal), LOCK_EX);
      path = g_strdup_printf ("%s = %s", filename, uri);
      len = strlen (path);
      write (fileno (journal), path, len);
      write (fileno (journal), "\0\0", 2);
      fsync (fileno (journal));
      g_free (path);
      flock(fileno (journal), LOCK_UN);
      fclose (journal);
    }

  return TRUE;
}
