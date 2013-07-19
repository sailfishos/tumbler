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

#include <math.h>

#include <glib.h>
#include <glib-object.h>
#include <gio/gio.h>
#include <glib/gi18n.h>

#include <tumbler/tumbler.h>

#include <quill-thumbnailer/quill-thumbnailer.h>

#include <QUrl>
#include <QDir>
#include <QCoreApplication>
#include <QuillImageFilter>
#include <QuillImageFilterFactory>
#include <QCryptographicHash>

static void quill_thumbnailer_create (TumblerAbstractThumbnailer *thumbnailer,
                                      GCancellable               *cancellable,
                                      TumblerFileInfo            *info);
static QCoreApplication *app;

struct _QuillThumbnailerClass
{
  TumblerAbstractThumbnailerClass __parent__;
};

struct _QuillThumbnailer
{
  TumblerAbstractThumbnailer __parent__;
};


G_DEFINE_DYNAMIC_TYPE (QuillThumbnailer, 
                       quill_thumbnailer,
                       TUMBLER_TYPE_ABSTRACT_THUMBNAILER);

void
quill_thumbnailer_register (TumblerProviderPlugin *plugin)
{
  quill_thumbnailer_register_type (G_TYPE_MODULE (plugin));
}


static void
quill_thumbnailer_class_init (QuillThumbnailerClass *klass)
{
  TumblerAbstractThumbnailerClass *abstractthumbnailer_class;
  int argc = 0;
  char *argv[2] = { NULL, NULL };

  app = new QCoreApplication (argc, argv);

  abstractthumbnailer_class = TUMBLER_ABSTRACT_THUMBNAILER_CLASS (klass);
  abstractthumbnailer_class->create = quill_thumbnailer_create;
}



static void
quill_thumbnailer_class_finalize (QuillThumbnailerClass *klass)
{
  // Apparently isn't destructing a QApplication something you should do, as
  // QApplication is designed to work on stack of the main() function.

  // delete app;
}



static void
quill_thumbnailer_init (QuillThumbnailer *thumbnailer)
{

}

static void
on_cancelled (GCancellable *cancellable, gpointer user_data)
{
  // user_data should be a pointer to QuillImageFilter which is currently working
  QuillImageFilter *runningFilter;
  runningFilter = static_cast<QuillImageFilter*>(user_data);
  
  if (runningFilter != 0)
    {
      runningFilter->cancel ();
    }
}

static gboolean
checkImageSize (const QSize  &fullImageSize,
                const gchar*  mime_type)
{
  // Values come from another image application on MeeGo Harmattan
  int imagePixelsLimit = 0;
  const QSize imageSizeLimit = QSize (10000, 10000);

  if (g_strcmp0 (mime_type, "image/svg+xml") == 0) // Vector graphics are always rendered to a fixed size
    return TRUE;

  if (imageSizeLimit.isValid() && (fullImageSize.boundedTo(imageSizeLimit) != fullImageSize))
    return FALSE;

  if (g_strcmp0 (mime_type, "image/jpeg") != 0)
    imagePixelsLimit = 16000000; // nonTiledImagePixelsLimit

  if (imagePixelsLimit == 0)
    imagePixelsLimit = 24000000; // imagePixelsLimit

  if ((imagePixelsLimit > 0) && (fullImageSize.width() * fullImageSize.height() > imagePixelsLimit))
    return FALSE;

  return TRUE;
}

static void
quill_thumbnailer_create (TumblerAbstractThumbnailer *thumbnailer,
                          GCancellable               *cancellable,
                          TumblerFileInfo            *info)
{
  TumblerThumbnailFlavor *flavor;
  TumblerThumbnail       *thumbnail;
  const gchar            *uri;
  GError                 *error = NULL;
  GFile                  *file;
  gchar                  *path;
  gint                    dest_width;
  gint                    dest_height;
  gint                    scale_width;
  gint                    scale_height;
  const gchar            *dirfname;
  gchar                  *dirname;
  QuillImageFilter       *load;
  QuillImageFilter       *save;
  QuillImageFilter       *crop;
  const gchar            *homedir = g_get_home_dir ();
  QString                 home = QString (homedir);
  QString                 final_filename;
  QByteArray              hashValue;
  QuillImage              image;
  QuillImage              blank;
  guint                   signal_id;
  const gchar*            mime_type;
  QSize                   src_size;
  QSize                   dst_size;
  gint                    src_width;
  gint                    src_height;
  gboolean                need_cropping;
  QUrl                    m_url;

  g_return_if_fail (IS_QUILL_THUMBNAILER (thumbnailer));
  g_return_if_fail (cancellable == NULL || G_IS_CANCELLABLE (cancellable));
  g_return_if_fail (TUMBLER_IS_FILE_INFO (info));

  /* create the file info for this URI */
  uri = tumbler_file_info_get_uri (info);

  /* try to load the file information */
  if (!tumbler_file_info_load (info, NULL, &error))
    {
      g_signal_emit_by_name (thumbnailer, "error", uri, error->code, error->message);
      g_error_free (error);
      return;
    }

  if (!tumbler_file_info_needs_update (info))
    {
       g_signal_emit_by_name (thumbnailer, "ready", uri);
       return;
    }

  hashValue = QCryptographicHash::hash (QByteArray (uri), 
                                        QCryptographicHash::Md5);

  /* Get path of original image */
  file = g_file_new_for_uri (uri);
  path = g_file_get_path (file);

  thumbnail = tumbler_file_info_get_thumbnail (info);
  g_assert (thumbnail != NULL);

  /* Get the flavor */
  flavor = tumbler_thumbnail_get_flavor (thumbnail);

  /* Get subdirname for flavor */
  dirfname = tumbler_thumbnail_flavor_get_name (flavor);

  /* Get complete dirname for flavor */
  dirname = g_build_filename (g_get_home_dir (), ".thumbnails", 
                                  dirfname, NULL);

  /* Ensure the destination directory exists */
  if (!g_file_test (dirname, G_FILE_TEST_EXISTS))
    g_mkdir_with_parents (dirname, 0770);


  /* Load original into Quill */

  final_filename = home               + QDir::separator () +
                   ".thumbnails"      + QDir::separator () +
                   QString (dirfname) + QDir::separator () + 
                   hashValue.toHex()  + ".jpeg";

  /* Generate thumbnail using Quill */

  mime_type = tumbler_file_info_get_mime_type (info);

  load = QuillImageFilterFactory::createImageFilter ("org.maemo.load");

  if (load == NULL)
    {
      g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_UNSUPPORTED,
                   _("No thumbnailer available for \"%s\": QUILL failed at createImageFilter (\"org.maemo.load\")"),
                   uri);
      goto had_error;
    }

  if (mime_type != NULL)
    load->setOption (QuillImageFilter::MimeType, QVariant(QString(mime_type)));

  signal_id = g_signal_connect (cancellable, "cancelled",
                                G_CALLBACK (on_cancelled),
                                load);
  m_url = QUrl::fromEncoded(uri);

  load->setOption (QuillImageFilter::FileName, 
                   m_url.toLocalFile());

  // get the size of the original image
  src_size = load->newFullImageSize (QSize());

  if (!checkImageSize (src_size, mime_type))
    {
      g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_UNSUPPORTED,
                   _("No thumbnailer available for \"%s\": this file is too big for QUILL"),
                   uri);
      g_signal_handler_disconnect (cancellable, signal_id);
      delete load;
      goto had_error;
    }

  src_width = src_size.width();
  src_height = src_size.height();
  // calculate width and height for flavor and that particular image
  tumbler_thumbnail_flavor_calculate_size (flavor,
                                           src_width, src_height,
                                           &scale_width, &scale_height,
                                           &need_cropping,
                                           &dest_width, &dest_height);

  blank = QuillImage (QImage (QSize (scale_width, scale_height), QImage::Format_RGB32));
  
  image = load->apply (blank);

  if (image.isNull())
    {
      g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_INVALID_FORMAT,
                   _("No thumbnailer available for \"%s\": QUILL failed at loading file"),
                   uri);
      g_signal_handler_disconnect (cancellable, signal_id);
      delete load;
      goto had_error;
    }

  // do cropping only if needed
  if (need_cropping)
    {
      crop = QuillImageFilterFactory::createImageFilter ("org.maemo.crop");
      if (crop == NULL)
        {
          g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_UNSUPPORTED,
                       _("No thumbnailer available for \"%s\": QUILL failed at createImageFilter (\"org.maemo.crop\")"),
                       uri);
          g_signal_handler_disconnect (cancellable, signal_id);
          delete load;
          goto had_error;
        }

      crop->setOption (QuillImageFilter::CropRectangle,
                       QVariant (QRect ((scale_width - dest_width)/2,
                                        (scale_height - dest_height)/2,
                                         dest_width,
                                         dest_height)));
      image = crop->apply (image);
      if (image.isNull())
        {
          g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_INVALID_FORMAT,
                       _("No thumbnailer available for \"%s\": QUILL failed at cropping thumbnail"),
                       uri);
          g_signal_handler_disconnect (cancellable, signal_id);
          delete load;
          goto had_error;
        }
      delete crop;
    }

  save = QuillImageFilterFactory::createImageFilter ("org.maemo.save");

  if (save == NULL)
    {
      g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_UNSUPPORTED,
                   _("No thumbnailer available for \"%s\": QUILL failed at createImageFilter (\"org.maemo.save\")"),
                   uri);
      g_signal_handler_disconnect (cancellable, signal_id);
      delete load;
      goto had_error;
    }

  save->setOption (QuillImageFilter::FileName, 
                   QVariant (final_filename));

  save->apply (image);

  if (save->error() != QuillImageFilter::NoError)
    {
      g_set_error (&error, TUMBLER_ERROR, TUMBLER_ERROR_UNSUPPORTED,
                   _("Problem with \"%s\": QUILL failed at saving file"),
                   uri);
      g_signal_handler_disconnect (cancellable, signal_id);
      delete load;
      delete save;
      goto had_error;
    }

  delete save;

  g_signal_handler_disconnect (cancellable, signal_id);
  delete load;

  /* Save metainfo about the thumbnail (passing NULL as image-data, as QUILL
   * has stored the thumbnail itself already) */

  tumbler_thumbnail_save_image_data (thumbnail, NULL,
                                     tumbler_file_info_get_mtime (info),
                                     NULL, &error);

had_error:

  /* Cleanup resources */
  g_free (dirname);
  g_object_unref (flavor);
  g_free (path);
  g_object_unref (file);
  g_object_unref (thumbnail);

  if (error != NULL)
    {
      g_signal_emit_by_name (thumbnailer, "error", uri, error->code, error->message);
      g_error_free (error);
    }
  else
    {
      g_signal_emit_by_name (thumbnailer, "ready", uri);
    }
}
