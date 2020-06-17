'''
object persistence routines

:authors: Sascha Lozenz, Jens Gruschel
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import uuid

from app import (app, mongo)
from app.sensors.badgesensor_management import (reset_badgesensor_info_cache)
from app.engine.story_management import (refresh_story_info)
from app.utils.api_responses import (
    json_success_update_insert,
    json_bad_request_error,
    json_forbidden_error,
    json_error_user_already_exists
)

from .authorization_management import (
    refresh_type_access,
    delete_role_info,
    refresh_role_info,
    reset_user_info_cache,
    get_user_info,
    select_type_access_info,
    select_object_access_level,
    ACCESS_WRITABLE
)
from .object_type_management import (
    refresh_object_type
)
from .object_utils import (
    get_time_stamp,
    check_user_exists,
    find_image_and_thumbnail_url
)


log = app.logger


def save_object(item, user_id):

    now = get_time_stamp()
    user_info = get_user_info(user_id) if user_id else None # user ID may not be set when init object API is used

    object_type = item.get('type')
    fields = item['fields'] if 'fields' in item else {}

    if 'id' not in item:

        # check authorization
        if user_info:
            type_access_level, creatable = select_type_access_info(user_info, object_type)
            if not creatable:
                return json_forbidden_error('OPERATION_NOT_ALLOWED', 'user is not allowed to create objects of this type')

        # special checks for user objects
        if object_type == 'user':
            email = fields.get('email')
            if not email:
                return json_bad_request_error('USER_EMAIL_MISSING', 'users require an email to be set')
            if check_user_exists(email):
                return json_error_user_already_exists()

        # adjust and insert object
        adjust_object_for_insert(item, user_id, now)
        result = mongo.db.objects.insert_one(item)
        if result.acknowledged:
            handle_object_change(item)
            access_level = select_object_access_level(user_info, item)
            log.info(f"object with generated ID {item['id']} successfully inserted to database")
            return json_success_update_insert(item, access_level)
        else:
            return json_bad_request_error('INSERT_FAILED', "object could not be saved to database")

    else:

        # check authorization
        if user_info:
            previous_object = mongo.db.objects.find_one({'id': item['id']})
            if previous_object:
                if select_object_access_level(user_info, previous_object) < ACCESS_WRITABLE:
                    return json_forbidden_error('OPERATION_NOT_ALLOWED', 'user is not allowed to modify this object')
            else:
                type_access_level, creatable = select_type_access_info(user_info, object_type)
                if not creatable:
                    return json_forbidden_error('OPERATION_NOT_ALLOWED', 'user is not allowed to create objects of this type')

        # adjust and update object
        adjust_object_for_update(item, user_id, now)
        mongo.db.objects.find_one_and_replace({'id': item['id']}, item, upsert=True)
        log.info(f"object with preset ID {item['id']} successfully inserted to database")
        handle_object_change(item)
        access_level = select_object_access_level(user_info, item)
        return json_success_update_insert(item, access_level)


def adjust_object_for_insert(item, user, timestamp):
    object_id = uuid.uuid4()
    item['id'] = item['type'] + '.' + str.upper(str(object_id))
    adjust_object_for_update(item, user, timestamp)


def adjust_object_for_update(item, user, timestamp):

    # make sure the creation information is never missing
    # (because also objects with predefined ID need this information)
    # and if present use the modification information
    # (which might already be set due to a bug in earlier versions)
    if 'timestamp-created' not in item:
        item['timestamp-created'] = item.get('timestamp-modified') or timestamp
    if 'user-created' not in item:
        item['user-created'] = item.get('user-modified') or user

    # also update the modification information (afterwards!!!)
    item['timestamp-modified'] = timestamp
    item['user-modified'] = user

    # get fields of object
    fields = item.get('fields') or {}

    # TODO: use fields defined in objecttypedefinition for title
    # (title is set by client right now, following code is just a fallback)
    if 'title' not in item:
        if 'title' in fields:
            item['title'] = fields['title']
        elif 'name' in fields:
            item['title'] = fields['name']
        elif 'subject' in fields:
            item['title'] = fields['subject']
        elif 'message' in fields:
            item['title'] = fields['message']

    # set description (if present)
    if 'description' in fields:
        item['description'] = fields['description']

    # make further enhancements
    enhance_object(item)
    set_object_image(item)


def set_object_image(item):

    image_url, thumbnail_url = find_image_and_thumbnail_url(item)

    # set or unset image URL
    if image_url:
        item['imageurl'] = image_url
    elif 'imageurl' in item:
        del item['imageurl']

    # set or unset thumbnail URL
    if thumbnail_url:
        item['thumbnailurl'] = thumbnail_url
    elif 'thumbnailurl' in item:
        del item['thumbnailurl']


def enhance_object(item):

    object_type = item.get('type')

    if object_type == 'mediaitem':

        # delete existing media info
        # (because no media info is better than wrong media info)
        if 'mediainfo' in item:
            del item['mediainfo']

        # embed media info from database
        url = item['fields'].get('url') if 'fields' in item else None
        if url:
            media_info = mongo.db.mediainfo.find_one({'_id': url}, {'_id': False})
            if media_info:
                item['mediainfo'] = media_info


def handle_object_change(item):

    object_type = item.get('type')

    if object_type == 'type':
        # update internal representations of types
        refresh_type_access(item)
        refresh_object_type(item)

    elif object_type == 'role':
        # update internal representation of user roles
        refresh_role_info(item)

    elif object_type == 'user':
        # better reset cache completely
        # (especially important if the email field was changed)
        reset_user_info_cache()

    elif object_type == 'badgesensor':
        # better reset cache completely
        # (especially important if the name field was changed)        
        reset_badgesensor_info_cache()

    elif object_type == 'story':
        # update internal representation of stories
        refresh_story_info(item)


def handle_object_deletion(item):

    object_id = item['id']
    object_type = item.get('type')

    if object_type == 'role':
        # update internal representation of user roles
        delete_role_info(object_id)
