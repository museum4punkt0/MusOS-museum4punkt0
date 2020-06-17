'''
API for object commands

:authors: Sascha Lozenz, Jens Gruschel, Maurizio Tidei
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import traceback
from flask import (request, jsonify)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from app import (app, mongo, flask_bcrypt)
from app.cms.authorization_management import (
    get_user_info,
    select_object_access_level,
    select_fieldset_access_levels,
    ACCESS_READONLY
)
from app.cms.object_persistence import (
    save_object,
    handle_object_change,
    handle_object_deletion
)
from app.cms.object_utils import (
    get_time_stamp,
    is_image_url
)
from app.utils.api_utils import (get_field_time_seconds)
from app.utils.api_responses import (
    json_success, json_success_update_insert, json_success_delete,
    json_bad_request_error, json_authorization_error, json_forbidden_error,
    json_not_found_error, json_not_acceptable_error,
    json_error_no_record_found, json_error_wrong_parameters,
    json_error_user_already_exists, json_error_database_access_failed
)


log = app.logger


@app.route('/object', methods=['PUT'])
@jwt_required
def on_put_object():

    user_id = get_jwt_identity()
    if not user_id:
        return json_authorization_error('USER_AUTHENTICATION_REQUIRED', "user authentication required")

    item = request.get_json()
    log.info(f"saving object {item}")

    # actuall save object
    return save_object(item, user_id)


# TODO: add simple auth to this service
@app.route('/init/object', methods=['PUT'])
def on_put_init_object():

    item = request.get_json()

    # preserve existing object if desired
    if item.get('__preserve') == True:
        preserve_id = item.get('id')
        if not preserve_id:
            return "object without ID cannot be preserved\n", 400
        existing_object = mongo.db.objects.find_one({"id": preserve_id})
        if existing_object:
            return f"object with ID {preserve_id} already existing, preserved\n", 200
        del item['__preserve']
    else:
        # mark object as created automatically
        item['autocreated'] = True


    # automatically created users also need a password hash,
    # using a password, which is passed as a field and removed afterwards
    if item.get('type') == 'user' and 'fields' in item:
        user_id = item['fields'].get('email')
        password = item['fields'].get('password')
        if user_id and password:
            passwordhash = flask_bcrypt.generate_password_hash(password).decode()
            del item['fields']['password']
            mongo.db.passwords.replace_one(
                {'userid': user_id},
                {'userid': user_id, 'passwordhash': passwordhash},
                upsert=True
            )

    # save object and return a text message instead of a JSON result
    json, code = save_object(item, get_jwt_identity())
    if code == 200:
        return "OK\n", 200
    else:
        return (json.get('message') or "error saving object") + "\n", code or 500


@app.route('/object/<id>', methods=['GET'])
@jwt_required
def on_get_object(id):

    current_user_id = get_jwt_identity()
    user_info = get_user_info(current_user_id)

    item = mongo.db.objects.find_one({'id': id}, {'_id': False})

    if not item:
        return json_not_found_error('OBJECT_NOT_FOUND', 'object not found')

    access_level = select_object_access_level(user_info, item)
    if access_level < ACCESS_READONLY:
        return json_not_found_error('OBJECT_NOT_FOUND', 'object not found')

    # enhancement is done when saving objects,
    # but in order to get up to date values
    # maybe it should be done here, too ???
    # enhance_object(item)

    response = {
        'data': item,
        'accesslevel': access_level,
        'fieldsetaccesslevels': select_fieldset_access_levels(user_info, item['type'], access_level)
    }
    return jsonify(response), 200


# this method is not used right now, maybe change the signature
# and make sure there are no conflicts with other APIs
# (and maybe make a backup or create an history entry)
@app.route('/object/<id>', methods=['DELETE'])
@jwt_required
def on_delete_object(id):

    if id is None:
        return json_error_wrong_parameters()

    item = mongo.db.objects.find_one_and_delete({'id': id})
    if not item:
        return json_error_no_record_found()

    handle_object_deletion(item)
    return json_success_delete()


@app.route('/recycle/object/<id>', methods=['PUT'])
@jwt_required
def on_put_recycle_object(id):

    if id is None:
        return json_error_wrong_parameters()

    item = mongo.db.objects.find_one_and_update(
        {'id': id},
        {'$set': {'timestamp-deleted': get_time_stamp(), 'user-deleted': get_jwt_identity()}}
    )
    if not item:
        return json_error_no_record_found()

    handle_object_deletion(item)
    return json_success_delete()


@app.route('/recycle/object/<id>', methods=['GET'])
@jwt_required
def on_get_recycle_object(id):

    if id is None:
        return json_error_wrong_parameters()

    # undelete item
    item = mongo.db.objects.find_one_and_update({'id': id}, {'$unset': {'timestamp-deleted': '', 'user-deleted': ''}})
    if not item:
        return json_error_no_record_found()

    # signal success
    handle_object_change(item)
    return json_success('Object successfully restored.')


@app.route('/config', methods=['GET'])
def on_get_config():

    # execute query
    try:
        item = mongo.db.objects.find_one({"id": "configuration.active"}, {'_id': False})
    except:
        log.error(f"database access failed for {request.url}")
        log.error(traceback.format_exc())
        return json_error_database_access_failed()

    response = {'items': [item]}
    return jsonify(response), 200


@app.route('/objectquery', methods=['POST'])
@jwt_required
def on_post_objectquery():
    """return objects plus additional information (access levels and reference counters)"""

    current_user_id = get_jwt_identity()
    user_info = get_user_info(current_user_id)
    query = request.get_json()

    # execute query
    try:
        cursor = mongo.db.objects.find(query, {'_id': False})
    except:
        log.error(f"database access failed for {request.url}")
        log.error(traceback.format_exc())
        return json_error_database_access_failed()

    # filter objects visible for the current user
    items = [item for item in cursor if select_object_access_level(user_info, item) >= ACCESS_READONLY]

    # also provide access levels and references of these items
    access = {item['id']: select_object_access_level(user_info, item) for item in items}

    response = {'items': items, 'accesslevels': access}
    return jsonify(response), 200


@app.route('/typelist', methods=['GET'])
@jwt_required
def on_get_typelist():

    query = {"type": "type"}

    try:
        cursor = mongo.db.objects.find(query, {'_id': False})
    except:
        log.error(f"database access failed for {request.url}")
        log.error(traceback.format_exc())
        return json_error_database_access_failed()

    # only pass information required for type
    items = [{
        'id': item['id'],
        'type': item['type'],
        'title': item.get('title'),
        'fields': item.get('fields')
    } for item in cursor]

    return jsonify(items), 200
