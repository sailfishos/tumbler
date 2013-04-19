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

#include <quill-cache/quill-cache-cache.h>
#include <quill-cache/quill-cache-provider.h>



static void   quill_cache_provider_cache_provider_init (TumblerCacheProviderIface *iface);
static GList *quill_cache_provider_get_caches          (TumblerCacheProvider      *provider);



struct _QUILLCacheProviderClass
{
  GObjectClass __parent__;
};

struct _QUILLCacheProvider
{
  GObject __parent__;
};



G_DEFINE_DYNAMIC_TYPE_EXTENDED (QUILLCacheProvider,
                                quill_cache_provider,
                                G_TYPE_OBJECT,
                                0,
                                TUMBLER_ADD_INTERFACE (TUMBLER_TYPE_CACHE_PROVIDER,
                                                       quill_cache_provider_cache_provider_init));



void
quill_cache_provider_register (TumblerProviderPlugin *plugin)
{
  quill_cache_provider_register_type (G_TYPE_MODULE (plugin));
}



static void
quill_cache_provider_class_init (QUILLCacheProviderClass *klass)
{
  GObjectClass *gobject_class;

  /* Determine the parent type class */
  quill_cache_provider_parent_class = g_type_class_peek_parent (klass);

  gobject_class = G_OBJECT_CLASS (klass);
}



static void
quill_cache_provider_class_finalize (QUILLCacheProviderClass *klass)
{
}



static void
quill_cache_provider_cache_provider_init (TumblerCacheProviderIface *iface)
{
  iface->get_caches = quill_cache_provider_get_caches;
}



static void
quill_cache_provider_init (QUILLCacheProvider *provider)
{
}



static GList *
quill_cache_provider_get_caches (TumblerCacheProvider *provider)
{
  QUILLCacheCache *cache;
  GList         *caches = NULL;

  g_return_val_if_fail (QUILL_CACHE_IS_PROVIDER (provider), NULL);

  cache = g_object_new (QUILL_CACHE_TYPE_CACHE, NULL);
  caches = g_list_append (caches, cache);

  return caches;
}
