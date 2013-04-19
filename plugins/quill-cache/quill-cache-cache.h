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

#ifndef __QUILL_CACHE_CACHE_H__
#define __QUILL_CACHE_CACHE_H__

#include <gio/gio.h>

#include <tumbler/tumbler.h>

G_BEGIN_DECLS;

#define QUILL_CACHE_TYPE_CACHE            (quill_cache_cache_get_type ())
#define QUILL_CACHE_CACHE(obj)            (G_TYPE_CHECK_INSTANCE_CAST ((obj), QUILL_CACHE_TYPE_CACHE, QUILLCacheCache))
#define QUILL_CACHE_CACHE_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass), QUILL_CACHE_TYPE_CACHE, QUILLCacheCacheClass))
#define QUILL_CACHE_IS_CACHE(obj)         (G_TYPE_CHECK_INSTANCE_TYPE ((obj), QUILL_CACHE_TYPE_CACHE))
#define QUILL_CACHE_IS_CACHE_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), QUILL_CACHE_TYPE_CACHE)
#define QUILL_CACHE_CACHE_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS ((obj), QUILL_CACHE_TYPE_CACHE, QUILLCacheCacheClass))

typedef struct _QUILLCacheCacheClass QUILLCacheCacheClass;
typedef struct _QUILLCacheCache      QUILLCacheCache;

GType    quill_cache_cache_get_type             (void) G_GNUC_CONST;
void     quill_cache_cache_register             (TumblerCachePlugin     *plugin);

GFile   *quill_cache_cache_get_file             (const gchar            *uri,
                                                 TumblerThumbnailFlavor *flavor) G_GNUC_MALLOC G_GNUC_WARN_UNUSED_RESULT;
GFile   *quill_cache_cache_get_temp_file        (const gchar            *uri,
                                                 TumblerThumbnailFlavor  *flavor) G_GNUC_MALLOC G_GNUC_WARN_UNUSED_RESULT;
gboolean quill_cache_cache_read_thumbnail_info  (const gchar            *filename,
                                                 gchar                 **uri,
                                                 guint64                *mtime,
                                                 GCancellable           *cancellable,
                                                 GError                **error);
gboolean quill_cache_cache_write_thumbnail_info (const gchar            *filename,
                                                 const gchar            *uri,
                                                 guint64                 mtime,
                                                 GCancellable           *cancellable,
                                                 GError                **error);
G_END_DECLS;

#endif /* !__QUILL_CACHE_CACHE_H__ */
