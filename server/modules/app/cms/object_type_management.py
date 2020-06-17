'''
object type management routines

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from app import (app, mongo)


log = app.logger


reference_type_field_map = {}
element_type_field_map = {}
medialist_type_field_map = {}


def get_reference_fields(type_id):
    global reference_type_field_map
    return reference_type_field_map.get(type_id) or []


def get_element_fields(type_id):
    global element_type_field_map
    return element_type_field_map.get(type_id) or []


def get_medialist_fields(type_id):
    global medialist_type_field_map
    return medialist_type_field_map.get(type_id) or []


def extract_fields(field_sets):
    result = []
    for field_set in field_sets:
        result.extend(field_set.get('fields') or [])
        sub_field_sets = field_set.get('fieldsets') or []
        if sub_field_sets:
            result.extend(extract_fields(sub_field_sets))
    return result


def refresh_object_type(type_object):

    global reference_type_field_map
    global element_type_field_map
    global medialist_type_field_map

    # get type id and definition
    type_fields = type_object['fields']
    type_id = type_fields['id']
    type_definition = type_fields.get('definition') or {}

    # find all fields of this type
    field_sets = type_definition.get('fieldsets') or []
    fields = extract_fields(field_sets)

    # find fields with references or elements
    reference_type_field_map[type_id] = [field.get('id') for field in fields if field.get('type') in ['reference', 'medialist']]
    element_type_field_map[type_id] = [field.get('id') for field in fields if field.get('type') == 'element']
    medialist_type_field_map[type_id] = [field.get('id') for field in fields if field.get('type') == 'medialist']


def refresh_all_object_types():

    global reference_type_field_map
    global element_type_field_map
    global medialist_type_field_map

    reference_type_field_map = {}
    element_type_field_map = {}
    medialist_type_field_map = {}

    cursor = mongo.db.objects.find({'type': 'type'}, {'_id': False})
    for type_object in cursor:
        refresh_object_type(type_object)


