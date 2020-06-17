'''
badge sensor state management

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from datetime import datetime, timedelta

from app import (app, mongo)
from app.cms.user_utils import find_user

from .sensor_utils import (remove_outdated_visitors, make_beacon_range_info, compute_beacon_range_signature)


log = app.logger


badgesensor_range_visitor_map = {}
badgesensor_info_cache = {}


def get_badgesensor_range_visitor_map(badgesensor_name, range_index):

    global badgesensor_range_visitor_map
    range_map = badgesensor_range_visitor_map.setdefault(badgesensor_name, {})
    return range_map.setdefault(range_index, {})


def reset_badgesensor_info_cache():

    global badgesensor_info_cache
    badgesensor_info_cache = {}


def find_badgesensor_info(badgesensor_name):

    global badgesensor_info_cache

    if not badgesensor_name: return None

    if badgesensor_name in badgesensor_info_cache:
        return badgesensor_info_cache[badgesensor_name]

    # find badge sensor
    query = {
        'type': 'badgesensor',
        'fields.name': badgesensor_name,
        'timestamp-deleted': {'$exists': False}
    }
    badgesensor = mongo.db.objects.find_one(query, {'_id': False})

    if not badgesensor or 'id' not in badgesensor or 'fields' not in badgesensor:
        log.warning(f"badge sensor {badgesensor_name} not registered")
        badgesensor_info = None
    
    else:
        badgesensor_fields = badgesensor['fields']
        badgesensor_ranges = badgesensor_fields.get('ranges') or []
        range_infos = [make_beacon_range_info(item) for item in badgesensor_ranges]

        badgesensor_info = {
            'id': badgesensor['id'],
            'name': badgesensor_fields.get('name'),
            'building': badgesensor_fields.get('building'),
            'section': badgesensor_fields.get('section'),
            'ranges': range_infos,
            'signature': compute_beacon_range_signature(range_infos)
        }

    badgesensor_info_cache[badgesensor_name] = badgesensor_info
    return badgesensor_info


def enter_badgesensor_range(badgesensor_info, range_index, visitor_id, now, timeout_seconds = 300):

    badgesensor_name = badgesensor_info['name']
    visitor_map = get_badgesensor_range_visitor_map(badgesensor_name, range_index)

    # remove outdated visitors
    remove_outdated_visitors(visitor_map, now, timeout_seconds)

    # remember visitor for this badge sensor range
    visitor_map[visitor_id] = {'entertime': now, 'holdtime': now}


def hold_badgesensor_range(badgesensor_info, range_index, visitor_id, now, timeout_seconds = 300):

    badgesensor_name = badgesensor_info['name']
    visitor_map = get_badgesensor_range_visitor_map(badgesensor_name, range_index)

    # remove outdated visitors
    remove_outdated_visitors(visitor_map, now, timeout_seconds)

    # remember visitor for this badge sensor range
    entry = visitor_map[visitor_id]
    if entry:
        entry['holdtime'] = now


def leave_badgesensor_range(badgesensor_info, range_index, visitor_id, now, timeout_seconds = 300):

    badgesensor_name = badgesensor_info['name']
    visitor_map = get_badgesensor_range_visitor_map(badgesensor_name, range_index)

    # delete visitor from this badge sensor range
    if visitor_id in visitor_map:
        del visitor_map[visitor_id]

    # remove outdated visitors
    remove_outdated_visitors(visitor_map, now, timeout_seconds)


def get_badgesensor_range_status_info(badgesensor_name, range_index, visitors):

    badgesensor_info = find_badgesensor_info(badgesensor_name) or {}
    ranges = badgesensor_info.get('ranges') or []

    return {
        'id': badgesensor_info.get('id'),
        'name': badgesensor_info.get('name') or '',
        'building': badgesensor_info.get('building') or '',
        'section': badgesensor_info.get('section') or '',
        'range': ranges[range_index].get('distance') if range_index < len(ranges) else '',
        'visitors': [
            {
                'id': visitor_id,
                'time': visitor_properties['entertime'].timestamp()
            } for (visitor_id, visitor_properties) in visitors.items()
        ]
    }


def get_badgesensor_range_status_list():

    global badgesensor_range_visitor_map

    return [
        get_badgesensor_range_status_info(badgesensor_name, range_index, visitors)
        for (badgesensor_name, badgesensor_ranges) in badgesensor_range_visitor_map.items() for (range_index, visitors) in badgesensor_ranges.items()
    ]
