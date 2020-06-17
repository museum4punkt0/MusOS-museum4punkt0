'''
API for media commands

:authors: Maurizio Tidei, Jens Gruschel
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import glob, os
import hashlib
import re
from flask import (request, jsonify, url_for, send_from_directory)
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from werkzeug.utils import secure_filename
from PIL import Image

from app import (app, mongo)
from app.media.media_utils import (ALLOWED_EXTENSIONS)
from app.media.media_processing import (process_media_file, create_media_directories)
from app.utils.api_responses import (json_success, json_bad_request_error)


log = app.logger


NO_FILE_EXISTS = 0
SAME_FILE_EXISTS = 1
OTHER_FILE_EXISTS = 2


# predefine regex pattern for filename counters (underscore and number directly before file extension)
filename_counter_pattern = re.compile('_([0-9]+)$')


@app.route('/upload/media', methods=['POST'])
@jwt_required
def on_post_upload_media():

    # check if the post request has the file part
    if 'file' not in request.files:
        return json_bad_request_error('NO_FILE_SELECTED', 'no file selected')

    uploaded_file = request.files['file']
    # if user does not select a file, the browser also submits an empty part without filename
    if uploaded_file.filename == '':
        return json_bad_request_error('FILE_NAME_MISSING', 'file name missing')

    basename, extension = os.path.splitext(uploaded_file.filename)

    if not extension:
        return json_bad_request_error('FILE_EXTENSION_NOT_SUPPORTED', 'file extension not supported: ' + uploaded_file.filename)

    extension = extension[1:].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return json_bad_request_error('FILE_EXTENSION_NOT_SUPPORTED', 'file extension not supported: ' + uploaded_file.filename)

    # save file
    file_name = save_file(uploaded_file)

    # process file and pass URLs and meta info
    response = process_media_file(file_name, extension)
    return jsonify(response), 200


def save_file(uploaded_file):

    file_name = secure_filename(uploaded_file.filename)
    while True:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        existing_file = check_existing_file(file_path, uploaded_file)
        if existing_file == OTHER_FILE_EXISTS:
            # try another file name
            file_name = find_alternative_filename(file_name)
        elif existing_file == SAME_FILE_EXISTS:
            # just continue (no need to save the same file again)
            return file_name
        else:
            # save file
            uploaded_file.save(file_path)
            return file_name


def check_existing_file(filepath, uploaded_file):

    if not os.path.exists(filepath): return NO_FILE_EXISTS

    with open(filepath, 'rb') as existing_file:
        existing_hash = generate_hash(existing_file)

    uploaded_hash = generate_hash(uploaded_file)
    uploaded_file.seek(0)

    if existing_hash == uploaded_hash:
        log.info(f"file {filepath} with same hash already exists: {existing_hash}")
        return SAME_FILE_EXISTS
    else:
        log.info(f"file {filepath} with other hash already exists: {existing_hash} instead of uploaded {uploaded_hash}")
        return OTHER_FILE_EXISTS


def generate_hash(stream):
    BUF_SIZE = 1048576 # 1 MB
    result = hashlib.sha256()
    while True:
        data = stream.read(BUF_SIZE)
        if not data:
            return result.hexdigest()
        result.update(data)


def find_alternative_filename(filename):
    name, extension = os.path.splitext(filename)
    counter_match = filename_counter_pattern.search(name)

    # in case there is no counter yet, insert a new one
    if not counter_match:
        return name + "_2" + extension

    # otherwise replace the counter
    counter = int(counter_match[1]) + 1
    counter_start = counter_match.start(1)
    counter_end = counter_match.end(1)
    return name[:counter_start] + str(counter) + name[counter_end:] + extension


@app.route('/uploads/<filename>', methods=['GET'])
def on_get_uploaded_file(filename):
    log.info("serving upload file " + filename + " from " + app.config['UPLOAD_FOLDER'])
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/thumbnails/<filename>', methods=['GET'])
def on_get_thumbnail_file(filename):
    log.info("serving thumbnail file " + filename + " from " + app.config['THUMBNAIL_FOLDER'])
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)


@app.route('/fullhd/<filename>', methods=['GET'])
def on_get_fullhd_file(filename):
    log.info("serving FullHD file " + filename + " from " + app.config['FULLHD_FOLDER'])
    return send_from_directory(app.config['FULLHD_FOLDER'], filename)

@app.route('/videoframes/<filename>', methods=['GET'])
def on_get_videoframe_file(filename):
    log.info("serving video frame file " + filename + " from " + app.config['VIDEO_FRAME_FOLDER'])
    return send_from_directory(app.config['VIDEO_FRAME_FOLDER'], filename)
