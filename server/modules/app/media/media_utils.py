'''
media file utilities for thumbnails

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import glob, os
from PIL import Image

from app import (app)


log = app.logger


UPLOAD_FOLDER = '/var/uploads/'
THUMBNAIL_FOLDER = '/var/media/thumbnails/'
FULLHD_FOLDER = '/var/media/fullhd/'
VIDEO_FRAME_FOLDER = '/var/media/videoframes/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
app.config['FULLHD_FOLDER'] = FULLHD_FOLDER
app.config['VIDEO_FRAME_FOLDER'] = VIDEO_FRAME_FOLDER

IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jpe', 'jfif', 'jif', 'jfi', 'gif', 'svg', 'webp'}
VIDEO_EXTENSIONS = {'mp4', 'webm'}
AUDIO_EXTENSIONS = {'mp3', 'ogg', 'wav'}
OTHER_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | OTHER_EXTENSIONS
# TODO Really restrict extensions?


def make_thumbnail(image, thumbnail_width, thumbnail_height, cover):

    if cover:
        image_width, image_height = image.size
        factor = max(thumbnail_width / image_width, thumbnail_height / image_height)
        thumbnail_size = (round(factor * image_width), round(factor * image_height))

    else:
        thumbnail_size = (thumbnail_width, thumbnail_height)

    image.thumbnail(thumbnail_size)


def generate_thumbnail(image_path, thumbnail_path, thumbnail_width, thumbnail_height, cover):

    try:
        Image.MAX_IMAGE_PIXELS = 30000 * 30000
        image = Image.open(image_path).convert('RGB')
        make_thumbnail(image, thumbnail_width, thumbnail_height, cover)
        image.save(thumbnail_path, "JPEG", quality=95)

    except BaseException as error:
        log.warning(f"{thumbnail_width} x {thumbnail_height} thumbnail creation failed for {image_path}: {error}")
        return False

    except:
        log.error(f"{thumbnail_width} x {thumbnail_height} thumbnail creation failed for {image_path}")
        return False

    else:
        log.info(f"{thumbnail_width} x {thumbnail_height} thumbnail created for {image_path}")
        return True


def generate_folder_thumbnails(input_dir, output_dir, thumbnail_width, thumbnail_height, cover):

    for input_path in glob.iglob(input_dir + "*"):
        base_name = os.path.basename(input_path)
        thumbnail_path = output_dir + base_name + ".jpg"
        generate_thumbnail(input_path, thumbnail_path, thumbnail_width, thumbnail_height, cover)

