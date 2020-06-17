'''
API for sensor communication

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import traceback
from datetime import (datetime, timedelta)
from flask import (request, jsonify)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from app import (app, mongo)
from app.utils.api_utils import (
    find_badge, get_individual, get_target, get_visitor_type
)
from app.utils.api_responses import (
    json_success,
    json_error_database_access_failed,
    json_action_execution_error,
    json_not_found_error,
    json_gone_error
)
from app.sensors.sensor_utils import (make_beacon_range_info, compute_beacon_range_signature)
from app.sensors.badgesensor_management import (
    find_badgesensor_info,
    enter_badgesensor_range, leave_badgesensor_range, hold_badgesensor_range,
    get_badgesensor_range_status_list
)
from app.engine.story_management import (
    get_story_status_list,
    execute_effects
)


log = app.logger


def extract_beacon_info(item):

    fields = item.get('fields') or {}
    ranges = fields.get('ranges') or []
    range_infos = [make_beacon_range_info(range_item) for range_item in ranges]

    return {
        'identifier': fields.get('identifier'),
        'ranges': [{
            'nearthreshold': info['nearthreshold'],
            'farthreshold': info['farthreshold']
        } for info in range_infos],
        'signature': compute_beacon_range_signature(range_infos)
    }


@app.route('/configuration/badgesensor/<sensor_name>', methods=['GET'])
# @jwt_required # executed by python script
def on_get_badgesensor_configuration(sensor_name):

    query = {
        'type': 'badgesensor',
        'fields.name': sensor_name,
        'timestamp-deleted': {'$exists': False}
    }

    try:
        item = mongo.db.objects.find_one(query, {'_id': False})
    except:
        log.error(f"database access failed for {request.url}")
        log.error(traceback.format_exc())
        return json_error_database_access_failed()

    if not item:
        return json_not_found_error('SENSOR_NOT_REGISTERED', "sensor not registered")

    # only pass information required for type
    fields = item.get('fields') or {}
    ranges = fields.get('ranges') or []
    range_infos = [make_beacon_range_info(range_item) for range_item in ranges]

    response = {
        'ranges': [{
            'nearthreshold': info['nearthreshold'],
            'farthreshold': info['farthreshold']
        } for info in range_infos],
        'signature': compute_beacon_range_signature(range_infos)
    }
    return jsonify(response), 200


@app.route('/state/sensors', methods=['GET'])
@jwt_required
def on_get_sensorstate():

    response = {
        'badgesensorstatus': get_badgesensor_range_status_list()
    }
    return jsonify(response), 200


@app.route('/state/stories', methods=['GET'])
@jwt_required
def on_get_storystate():

    story_status = get_story_status_list()
    response = {
        'storystatus': story_status
    }
    return jsonify(response), 200


@app.route('/trigger/badgesensor/<sensor_name>/<int:range_index>', methods=['GET'])
def on_trigger_badgesensor(sensor_name, range_index):

    # find method
    method = request.args.get('method')
    signature = request.args.get('signature')

    # find sensor
    sensor_info = find_badgesensor_info(sensor_name)
    if not sensor_info:
        log.warning(f"sensor {sensor_name} not registered")
        return json_not_found_error('SENSOR_NOT_REGISTERED', "sensor not registered")
    if signature and signature != sensor_info.get('signature'):
        return json_gone_error('SENSOR_CONFIGURATION_CHANGED', "sensor configuration has been changed and must be updated")

    # find beacon range
    beacon_ranges = sensor_info['ranges']
    if range_index >= len(beacon_ranges):
        log.warning(f"beacon range {range_index} not defined for {sensor_name}")
        return json_not_found_error('INVALID_BEACON_RANGE', "invalid beacon range")
    beacon_range = beacon_ranges[range_index]

    # find individual / visitor type from badge
    badge = find_badge(request.args)
    if not badge or 'id' not in badge or 'fields' not in badge:
        return json_not_found_error('BADGE_NOT_REGISTERED', "badge not registered")
    badge_fields = badge['fields']
    individual = badge['id']
    visitor_type_field = badge_fields.get('visitortype')
    if visitor_type_field:
        visitor_type_id = visitor_type_field[0]
        visitor_type = mongo.db.objects.find_one({'id': visitor_type_id}, {'_id': False}) if visitor_type_id else None
    else:
        visitor_type = None

    # update sensor state
    now = datetime.utcnow()
    if method == 'hold':
        hold_badgesensor_range(sensor_info, range_index, individual, now)
        return json_success("sensor hold successfully")
    elif method == 'leave':
        leave_badgesensor_range(sensor_info, range_index, individual, now)
    else:
        enter_badgesensor_range(sensor_info, range_index, individual, now)

    # find effects
    sensor_effect_ids = beacon_range.get('effects') or []
    badge_effect_ids = badge_fields.get('effects') or []
    effect_ids = sensor_effect_ids + badge_effect_ids
    if not effect_ids:
        return json_success("sensor triggered without effects")

    # execute effects
    log.info(f"{len(effect_ids)} effects(s) on {method} for {individual} of visitor type {visitor_type and visitor_type.get('title')} triggered by badge sensor {sensor_name}")
    errors = execute_effects(now, effect_ids, individual, visitor_type, [], method == 'leave')
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("sensor triggered successfully")


@app.route('/trigger/sensor/<sensor_name>', methods=['GET'])
def on_trigger_simple_trigger(sensor_name):

    # find sensor
    sensor = mongo.db.objects.find_one({'type': 'simpletrigger', 'fields.name': sensor_name, 'timestamp-deleted': {'$exists': False}}, {'_id': False})
    if not sensor or 'id' not in sensor or 'fields' not in sensor:
        log.warning(f"sensor {sensor_name} not registered")
        return json_not_found_error('SENSOR_NOT_REGISTERED', "sensor not registered")
    sensor_fields = sensor['fields']

    # execute effects
    effect_ids = sensor_fields.get('triggereffects') or []
    log.info(f"{len(effect_ids)} effects(s) triggered by simple trigger {sensor_name}")
    errors = execute_effects(datetime.utcnow(), effect_ids, None, None, [], False)
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("sensor triggered successfully")
