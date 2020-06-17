'''
API for login and user management

:authors: Sascha Lorenz, Jens Gruschel
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import os
from flask import (request, jsonify)
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, jwt_refresh_token_required, get_jwt_identity
)

from app import (app, mongo, flask_bcrypt, jwt)
from app.cms.user_utils import (find_user)
from app.utils.api_responses import (
    json_success, json_login_error, json_bad_request_error,
    json_internal_server_error, json_authorization_error,
    json_not_found_error, json_forbidden_error
)


log = app.logger


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return json_authorization_error('MISSING_AUTHORIZATION', 'authorization header missing')


@app.route('/login', methods=['POST'])
def on_post_login():

    # parse data
    data = request.get_json()
    if not 'user' in data:
        return json_bad_request_error('USER_MISSING', 'user ID missing')
    user_id = data['user']

    # find user
    user = find_user(user_id)
    if not user or not 'fields' in user:
        return json_login_error()

    # find password hash
    password_hash = find_user_password_hash(user_id)
    if not password_hash:
        return json_login_error()

    # check password and login if correct
    if check_password(password_hash, data['password']):
        if 'password' in user['fields']:
            del user['fields']['password']
        access_token = create_access_token(identity=data['user'])
        response = {
            'accessToken': access_token
        }
        return jsonify(response), 200
    else:
        return json_authorization_error('INVALID_LOGIN', 'invalid username or password')


@app.route('/resetuserpassword', methods=['POST'])
@jwt_required
def on_post_reset_user_password():

    # check current user
    current_user_id = get_jwt_identity()
    current_user_roles = find_user_roles(current_user_id)
    if not roles_have_flag(current_user_roles, 'resetOtherUsers'):
        return json_forbidden_error('LEGITIMATION_ERROR', 'legitimation failed')

    # parse data
    data = request.get_json()
    if not 'userid' in data:
        return json_bad_request_error('USER_MISSING', 'user ID missing')
    if not 'password' in data:
        return json_bad_request_error('PASSWORD_MISSING', 'password missing')
    user_id = data['userid']
    password = data['password']

    # check if user exists
    user = find_user(user_id)
    if not user:
        return json_not_found_error('USER_NOT_FOUND', 'user not found')

    # change password
    password_hash = hash_password(password)
    result = mongo.db.passwords.replace_one({'userid': user_id}, {'userid': user_id, 'passwordhash': password_hash}, upsert=True)
    if result.acknowledged:
        return json_success('password reset')
    else:
        return json_internal_server_error('OPERATION_FAILED', 'could not reset password')


@app.route('/changeownpassword', methods=['POST'])
@jwt_required
def on_post_change_own_password():

    # check current user
    user_id = get_jwt_identity()
    user = find_user(user_id)
    if not user:
        return json_not_found_error('USER_NOT_FOUND', 'user not found')

    # parse data
    data = request.get_json()
    if not 'oldpassword' in data or not 'newpassword' in data:
        return json_bad_request_error('PASSWORD_MISSING', 'password missing')
    old_password = data['oldpassword']
    new_password = data['newpassword']

    # make sure old password is correct
    existing_password_hash = find_user_password_hash(user_id)
    if not existing_password_hash:
        return json_internal_server_error('OPERATION_FAILED', 'password not existing')
    elif not check_password(existing_password_hash, old_password):
        return json_authorization_error('INVALID_PASSWORD', 'invalid password')

    # test password
    if not is_password_valid(new_password):
        return json_bad_request_error('INVALID_PASSWORD', 'password must be at least 8 characters long')

    # change password
    password_hash = hash_password(new_password)
    result = mongo.db.passwords.replace_one({'userid': user_id}, {'userid': user_id, 'passwordhash': password_hash}, upsert=True)
    if result.acknowledged:
        return json_success('password changed')
    else:
        return json_internal_server_error('OPERATION_FAILED', 'could not change password')


def find_user_password_hash(user_id):
    data = mongo.db.passwords.find_one({'userid': user_id}, {"_id": False})
    if not data or 'passwordhash' not in data:
        log.warning(f"user {user_id} not found")
        return None
    return data['passwordhash']
    

def find_user_roles(user_id):
    user = find_user(user_id)
    if not user or not 'fields' in user or not 'roles' in user['fields']:
        return []
    role_ids = user['fields']['roles']
    if not role_ids:
        return []
    role_cursor = mongo.db.objects.find({'type': 'role', 'id': {'$in': role_ids}}, {"_id": False})
    return [role for role in role_cursor]


def roles_have_flag(roles, field_name):
    for role in roles:
        if 'fields' in role and field_name in role['fields']:
            if role['fields'][field_name]:
                return True
    return False


def is_password_valid(password):
    return len(password) >= 8


def hash_password(password):
    return flask_bcrypt.generate_password_hash(password).decode()


def check_password(hash, password):
    return flask_bcrypt.check_password_hash(hash, password)