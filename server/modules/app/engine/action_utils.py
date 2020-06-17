'''
action processing utilities

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import re

from app import (app, socketio, mongo)
from app.cms.object_utils import (strip_item)
from app.utils.language_utils import (translate)


# predefine regex pattern for placeholders
placeholder_pattern = re.compile('\{([\w.]+)\}')


def create_chat_object(item):
    result = strip_item(item)
    return result


def get_avatar(avatar_id):
    if not avatar_id: return None
    avatar_object = mongo.db.objects.find_one({'id': avatar_id}, {'_id': False})
    if not avatar_object or 'fields' not in avatar_object: return None
    avatar_fields = avatar_object['fields']
    return {
        'id': avatar_id,
        'name': avatar_fields.get('name'),
        'imageurl': avatar_object.get('imageurl')
    }


def complete_subject_text(text, subject_ids, default_value = None):

    # initialize current language and flag to indicate success of all replacements
    language = ''
    successfull = True

    # define actual replacement of a single placeholder as inner function
    # (which needs to access the success flag defined above)
    def replace_single_placeholder(match):

        nonlocal language
        nonlocal successfull

        # extract field name from first group (inside brackets)
        field_name = match.group(1)

        # find subject
        if not subject_ids:
            successfull = False
            return default_value or "?"
        subject_id = subject_ids[0]
        subject = mongo.db.objects.find_one({'id': subject_id}, {'_id': False})
        if not subject:
            successfull = False
            return default_value or "?"

        # find subject field
        if 'fields' not in subject:
            successfull = False
            return default_value or "?"
        fields = subject['fields']
        if field_name not in fields:
            successfull = False
            return default_value or "?"

        # find field value and suffix
        field_value = translate(fields[field_name], language)
        field_suffix = fields.get(field_name + '__suffix')

        # return field value (plus suffix if given)
        return field_value + " " + field_suffix if field_suffix else field_value

    # replace all placeholders with multi language support using the function above
    if isinstance(text, dict):
        result = {}
        for key, value in text.items():
            language = key
            result[key] = placeholder_pattern.sub(replace_single_placeholder, value)
    else:
        result = placeholder_pattern.sub(replace_single_placeholder, text)

    # return result only in case everything is okay
    if successfull or default_value:
        return result
    else:
        return None