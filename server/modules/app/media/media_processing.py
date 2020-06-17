'''
media file processing and meta data extraction

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import glob, os
import cv2
import mutagen
import traceback
import statistics
from flask import (url_for)
from PIL import Image

from app import (app, mongo)

from .media_utils import (
    VIDEO_EXTENSIONS,
    AUDIO_EXTENSIONS,
    IMAGE_EXTENSIONS,
    generate_thumbnail,
    generate_folder_thumbnails
)


log = app.logger


THUMBNAIL_WIDTH = 315
THUMBNAIL_HEIGHT = 200

FULLHD_WIDTH = 1920 # assume height = width (for portrait mode)


def make_jpeg_extension(path):
    lower_path = path.lower()
    if path.endswith(".jpg"): return path
    if path.endswith(".jpeg"): return path
    if path.endswith(".jpe"): return path
    return path + ".jpg"


def generate_thumbnail_folder():
    generate_folder_thumbnails(
        app.config['UPLOAD_FOLDER'],
        app.config['THUMBNAIL_FOLDER'],
        THUMBNAIL_WIDTH,
        THUMBNAIL_HEIGHT,
        True # at least 315x200 (for covering, cutting off sides)
    )


def generate_fullhd_folder():
    generate_folder_thumbnails(
        app.config['UPLOAD_FOLDER'],
        app.config['FULLHD_FOLDER'],
        FULLHD_WIDTH,
        FULLHD_WIDTH,
        False # not more than 1920x1920 (usually 1920x1080 or 1080x1920 or similar)
    )


def create_media_directories():

    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)
    os.makedirs(app.config['FULLHD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VIDEO_FRAME_FOLDER'], exist_ok=True)


def process_media_file(file_name, extension):

    try:

        if extension in ['svg']:
            # SVG files are not supported yet
            media_info = None

        elif extension in VIDEO_EXTENSIONS:
            media_info = process_video(file_name)

        elif extension in AUDIO_EXTENSIONS:
            media_info = process_audio(file_name)

        else:
            media_info = process_image(file_name)

        # save meta info to database
        log.info(f"updating info for media file {file_name}: {media_info}")
        file_url = url_for('on_get_uploaded_file', filename=file_name)
        if media_info:
            mongo.db.mediainfo.find_one_and_replace({'_id': file_url}, media_info, upsert=True)
        else:
            mongo.db.mediainfo.remove({'_id': file_url})

        # return URL plus media info
        return {
            'url': file_url,
            'info': media_info
        }

    except:
        log.error(f"error processing media file {file_name}")
        log.error(traceback.format_exc())


def process_image(file_name):

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file_stat = os.stat(file_path)

        Image.MAX_IMAGE_PIXELS = 30000 * 30000
        image = Image.open(file_path)
        image_width, image_height = image.size

        # generate thumbnail
        thumbnail_name = make_jpeg_extension(file_name)
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_name)
        if generate_thumbnail(file_path, thumbnail_path, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, True):
            thumbnail_url = url_for('on_get_thumbnail_file', filename=thumbnail_name)
        else:
            thumbnail_url = None

        # generate Full HD version (for mobile devices)
        fullhd_name = make_jpeg_extension(file_name)
        fullhd_path = os.path.join(app.config['FULLHD_FOLDER'], fullhd_name)
        if generate_thumbnail(file_path, fullhd_path, FULLHD_WIDTH, FULLHD_WIDTH, False):
            fullhd_url = url_for('on_get_fullhd_file', filename=fullhd_name)
        else:
            fullhd_url = None

        return {
            'type': 'image',
            'width': image_width,
            'height': image_height,
            'thumbnail': thumbnail_url,
            'fullhd': fullhd_url,
            'filesize': file_stat.st_size
        }

    except:
        log.error(f"image processing failed for {file_name}")
        log.error(traceback.format_exc())
        return None


def process_video(file_name):

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file_stat = os.stat(file_path)

        capture = cv2.VideoCapture(file_path)
        if not capture.isOpened():
            return None

        # get video dimensions
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        if isinstance(width, float): width = int(round(width))
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if isinstance(height, float): height = int(round(height))

        # get video duration
        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps <= 0 or frame_count <= 0:
            capture.release()
            return None
        duration_seconds = frame_count / fps

        # compute full hd frame size (downscaling the larger side to 1920)
        factor = max(min(1920 / width, 1920 / height), 1.0)
        full_hd_size = (round(factor * width), round(factor * height))

        # initialize frame variables
        frame_paths = []
        frame_urls = []

        # the very beginning and the very end might not be very interesting (black etc.),
        # so let's take some frames from 0% to 95%
        ratios = range(0, 100, 5)
        for ratio in ratios:
            msecs = int(duration_seconds * ratio * 10.0)
            capture.set(cv2.CAP_PROP_POS_MSEC, msecs)

            # extract single frame
            success, frame_image = capture.read()

            if not success:
                # return video properties without frames
                log.warning(f"frame selection of {file_name} failed at {msecs} msecs ({ratio}%)")
                capture.release()
                return {
                    'type': 'video',
                    'width': width,
                    'height': height,
                    'duration': round(duration_seconds, 3),
                    'filesize': file_stat.st_size
                }

            # scale and save image
            scaled_image = cv2.resize(frame_image, full_hd_size)
            frame_name = file_name + '.' + str(ratio) + '.jpg'
            frame_path = os.path.join(app.config['VIDEO_FRAME_FOLDER'], frame_name)
            frame_url = url_for('on_get_videoframe_file', filename=frame_name)
            cv2.imwrite(frame_path, scaled_image)
            frame_paths.append(frame_path)
            frame_urls.append(frame_url)

        # finish capturing frames (we)
        capture.release()

        suggested_index = len(frame_paths) // 2
        suggested_frame_path = frame_paths[suggested_index]
        suggested_frame_url = frame_urls[suggested_index]

        # generate thumbnail from frame
        thumbnail_name = make_jpeg_extension(file_name)
        thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_name)
        if generate_thumbnail(suggested_frame_path, thumbnail_path, THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, True):
            thumbnail_url = url_for('on_get_thumbnail_file', filename=thumbnail_name)
        else:
            thumbnail_url = None

        return {
            'type': 'video',
            'width': width,
            'height': height,
            'duration': round(duration_seconds, 3),
            'frames': frame_urls,
            'suggestedFrame': suggested_frame_url,
            'thumbnail': thumbnail_url,
            'filesize': file_stat.st_size
        }

    except:
        log.error(f"video processing failed for {file_name}")
        log.error(traceback.format_exc())
        return None


def process_audio(file_name):

    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file_stat = os.stat(file_path)

        media_file = mutagen.File(file_path)
        if not media_file: return None
        duration_seconds = media_file.info.length
        return {
            'type': 'audio',
            'duration': round(duration_seconds, 3),
            'filesize': file_stat.st_size
        }

    except:
        log.error(f"audio processing failed for {file_name}")
        log.error(traceback.format_exc())
        return None

