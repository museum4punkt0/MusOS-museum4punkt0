'''
API for administration

:authors: Maurizio Tidei, Jens Gruschel
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import glob, os
import logging
from datetime import (datetime)
from flask import (request, jsonify, send_file)
from pymongo.errors import OperationFailure

from app import (app, socketio, mongo)
from app.utils.api_responses import (json_success, json_success_hint)
from app.cms.object_persistence import (enhance_object, set_object_image)
from app.media.media_processing import (create_media_directories, process_media_file)


log = app.logger


def create_index(collection, name, keys, unique = False):
    try:
        return mongo.db[collection].create_index(keys, name=name, unique=unique)
    except OperationFailure:
        # probably the index already does exist and was modified
        mongo.db[collection].drop_index(name)
        return mongo.db[collection].create_index(keys, name=name, unique=unique)


@app.route('/dbadmin/initdb', methods=['POST'])
def on_post_initdb():
    result = []
    result.append(create_index('objects', 'uniqueid_index', [('id', 1)], True))
    result.append(create_index('objects', 'type_index', [('type', 1), ('title', 1)]))
    result.append(create_index('objects', 'fulltext_index', [('$**', 'text')]))
    result.append(create_index('actionqueue', 'action_time_index', [('time', 1)]))
    result.append(create_index('actionqueue', 'action_targets_index', [('targets', 1), ('time', 1)]))
    result.append(create_index('passwords', 'uniqueid_index', [('userid', 1)], unique=True))
    result.append(create_index('propertyvalues', 'property_index', [('individual', 1), ('property', 1)]))
    return jsonify({'indexes': result})


@app.route('/logging/level/<level>', methods=['GET'])
def on_set_log_level(level):
    log.info("Changing log level to " + level)
    if level.lower() == "info":
        log.setLevel(logging.INFO)
    elif level.lower() == "debug":
        log.setLevel(logging.DEBUG)

    log.info("New log level: " + str(log.level))
    log.debug("debug New log level: " + str(log.level))
    return json_success("log level set to " + level)


@app.route('/logging/get/<int:bytes_hint>', methods=['GET'])
def on_get_logfile(bytes_hint):
    log.info("logfile:" + app.config['LOGFILE_PATH'])
    f = open(app.config['LOGFILE_PATH'], "r")
    result = "".join(f.readlines(bytes_hint))
    f.close()
    return json_success(result)


@app.route('/logging/server.log', methods=['GET'])
def on_get_whole_logfile():
    postfix = request.args.get('postfix', '')
    result = send_file(app.config['LOGFILE_PATH'] + postfix, as_attachment=True, attachment_filename="server.log" + postfix)
    return result


@app.route('/admin/mediainfodatabase/rebuild', methods=['GET'])
def on_get_rebuild_media_info_database():

    create_media_directories()

    media_file_count = 0
    media_item_count = 0

    for input_path in glob.iglob(app.config['UPLOAD_FOLDER'] + "*"):

        file_name = os.path.basename(input_path)
        basename, extension = os.path.splitext(file_name)
        extension = extension[1:].lower()

        process_media_file(file_name, extension)
        media_file_count += 1

    cursor = mongo.db.objects.find({'type': 'mediaitem'}, {'_id': False})
    for item in cursor:
        enhance_object(item)
        mongo.db.objects.find_one_and_replace({'id': item['id']}, item)
        media_item_count += 1

    cursor = mongo.db.objects.find({}, {'_id': False})
    for item in cursor:
        set_object_image(item)
        mongo.db.objects.find_one_and_replace({'id': item['id']}, item)

    return json_success_hint(f"media info database rebuilt successfully, {media_file_count} files analyzed, {media_item_count} media items adjusted")
