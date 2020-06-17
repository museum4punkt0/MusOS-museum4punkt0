'''
user authorization management routines

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from app import (app, mongo)

from .user_utils import (find_user)


log = app.logger


ACCESS_UNDEFINED   = 0
ACCESS_HIDDEN      = 1
ACCESS_READONLY    = 2
ACCESS_WRITABLE    = 3

NO_ROLE_INFO = {'accesslevel': ACCESS_HIDDEN}
NO_USER_INFO = {'id': None, 'roles': set(), 'accesslevel': ACCESS_HIDDEN}

PRIVILEGE_FIELD_NAMES = [
    "changeOwnPassword",
    "resetOtherUsers"
]


type_access_map = {}
role_info_map = {}
user_info_cache = {}


def get_accessibility_level(accessibility):

    if accessibility == "hidden": return ACCESS_HIDDEN
    if accessibility == "readonly": return ACCESS_READONLY
    return ACCESS_WRITABLE # default is writable (especially if not specified at all)


def refresh_type_access(type_object):

    global type_access_map

    # get type id and type access fields
    type_fields = type_object['fields']
    type_id = type_fields['id']
    type_definition = type_fields.get('definition') or {}
    type_fieldsets = type_definition.get('fieldsets') or []
    type_access = type_fields.get('typeaccess') or []
    type_access_fields = (type_access[0].get('fields') or {}) if len(type_access) > 0 else {}
    type_access_fields['creatableFor'] = type_fields.get('creatableFor') or []
    type_access_fields['deleted'] = bool(type_object.get('timestamp-deleted'))
    type_access_fields['fieldsetaccess'] = {fieldset['id']: fieldset['access'] for fieldset in type_fieldsets if 'access' in fieldset}

    # refresh map
    type_access_map[type_id] = type_access_fields


def refresh_type_access_map():

    global type_access_map

    type_access_map = {}

    cursor = mongo.db.objects.find({'type': 'type'}, {'_id': False})
    for type_object in cursor:
        refresh_type_access(type_object)


def get_type_access(type_id):
    global type_access_map
    return type_access_map.get(type_id) or {}


def create_role_info(role):

    if 'fields' not in role:
        return NO_ROLE_INFO

    fields = role['fields']
    if 'defaultaccessibility' in fields:
        accessibility = fields['defaultaccessibility']
        access_level = get_accessibility_level(accessibility)
    else:
        access_level = ACCESS_HIDDEN

    privileges = set([field_name for field_name in PRIVILEGE_FIELD_NAMES if fields.get(field_name)])

    return {'accesslevel': access_level, 'privileges': privileges}


def delete_role_info(role_id):

    global role_info_map

    if role_id in role_info_map:
        del role_info_map[role_id]


def refresh_role_info(role):

    global role_info_map

    role_id = role['id']
    role_info_map[role_id] = create_role_info(role)


def refresh_role_info_map():

    global role_info_map

    role_info_map = {}
    user_info_cache = {}

    cursor = mongo.db.objects.find({'type': 'role'}, {'_id': False})
    for role in cursor:
        refresh_role_info(role)


def create_user_info(user):

    if 'fields' not in user or not user['fields'].get('roles'):
        return NO_USER_INFO

    user_fields = user['fields']
    user_id = user_fields.get('email')
    user_name = user_fields.get('name')
    role_ids = set(user_fields.get('roles')) | {'role.any'}

    user_access_level = ACCESS_HIDDEN
    user_privileges = set()

    for role_id in role_ids:
        role_info = role_info_map.get(role_id) or {}

        # compute access level
        role_access_level = role_info.get('accesslevel') or ACCESS_HIDDEN
        if role_access_level > user_access_level:
            user_access_level = role_access_level

        # compute privileges
        role_privieges = role_info.get('privileges') or set()
        user_privileges |= role_privieges

    return {'id': user_id, 'name': user_name, 'roles': role_ids, 'accesslevel': user_access_level, 'privileges': user_privileges}


def reset_user_info_cache():

    global user_info_cache
    user_info_cache = {}


def get_user_info(user_id):

    global user_info_cache

    if user_id in user_info_cache:
        return user_info_cache[user_id]

    user = find_user(user_id)
    if not user:
        return NO_USER_INFO

    user_info = create_user_info(user)
    user_info_cache[user_id] = user_info
    
    return user_info


def select_user_membership(user_info, roles):

    if not roles: return []
    user_roles = user_info['roles']
    return [role for role in roles if role in user_roles]


def get_access_level(user_info, access, basic_access_level):

    if not access: return basic_access_level

    access_level = get_accessibility_level(access.get('accessibility'))
    
    # compute total level
    total_level = min(basic_access_level, access_level)

    # grant write access if explicitly given for user role (or level already reached)
    if total_level >= ACCESS_WRITABLE: return total_level
    if select_user_membership(user_info, access.get('writableFor')): return ACCESS_WRITABLE

    # grant read access if explicitly given for user role (or level already reached)
    if total_level >= ACCESS_READONLY: return total_level
    if select_user_membership(user_info, access.get('readableFor')): return ACCESS_READONLY

    # return level computed earlier
    return total_level


def select_type_access_level(user_info, type_id):

    if not user_info: return ACCESS_HIDDEN

    type_access = get_type_access(type_id)
    type_access_level = get_access_level(user_info, type_access, user_info['accesslevel'])
    return type_access_level


def select_type_access_info(user_info, type_id):

    if not user_info: return ACCESS_HIDDEN, False
    type_access = get_type_access(type_id)
    existing = not type_access.get('deleted')
    type_access_level = get_access_level(user_info, type_access, user_info['accesslevel'])
    creatable = type_access_level >= ACCESS_WRITABLE or bool(select_user_membership(user_info, type_access.get('creatableFor')))
    return type_access_level, existing and creatable


def select_object_access_level(user_info, item):

    if not user_info: return ACCESS_HIDDEN
    if not item: return ACCESS_HIDDEN

    # grant full access to the owner (creator) of an object
    owner = item.get('user-created')
    if owner and owner == user_info['id']: return ACCESS_WRITABLE

    # compute access level for the object type
    type_access_level = select_type_access_level(user_info, item.get('type'))

    # compute access level for the concrete object instance (if defined)
    if 'objectaccess' in item and item['objectaccess'].get('accessibility'):
        object_access_level = get_access_level(user_info, item['objectaccess'], type_access_level)
        return object_access_level
    else:
        return type_access_level


def select_fieldset_access_levels(user_info, type_id, object_access_level):

    if not user_info: return {}
    if not type_id: return {}

    type_access = get_type_access(type_id)
    fieldset_access = type_access['fieldsetaccess']
    return {key: get_access_level(user_info, access, object_access_level) for (key, access) in fieldset_access.items()}
