'''
storytelling state management

:author: Jens Gruschel
:copyright: © 2020 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from datetime import (datetime, timedelta)

from app import (app, mongo)
from app.cms.user_utils import (find_user)
from app.utils.math_utils import (get_float_or_default)

from .action_engine import (execute_story)


log = app.logger


story_visitor_map = {}
story_info_cache = {}


def get_story_visitor_map(story_id):

    global story_visitor_map
    return story_visitor_map.setdefault(story_id, {})


def create_story_info(story):

    if 'fields' not in story:
        return {}

    fields = story['fields']

    return {
            'id': story.get('id'),
            'name': fields.get('name'),
            'mode': fields.get('mode')
    }


def refresh_story_info(story):

    global story_info_cache

    story_id = story['id']
    story_info_cache[story_id] = create_story_info(story)


def find_story_info(story_id):

    global story_info_cache

    if not story_id: return None

    if story_id in story_info_cache:
        return story_info_cache[story_id]

    # find story
    story = mongo.db.objects.find_one({'id': story_id}, {'_id': False})

    if not story:
        return None

    story_info = create_story_info(story)
    story_info_cache[story_id] = story_info    
    return story_info


def remove_outdated_visitors(visitor_map, now, timeout_seconds):

    long_ago = now - timedelta(seconds=timeout_seconds)
    keys = list(visitor_map.keys())
    for key in keys:
        if visitor_map[key]['holdtime'] < long_ago:
            del visitor_map[key]


def find_next_exclusive_visitor(visitor_map, now):

    chosen_key = None
    chosen_time = now
    for key in visitor_map.keys():
        if visitor_map[key]['entertime'] < chosen_time:
            chosen_key = key
            chosen_time = visitor_map[key]['entertime']
    return chosen_key


def execute_effects(now, effect_ids, visitor_id, visitor_type, targets, leave):
    effect_cursor = mongo.db.objects.find({'id': {'$in': effect_ids}}, {'_id': False})
    errors = []
    for effect in effect_cursor:
        effect_type = effect.get('type')
        if effect_type == 'story':
            story_id = effect.get('id')
            story_fields = effect.get('fields') or {}
            story_mode = story_fields.get('mode') or 'individual'
            if not leave:
                errors.extend(enter_story(now, story_id, story_mode, effect, visitor_id, visitor_type, targets))
            else:
                errors.extend(leave_story(now, story_id, story_mode, effect, visitor_id, visitor_type, targets))
        else:
            errors.append(f"effect type {effect_type or 'unknown'} not supported")
    return errors


def enter_story(now, story_id, story_mode, effect, visitor_id, visitor_type, targets, timeout_seconds = 300):

    visitor_map = get_story_visitor_map(story_id)

    # remove outdated visitors
    remove_outdated_visitors(visitor_map, now, timeout_seconds)

    # by default ('individual') always fire, but not exclusive
    fire = True
    exclusive = False

    if story_mode == 'shared':
        fire = len(visitor_map) == 0

    elif story_mode in ['exclusive', 'queueing']:
        fire = len(visitor_map) == 0
        exclusive = fire

    visitor_object = mongo.db.objects.find_one({'id': visitor_id}, {'_id': False})
    visitor_title = visitor_object and visitor_object.get('title')

    # remember visitor for this story
    visitor_map[visitor_id] = {
        'entertime': now,
        'holdtime': now,
        'exclusive': exclusive,
        'visitortype': visitor_type,
        'visitorname': visitor_title,
        'effect': effect,
        'targets': targets
    }

    log.info(f"entering {story_mode} story {story_id} for {visitor_title} ({visitor_id}) with fire = {fire}")
    if fire:
        return execute_story(effect, visitor_id, visitor_type, targets, False)
    else:
        return []


def leave_story(now, story_id, story_mode, effect, visitor_id, visitor_type, targets, timeout_seconds = 300):

    visitor_map = get_story_visitor_map(story_id)

    # get and delete visitor from this story
    if visitor_id in visitor_map:
        visitor_info = visitor_map[visitor_id]
        del visitor_map[visitor_id]
    else:
        visitor_info = {}

    # remove outdated visitors
    remove_outdated_visitors(visitor_map, now, timeout_seconds)

    # by default ('individual') always fire
    fire = True
    next_visitor_id = None

    if story_mode == 'shared':
        fire = len(visitor_map) == 0 

    elif story_mode in ['exclusive', 'queueing']:
        fire = visitor_info.get('exclusive')
        if fire and story_mode == 'queueing':
            next_visitor_id = find_next_exclusive_visitor(visitor_map, now)

    log.info(f"leaving {story_mode} story {story_id} for {visitor_id} with fire = {fire}")
    if fire:
        # execute story for previous visitor (leaving)
        errors = execute_story(effect, visitor_id, visitor_type, targets, True)
        # afterwards if someone is waiting also execute story for next visitor (entering)
        if next_visitor_id:
            visitor_map[next_visitor_id]['exclusive'] = True
            next_visitor_info = visitor_map[next_visitor_id]
            errors.extend(execute_story(
                next_visitor_info['effect'],
                next_visitor_id,
                next_visitor_info['visitortype'],
                next_visitor_info['targets'],
                False
            ))
        return errors
    else:
        return []


def get_story_status_info(story_id, visitors):

    story_info = find_story_info(story_id) or {}

    return {
        'id': story_info.get('id'),
        'name': story_info.get('name') or '',
        'mode': story_info.get('mode') or 'individual',
        'visitors': [
            {
                'id': visitor_id,
                'name': visitor_properties['visitorname'],
                'time': visitor_properties['entertime'].timestamp(),
                'exclusive': visitor_properties.get('exclusive')
            } for (visitor_id, visitor_properties) in visitors.items()
        ]
    }


def get_story_status_list():

    global story_visitor_map

    return [
        get_story_status_info(story_id, visitors)
        for (story_id, visitors) in story_visitor_map.items()
    ]
