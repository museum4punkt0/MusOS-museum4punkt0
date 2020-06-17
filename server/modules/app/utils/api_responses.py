'''
global response declarations for rest APIs

:authors: Sascha Lorenz, Jens Gruschel
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from flask import jsonify


# success responses

def json_success(message = ""):
    return jsonify({'message': message}), 200


def json_success_update_insert(data, access_level):
    if '_id' in data: del data['_id']
    response = {
        'message': 'Object successfully created / updated.',
        'data': data,
        'accesslevel': access_level
    }
    return jsonify(response), 200


def json_success_hint(message = ""):
    # hints should be shown visually to the user
    return jsonify({'level': 'hint', 'message': message}), 200


def json_success_warning(message = ""):
    # warnings should be shown visually to the user
    return jsonify({'level': 'warning', 'message': message}), 200

def json_success_delete():
    return json_success('Object successfully deleted.')


# general error responses

def json_error(id, message, http_code):
    return jsonify({'error_id': id, 'message': message}), http_code


def json_bad_request_error(id, message):
    return json_error(id, message, 400)


def json_authorization_error(id, message):
    return json_error(id, message, 401)


def json_forbidden_error(id, message):
    return json_error(id, message, 403)


def json_not_found_error(id, message):
    return json_error(id, message, 404)


def json_not_acceptable_error(id, message):
    return json_error(id, message, 406)


def json_gone_error(id, message):
    return json_error(id, message, 410)


def json_internal_server_error(id, message):
    return json_error(id, message, 500)


def json_service_unavailable_error(id, message):
    return json_error(id, message, 503)


# concrete error responses

def json_login_error():
    # should be the same no matter why login fails
    return json_authorization_error('INVALID_LOGIN', 'invalid username or password')


def json_error_no_record_found():
    return json_not_found_error('NO_RECORD', 'No record found in database.')


def json_error_wrong_parameters():
    return json_bad_request_error('WRONG_PARAMETERS', 'Service called with wrong parameters.')


def json_error_user_already_exists():
    return json_bad_request_error('USER_ALREADY_EXISTS', 'User already exists.')


def json_error_database_access_failed():
    return json_service_unavailable_error('DATABASE_ACCESS_FAILED', "database access failed")


def json_no_command_target_found_error():
    return json_not_found_error('NO_TARGET_FOUND', 'no target found for given command')


def json_action_execution_error(errors):
    return json_internal_server_error('EXECUTION_ERROR', ", ".join(errors))
