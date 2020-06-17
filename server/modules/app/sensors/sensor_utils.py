'''
utilities for sensor management

:author: Jens Gruschel
:copyright: © 2020 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from datetime import (datetime, timedelta)

from app.utils.math_utils import (get_float_or_default)


def remove_outdated_visitors(visitor_map, now, timeout_seconds):

    long_ago = now - timedelta(seconds=timeout_seconds)
    keys = list(visitor_map.keys())
    for key in keys:
        if visitor_map[key]['holdtime'] < long_ago:
            del visitor_map[key]


def make_beacon_range_info(range_item):

    fields = range_item.get('fields') or {}
    distance = get_float_or_default(fields.get('distance'), 1.0)
    hysteresis = get_float_or_default(fields.get('hysteresis'), 50.0) * 0.01
    near_threshold = distance
    far_threshold = distance * (1.0 + hysteresis)

    return {
        'distance': distance,
        'nearthreshold': near_threshold,
        'farthreshold': far_threshold,
        'effects': fields.get('effects') or []
    }


def compute_beacon_range_signature(range_info_list):

    # if any threshold of any range changes, the signature changes,
    # which means the client (sensor) has to fetch the range info again
    # in order to communicate with the server
    return str(hash(
        tuple([hash((info['nearthreshold'], info['farthreshold'])) for info in range_info_list])
    ) % 0x7fffffffffffffff)