/* vi:set et ai sw=2 sts=2 ts=2: */
/*-
 * Copyright (c) 2009 Jannis Pohlmann <jannis@xfce.org>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 * GNU Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General 
 * Public License along with this library; if not, write to the 
 * Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <glib.h>
#include <glib-object.h>

#include <tumbler/tumbler-thumbnail-flavor.h>



/* property identifiers */
enum
{
  PROP_0,
  PROP_NAME,
  PROP_WIDTH,
  PROP_HEIGHT,
  PROP_MIN_WIDTH,
  PROP_MIN_HEIGHT
};



static void tumbler_thumbnail_flavor_finalize     (GObject      *object);
static void tumbler_thumbnail_flavor_get_property (GObject      *object,
                                                   guint         prop_id,
                                                   GValue       *value,
                                                   GParamSpec   *pspec);
static void tumbler_thumbnail_flavor_set_property (GObject      *object,
                                                   guint         prop_id,
                                                   const GValue *value,
                                                   GParamSpec   *pspec);



struct _TumblerThumbnailFlavorClass
{
  GObjectClass __parent__;
};

struct _TumblerThumbnailFlavor
{
  GObject __parent__;

  gchar  *name;
  gint    width;
  gint    height;
  gint    min_width;
  gint    min_height;
};



G_DEFINE_TYPE (TumblerThumbnailFlavor, tumbler_thumbnail_flavor, G_TYPE_OBJECT)



static void
tumbler_thumbnail_flavor_class_init (TumblerThumbnailFlavorClass *klass)
{
  GObjectClass *gobject_class;

  /* Determine the parent type class */
  tumbler_thumbnail_flavor_parent_class = g_type_class_peek_parent (klass);

  gobject_class = G_OBJECT_CLASS (klass);
  gobject_class->finalize = tumbler_thumbnail_flavor_finalize; 
  gobject_class->get_property = tumbler_thumbnail_flavor_get_property;
  gobject_class->set_property = tumbler_thumbnail_flavor_set_property;

  g_object_class_install_property (gobject_class, PROP_NAME,
                                   g_param_spec_string ("name",
                                                        "name",
                                                        "name",
                                                        NULL,
                                                        G_PARAM_READWRITE |
                                                        G_PARAM_CONSTRUCT_ONLY));

  g_object_class_install_property (gobject_class, PROP_WIDTH,
                                   g_param_spec_int ("width",
                                                     "width",
                                                     "width",
                                                     -1, G_MAXINT, 0,
                                                     G_PARAM_READWRITE |
                                                     G_PARAM_CONSTRUCT_ONLY));

  g_object_class_install_property (gobject_class, PROP_HEIGHT,
                                   g_param_spec_int ("height",
                                                     "height",
                                                     "height",
                                                     -1, G_MAXINT, 0,
                                                     G_PARAM_READWRITE |
                                                     G_PARAM_CONSTRUCT_ONLY));

  g_object_class_install_property (gobject_class, PROP_MIN_WIDTH,
                                   g_param_spec_int ("min_width",
                                                     "min_width",
                                                     "min_width",
                                                     -1, G_MAXINT, 0,
                                                     G_PARAM_READWRITE |
                                                     G_PARAM_CONSTRUCT_ONLY));

  g_object_class_install_property (gobject_class, PROP_MIN_HEIGHT,
                                   g_param_spec_int ("min_height",
                                                     "min_height",
                                                     "min_height",
                                                     -1, G_MAXINT, 0,
                                                     G_PARAM_READWRITE |
                                                     G_PARAM_CONSTRUCT_ONLY));
}



static void
tumbler_thumbnail_flavor_init (TumblerThumbnailFlavor *flavor)
{
}



static void
tumbler_thumbnail_flavor_finalize (GObject *object)
{
  TumblerThumbnailFlavor *flavor = TUMBLER_THUMBNAIL_FLAVOR (object);

  g_free (flavor->name);

  (*G_OBJECT_CLASS (tumbler_thumbnail_flavor_parent_class)->finalize) (object);
}



static void
tumbler_thumbnail_flavor_get_property (GObject    *object,
                                       guint       prop_id,
                                       GValue     *value,
                                       GParamSpec *pspec)
{
  TumblerThumbnailFlavor *flavor = TUMBLER_THUMBNAIL_FLAVOR (object);

  switch (prop_id)
    {
    case PROP_NAME:
      g_value_set_string (value, flavor->name);
      break;
    case PROP_WIDTH:
      g_value_set_int (value, flavor->width);
      break;
    case PROP_HEIGHT:
      g_value_set_int (value, flavor->height);
      break;
    case PROP_MIN_WIDTH:
      g_value_set_int (value, flavor->min_width);
      break;
    case PROP_MIN_HEIGHT:
      g_value_set_int (value, flavor->min_height);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}



static void
tumbler_thumbnail_flavor_set_property (GObject      *object,
                                       guint         prop_id,
                                       const GValue *value,
                                       GParamSpec   *pspec)
{
  TumblerThumbnailFlavor *flavor = TUMBLER_THUMBNAIL_FLAVOR (object);

  switch (prop_id)
    {
    case PROP_NAME:
      flavor->name = g_value_dup_string (value);
      break;
    case PROP_WIDTH:
      flavor->width = g_value_get_int (value);
      break;
    case PROP_HEIGHT:
      flavor->height = g_value_get_int (value);
      break;
    case PROP_MIN_WIDTH:
      flavor->min_width = g_value_get_int (value);
      break;
    case PROP_MIN_HEIGHT:
      flavor->min_height = g_value_get_int (value);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
    }
}



TumblerThumbnailFlavor *
tumbler_thumbnail_flavor_new (const gchar *name,
                              gint         width,
                              gint         height)
{
  g_return_val_if_fail (name != NULL && *name != '\0', NULL);

  return g_object_new (TUMBLER_TYPE_THUMBNAIL_FLAVOR, "name", name, 
                       "width", width, "height", height, NULL);
}

TumblerThumbnailFlavor *
tumbler_thumbnail_flavor_new_with_minimum_size (const gchar *name,
                                                gint         width,
                                                gint         height,
                                                gint         min_width,
                                                gint         min_height)
{
  g_return_val_if_fail (name != NULL && *name != '\0', NULL);

  return g_object_new (TUMBLER_TYPE_THUMBNAIL_FLAVOR, "name", name, 
                       "width", width, "height", height, 
                       "min_width", min_width, "min_height", min_height, NULL);
}

TumblerThumbnailFlavor *
tumbler_thumbnail_flavor_new_normal (void)
{
  return g_object_new (TUMBLER_TYPE_THUMBNAIL_FLAVOR, "name", "normal",
                       "width", 128, "height", 128, NULL);
}



TumblerThumbnailFlavor *
tumbler_thumbnail_flavor_new_large (void)
{
  return g_object_new (TUMBLER_TYPE_THUMBNAIL_FLAVOR, "name", "large",
                       "width", 256, "height", 256, NULL);
}



const gchar *
tumbler_thumbnail_flavor_get_name (TumblerThumbnailFlavor *flavor)
{
  g_return_val_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor), NULL);
  return flavor->name;
}



void
tumbler_thumbnail_flavor_get_size (TumblerThumbnailFlavor *flavor,
                                   gint                   *width,
                                   gint                   *height)
{
  g_return_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor));
  
  if (width != NULL)
    *width = flavor->width;

  if (height != NULL)
    *height = flavor->height;
}

void
tumbler_thumbnail_flavor_get_min_size (TumblerThumbnailFlavor *flavor,
                                       gint                   *width,
                                       gint                   *height)
{
  g_return_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor));
  
  if (width != NULL)
    *width = flavor->min_width;

  if (height != NULL)
    *height = flavor->min_height;
}


/* Calculates desired thumbnail size for particular image and flavor.
   Takes into account width/height and min_width/min_height values of flavor
   and also the size (src_width/src_height parameters) of the source image.
   
   Saves calculated size into scale_width/scale_height variables, and if that
   will require further cropping it will return cropping size in dst_width/
   dst_height variable and return 1 (if scale_width/scale_height are the final
   sizes function returns 0)
*/
void
tumbler_thumbnail_flavor_calculate_size (TumblerThumbnailFlavor *flavor,
                                         gint                    src_width,
                                         gint                    src_height,
                                         gint                   *scale_width,
                                         gint                   *scale_height,
                                         gboolean               *need_cropping,
                                         gint                   *dst_width,
                                         gint                   *dst_height)
{
  /* local, temporary variables */
  gint width = 0;
  gint height = 0;
  gfloat x_factor = 0.0f;
  gfloat y_factor = 0.0f;
  gfloat min_factor = 0.0f;
  gfloat x_min_factor = 0.0f;
  gfloat y_min_factor = 0.0f;
  
  g_return_if_fail (TUMBLER_IS_THUMBNAIL_FLAVOR (flavor));

  /* if in both direction image is smaller than target thumbnail - do nothing.
     Even if min_width/min_height are bigger than that, we are not scaling up */
  if (src_width <= flavor->width && src_height <= flavor->height)
    {
      if (NULL != scale_width)
        *scale_width  = src_width;

      if (NULL != scale_height)
        *scale_height = src_height;

      if (NULL != need_cropping)
	*need_cropping = FALSE;
      return;
    }
  
  /* Calculate factor of scaling in both direction ... */
  x_factor = (float)(flavor->width) / (float)(src_width);
  y_factor = (float)(flavor->height) / (float)(src_height);
  /* .. and then find the smaller factor. */
  min_factor = MIN (x_factor, y_factor);
  
  /* Calculate potential size of scaled image (that will have the same aspect
     ratio as the source image) */
  width  = (int)( min_factor * (float)(src_width) + 0.5f);
  height = (int)( min_factor * (float)(src_height) + 0.5f);
  /* at least 1 pixel in both direction */
  width  = MAX (width,  1);
  height = MAX (height, 1);
  /* ... and if those are bigger than min_width/min_height that is the final,
     target size - after scalling only*/
  if ((width >= flavor->min_width) && (height >= flavor->min_height))
    {
      if (NULL != scale_width)
        *scale_width  = width;

      if (NULL != scale_height)
        *scale_height = height;

      if (NULL != need_cropping)
	*need_cropping = FALSE;
      return;
    }

  /* Below code is executed in case we need cropping */
  /* now we need to find out the size of the image that will meet minimum size
     of the flavor (but remember to keep the aspect ratio of the original).
     Final size will be bigger in one dimension than with/height of flavor - 
     in that one direction we need to cropp the image to meet the destination
     size boundary. */
  x_min_factor = (float)(flavor->min_width) / (float)(src_width);
  y_min_factor = (float)(flavor->min_height) / (float)(src_height);
  min_factor = MAX (x_min_factor, y_min_factor);
  /* BUT! Remember that it cannot be bigger than 1.0!!! We do _NOT_ scale up */
  min_factor = MIN (min_factor, 1.0f);
  /* Calculate potential size of thumbnail (this size will keep aspect ratio
     and will satisfy flavor's min_size conditions) */
  width  = (int)(min_factor * (float)(src_width) + 0.5f);
  height = (int)(min_factor * (float)(src_height) + 0.5f);

  /* save that as a destination size after scalling only */
  if (NULL != scale_width)
    *scale_width  = width;
  
  if (NULL != scale_height)
    *scale_height = height;
  
  /* now we need to calculate the size after cropping scaled image */
  width  = MIN (width,  flavor->width);
  height = MIN (height, flavor->height);

  /* and last modification, no smaller than 1x1 */
  width  = MAX (width,  1);
  height = MAX (height, 1);

  /* save final size of thumbnail - after scalling and cropping */
  if (NULL != dst_width)
    *dst_width  = width;
  
  if (NULL != dst_height)
    *dst_height = height;

  if (NULL != need_cropping)
    *need_cropping = TRUE;
}
