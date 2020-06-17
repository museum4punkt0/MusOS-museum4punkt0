'''
utilities for rest APIs

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from app import (app, mongo)


log = app.logger


def find_box(box_name):
    return mongo.db.objects.find_one({'type': 'cbox', 'fields.name': box_name, 'timestamp-deleted': {'$exists': False}}, {'_id': False})


def find_sensor(sensor_name):
    return mongo.db.objects.find_one({'type': {'$in': ['sensor', 'badgesensor', 'simpletrigger']}, 'fields.name': sensor_name, 'timestamp-deleted': {'$exists': False}}, {'_id': False})


def find_channel(channel_name):
    return mongo.db.objects.find_one({'type': 'channel', 'fields.name': channel_name, 'timestamp-deleted': {'$exists': False}}, {'_id': False})


def find_badge(args):
    if 'badge' in args and args.get('badge'):
        # find badge (case insensitive with collation)
        badge_id = args.get('badge')
        badges = [badge for badge in mongo.db.objects.find({'type': 'badge', 'fields.identifier': badge_id, 'timestamp-deleted': {'$exists': False}}, {'_id': False}).collation({'locale': 'en_US', 'strength': 2})]
        if badges and 'id' in badges[0]:
            return badges[0]
        else:
            log.warning(f"badge {badge_id} not registered")
            return None
    else:
        return None


def get_storyline(args):
    if 'storyline' in args and args.get('storyline'):
        return args.get('storyline')
    else:
        return None


def get_individual(args):
    if 'individual' in args and args.get('individual'):
        return args.get('individual')
    else:
        return None


def get_target(args):
    if 'sid' in args and args.get('sid'):
        return args.get('sid')
    elif 'channelid' in args and args.get('channelid'):
        return args.get('channelid')
    elif 'boxname' in args and args.get('boxname'):
        box = find_box(args.get('boxname'))
        return box['id'] if box and 'id' in box else None
    elif 'channelname' in args and args.get('channelname'):
        channel = find_channel(args.get('channelname'))
        return channel['id'] if channel and 'id' in channel else None
    elif 'boxorchannel' in args and args.get('boxorchannel'):
        box = find_box(args.get('boxorchannel'))
        if box and 'id' in box : return box['id']
        channel = find_channel(args.get('channelname'))
        if channel and 'id' in channel : return channel['id']
        return args.get('boxorchannel')
    else:
        return None


def get_visitor_type(args):
    if 'visitortype' in args and args.get('visitortype'):
        visitor_type_id = args.get('visitortype')
        return mongo.db.objects.find_one({'type': 'visitortype', 'fields.name': visitor_type_id, 'timestamp-deleted': {'$exists': False}}, {'_id': False})
    else:
        return None


def get_field_time_seconds(fields, field_name, default_value, default_suffix):

    if field_name in fields:
        try:
            result = float(fields[field_name])
        except:
            result = default_value
    else:
        result = default_value

    suffix_name = field_name + '__suffix'
    if suffix_name in fields and fields[suffix_name]:
        suffix = fields[suffix_name]
    else:
        suffix = default_suffix

    if suffix == 'ms':
        return result * 0.001
    elif suffix == 'min':
        return result * 60
    elif suffix == 'h':
        return result * 3660
    elif suffix == 'd':
        return result * 86400
    else:
        return result
