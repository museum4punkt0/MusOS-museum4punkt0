'''
action processing engine with scheduling thread

:authors: Jens Gruschel, Maurizio Tidei
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import threading
import time
import uuid
import traceback
import random
from datetime import (datetime, timedelta)

from app import (app, socketio, mongo)
from app.cms.object_utils import (find_referenced_items)
from app.utils.api_utils import (get_field_time_seconds)
from app.utils.math_utils import (get_int_or_default)

from .action_utils import (get_avatar, complete_subject_text, create_chat_object)
from .property_utils import (get_property_key, evaluate_conditions)


log = app.logger


def action_timer_thread():
    while True:
        socketio.sleep(0.1)
        try:
            with app.app_context():
                process_action_queue()
        except Exception as e:
            log.error("action timer thread error: " + str(e))


def process_action_queue():
    now = datetime.utcnow()
    items = mongo.db.actionqueue.find({'$query': {'time': {'$lte': now.timestamp()}}, '$orderby': {'time': 1}})
    try:
        for item in items:

            time = datetime.utcfromtimestamp(item['time'])
            action = item['action']
            origin = item['origin']
            storyline = item['storyline']
            context = item['context']
            targets = item['targets']

            errors = execute_action_now(time, action, origin, storyline, context, targets)
            if errors:
                log.error("error processing action queue: " + ", ".join(errors))
    finally:
        mongo.db.actionqueue.remove({'time': {'$lte': now.timestamp()}})


def queue_action(time, action, origin, storyline, context, targets):
    """
    queue a single action for later processing (given by the time parameter)
    """

    # queue action in mongo db
    log.debug(f"queuing {action} of {origin} on {targets} with {context} at {time}")
    mongo.db.actionqueue.insert({
        'time': time.timestamp(),
        'action': action,
        'origin': origin,
        'storyline': storyline,
        'context': context,
        'targets': targets
    })
    return []
    

def declare_action(time, end, action, storyline, targets):
    for target in targets:
        mongo.db.actionstate.insert({
            'time': time.timestamp(),
            'end': end.timestamp(),
            'action': action,
            'storyline': storyline,
            'target': target
        })


def cancel_all_actions_on_targets(targets):
    affected = 0
    if targets:
        for target in targets:
            # first remove actions with exactly this target
            result = mongo.db.actionqueue.delete_many({'targets': [target]})
            if result.acknowledged:
                affected += result.deleted_count
            # also remove target from actions with more than one target
            result = mongo.db.actionqueue.update_many({'targets': target}, {'$pull': {'targets': target}})
            if result.acknowledged:
                affected += result.modified_count
    else:
        # remove actions without any target
        result = mongo.db.actionqueue.delete_many({'targets': []})
        if result.acknowledged:
            affected += result.deleted_count
    log.info(f"cancelled all {affected} action(s) on {targets}")
    return affected


def cancel_obsolete_actions(storyline, targets, time):
    affected = 0
    timestamp = time.timestamp()
    if targets:
        for target in targets:
            # first remove actions with exactly this target
            result = mongo.db.actionqueue.delete_many({'targets': [target], 'time': {'$gte': timestamp}, 'storyline': {'$ne': storyline}})
            if result.acknowledged:
                affected += result.deleted_count
            # also remove target from actions with more than one target
            result = mongo.db.actionqueue.update_many({'targets': target, 'time': {'$gte': timestamp}, 'storyline': {'$ne': storyline}}, {'$pull': {'targets': target}})
            if result.acknowledged:
                affected += result.modified_count
    else:
        # remove actions without any target
        result = mongo.db.actionqueue.delete_many({'targets': [], 'time': {'$gte': timestamp}, 'storyline': {'$ne': storyline}})
        if result.acknowledged:
            affected += result.deleted_count
    if affected > 0:
        log.info(f"cancelled {affected} obsolete action(s) on {targets}")
    return affected


def cancel_storyline(storyline):
    affected = 0
    result = mongo.db.actionqueue.delete_many({'storyline': storyline})
    if result.acknowledged:
        affected += result.deleted_count
    log.info(f"cancelled {affected} action(s) of storyline {storyline}")
    return affected


def execute_stories(stories, individual, visitor_type, targets):
    errors = []
    for story in stories:
        errors.extend(execute_story(story, individual, visitor_type, targets))
    return errors


def execute_story(story, individual, visitor_type, targets, leave = False):
    if not story or not 'fields' in story:
        log.warning(f"ignoring invalid story {story}")
        return ['invalid story']
    story_fields = story['fields']
    entries = story_fields.get('exit') if leave else story_fields.get('entry')
    if not entries:
        log.warning(f"ignoring story {story.get('id')} without any entries")
        return [] # no entries defined (yet), which is okay

    visitor_type_id = visitor_type.get('id') if visitor_type else None
    visitor_type_fields = (visitor_type.get('fields') or {}) if visitor_type else {}
    avatars = story_fields.get('avatar') or visitor_type_fields.get('avatar') or []
    avatar_id = avatars[0] if avatars else None
    context = {'individual': individual or 'anyone', 'avatar': avatar_id, 'subjects': story_fields.get('exhibits') or []}

    # get probabilities
    probabilities = [get_selection_probability(entry, context, visitor_type_id) for entry in entries]
    total = sum(probabilities)
    log.debug(f"entry probabilities for {visitor_type and visitor_type.get('title')} are {probabilities}, total = {total}")
    if total <= 0:
        log.warning(f"ignoring story {story.get('id')} without any entries for {visitor_type and visitor_type.get('title')}")
        return [] # no entries defined (yet), which is okay

    # alternative targets defined?
    if 'target' in story_fields and story_fields['target']:
        targets = story_fields['target']

    # start new storyline
    storyline = str(uuid.uuid4())
    now = datetime.utcnow()

    log.info(f"{'leaving' if leave else 'executing'} story with {len(entries)} entrie(s) as {storyline} for {visitor_type and visitor_type.get('title')} with {context} on {targets}")

    # execute a single scene at random
    number = random.random() * total
    for i, probability in enumerate(probabilities):
        if number < probability:
            return execute_selection(now, entries[i], storyline, context, targets)
        number -= probability

    # probably the random number was too large (due to rounding errors),
    # so simply execute scene with highest probability
    max_probability = max(probabilities)
    index = probabilities.index(max_probability)
    return execute_selection(now, entries[index], storyline, context, targets)


def get_selection_probability(selection, context, visitor_type_id):
    if not 'fields' in selection:
        return 0
    fields = selection['fields']

    # evaluate conditions
    conditions = fields.get('conditions') or []
    if not evaluate_conditions(conditions, context):
        return 0

    # check visitor type
    visitor_types = fields['visitortype'] if 'visitortype' in fields else []
    if not visitor_types or visitor_type_id in visitor_types:
        if not 'probability' in fields:
            return 0
        try:
            probability = float(fields['probability'])
            return probability if probability >= 0 else 0
        except:
            return 0
    return 0


def execute_selection(ref_time, selection, storyline, context, targets):
    if not 'fields' in selection:
        return ['invalid selection']
    fields = selection['fields']
    scene_ids = fields['scene'] if 'scene' in fields else []
    errors = []
    for scene_id in scene_ids:
        errors.extend(execute_scene_id(ref_time, scene_id, storyline, context, targets))
    return errors


def execute_scene_id(ref_time, scene_id, storyline, context, targets, ignore_ids = None):
    scene = mongo.db.objects.find_one({'id': scene_id}, {'_id': False})
    return execute_scene(ref_time, scene, storyline, context, targets, ignore_ids)


def execute_scene(ref_time, scene, storyline, context, targets, ignore_ids = None):
    if not scene or not 'fields' in scene:
        return ['invalid scene']
    fields = scene['fields']
    if not 'actions' in fields:
        return [] # no actions defined (yet), which is okay
    actions = fields['actions']

    # alternative targets defined?
    if 'target' in fields and fields['target']:
        targets = fields['target']

    # avoid endless recursion and circles
    scene_id = scene.get('id')
    if scene_id:
        if not ignore_ids:
            ignore_ids = {scene_id}
        else:
            ignore_ids.add(scene_id)

    log.info(f"executing scene {scene_id} with {len(actions)} action(s) as storyline {storyline} with {context} on {targets}")

    return schedule_actions(ref_time, actions, scene_id, storyline, context, targets, ignore_ids)


def execute_interaction_option(ref_time, option, context, targets):
    if not option or not 'fields' in option:
        return ['invalid option']

    storyline = str(uuid.uuid4())
    fields = option['fields']

    # alternative targets defined?
    if 'target' in fields and fields['target']:
        targets = fields['target']

    # get actions
    reactions = fields['reactions'] if 'reactions' in fields else []
    log.debug(f"executing option with reactions {reactions} with {context} on {targets}")

    # execute actions
    return schedule_actions(ref_time, reactions, None, storyline, context, targets)


def schedule_actions(ref_time, actions, scene_id, storyline, context, targets, ignore_ids = None, schedule = None):
    """
    execute a list of actions relative to a given reference time, which defines what "null" means
    (which usually is near datetime.utcnow(), but can differ due to inaccuracies and processing latency),
    ignoring objects (scenes) on a black list to avoid endless recursion or circles
    """

    if schedule is None:
        schedule = {'previous_start': 0, 'previous_stop': 0}

    log.debug(f"executing {len(actions)} action(s) of szene {scene_id} with {context} on {targets} at {ref_time} and {schedule}")

    try:
        errors = []
        for index, action in enumerate(actions):
            origin = {'scene': scene_id, 'index': index}
            errors.extend(schedule_action(ref_time, action, origin, storyline, context, targets, ignore_ids, schedule))
        return errors
    except Exception as e:
        log.error("actions error: " + str(e))
        return errors.extend(str(e))


def select_case_actions(cases, context):

    for case in cases:
        if 'type' not in case or 'fields' not in case: continue
        caseType = case['type']
        fields = case['fields']

        if caseType == 'case':
            conditions = fields.get('conditions') or []
            if evaluate_conditions(conditions, context):
                return fields.get('actions') or []

    return None # which means "else", "alternative" actions will be executed


def create_answer(option, context):
    if 'fields' not in option:
        return None
    fields = option['fields']
    if 'answer' not in fields:
        return None
    if 'conditions' in fields:
        if not evaluate_conditions(fields['conditions'], context):
            return None
    return fields['answer']


def schedule_action(ref_time, action, origin, storyline, context, targets, ignore_ids = None, schedule = None):
    """
    execute a single action relative to a given reference time, which defines what "null" means
    (which usually is near datetime.utcnow(), but can differ due to inaccuracies and processing latency),
    using a schedule object to schedule actions relative to other ones,
    ignoring objects (scenes) on a black list to avoid endless recursion or circles
    """

    if schedule is None:
        schedule = {'previous_start': 0, 'previous_stop': 0}

    log.debug(f"scheduling action {action} of {origin} with {context} on {targets} at {ref_time} and {schedule}")

    try:
        # valid action?
        if not 'fields' in action or not 'type' in action:
            return ['invalid action']
        fields = action['fields']
        
        # action inactive? (return no error because it was intended to do nothing)
        if 'active' in fields:
            active = fields['active']
            if active == False:
                return []

        # alternative targets defined?
        action_targets = fields['target'] if 'target' in fields and fields['target'] else targets

        # calculate delay of action (based on properties and schedule)
        delay = get_field_time_seconds(fields, 'delay', 0, 's')
        duration = get_field_time_seconds(fields, 'duration', 0, 's')
        if 'start' in fields:
            if fields['start'] == 'withprevious':
                delay += schedule['previous_start']
            elif fields['start'] == 'afterprevious':
                delay += schedule['previous_stop']
        schedule['previous_start'] = delay
        schedule['previous_stop'] = delay + duration

        # execute action now or later
        delta = timedelta(seconds=delay)
        offset = datetime.utcnow() - ref_time
        if delta > offset:
            time = ref_time + delta
            cancel_obsolete_actions(storyline, action_targets, time)
            return queue_action(time, action, origin, storyline, context, action_targets)
        else:
            cancel_obsolete_actions(storyline, action_targets, ref_time)
            return execute_action_now(ref_time, action, origin, storyline, context, action_targets, ignore_ids)

    except Exception as e:
        msg = f"action scheduling error: {e}"
        log.error(msg)
        return [msg]
        
        
def execute_action_now(ref_time, action, origin, storyline, context, targets, ignore_ids = None):
    """
    execute a single action immediately either on the targets defined with the action
    or on the given targets
    (a reference time is required in case the action leads to an executaion of other sub-actions)
    """

    # valid action?
    if not 'fields' in action or not 'type' in action:
        return ['invalid action']
    actionType = action['type']
    fields = action['fields']

    log.debug(f"executing {actionType} of {origin} with {fields} with {context} on {targets} at {ref_time}")

    duration = duration = get_field_time_seconds(fields, 'duration', 0, 's')
    declare_action(ref_time, ref_time + timedelta(seconds=duration), action, storyline, targets)

    try:

        if actionType == 'sceneaction':

            scene_ids = [id for id in fields['scene'] if id not in ignore_ids] if ignore_ids else [id for id in fields['scene']]
            scenes = mongo.db.objects.find({'id': {'$in': scene_ids}}, {'_id': False})

            errors = []
            for scene in scenes:
                errors.extend(execute_scene(ref_time, scene, storyline, context, targets, ignore_ids))
            return errors

        elif actionType == 'textaction':

            # get text, making replacements if necessary
            subject_ids = context.get('subjects')
            text = complete_subject_text(fields['text'], subject_ids) if 'text' in fields else None

            # get images or videos
            media_ids = fields['medialist'] if 'medialist' in fields else []
            media_items_cursor = mongo.db.objects.find({'id': {'$in': media_ids}}, {'_id': False})
            objects = [create_chat_object(item) for item in media_items_cursor]

            # automatically extend message
            automatismns = fields.get('automatismns')
            if automatismns:
                for automatismn in automatismns:
                    automatismn_type = automatismn.get('type')
                    if not automatismn_type: continue
                    automatismn_fields = automatismn.get('fields')
                    if not automatismn_fields: continue
                    if automatismn_type == 'taggedmediaautomatism':
                        max_count = get_int_or_default(automatismn_fields.get('maxCount'))
                        if max_count < 1: continue
                        tags = automatismn_fields.get('tags')
                        if not tags: continue
                        if subject_ids:
                            subject_media_cursor = mongo.db.objects.find(
                                {'id': {'$in': subject_ids}},
                                {'fields.medialist': True, '_id': False}
                            ) # TODO: does not work for media item fields with other name
                            subject_media_ids = [
                                media_id for subject in subject_media_cursor for media_id in (subject['fields'].get('medialist') or [])
                            ] # TODO: does not work for media item fields with other name
                            tagged_media_items_cursor = mongo.db.objects.find(
                                {'id': {'$in': subject_media_ids}, 'tags': {'$all': tags}},
                                {'_id': False}
                            )
                        else:
                            tagged_media_items_cursor = mongo.db.objects.find(
                                {'type': 'mediaitem', 'tags': {'$all': tags}},
                                {'_id': False}
                            )
                        tagged_objects = [create_chat_object(item) for item in tagged_media_items_cursor]
                        log.info(f"{len(tagged_objects)} media items for subjects {subject_ids} with tags {tags} added automatically")
                        # randomly attach some of the pictures we found
                        random.shuffle(tagged_objects)
                        objects.extend(tagged_objects[:max_count])
                if not objects:
                    # in case there are any automatisms but no pictures at all
                    # the text probably makes no sense
                    text = None

            if text or objects:

                # get avatar
                if 'avatar' in fields and fields['avatar']:
                    avatar_id = fields['avatar'][0]
                    context = {**context, 'avatar': avatar_id}
                else:
                    avatar_id = context.get('avatar')
                avatar = get_avatar(avatar_id)
                
                # send message
                log.debug(f"sending chat message '{text}' from {avatar} with objects {objects} to {targets}")
                for target in targets:
                    socketio.emit('chatmessage', {
                        'time': ref_time.timestamp(),
                        'text': text or '',
                        'objects': objects,
                        'avatar': avatar,
                        'conversation': avatar # TODO: maybe later multiple avatars can join one conversation or one avatar can join multiple conversations
                    }, room=target)

        elif actionType == 'interaction':

            # get text, making replacements if necessary
            subject_ids = context.get('subjects')
            text = complete_subject_text(fields['text'], subject_ids) if 'text' in fields else None

            # get answers
            options = fields['options'] if 'options' in fields else []
            answers = [create_answer(option, context) for option in options]

            # get avatar
            if 'avatar' in fields and fields['avatar']:
                avatar_id = fields['avatar'][0]
                context = {**context, 'avatar': avatar_id}
            else:
                avatar_id = context.get('avatar')
            avatar = get_avatar(avatar_id)

            # send message
            log.debug(f"sending interaction '{text}' and answers {answers} to {targets}")
            for target in targets:
                socketio.emit('chatinteraction', {
                    'time': ref_time.timestamp(),
                    'origin': origin,
                    'text': text or '',
                    'answers': answers,
                    'avatar': avatar,
                    'context' : context,
                    'conversation': avatar # TODO: maybe later multiple avatars can join one conversation or one avatar can join multiple conversations
                }, room=target)

        elif actionType == 'notificationaction':

            text = fields['text'] if 'text' in fields else ''
            log.debug(f"sending notification '{text}' to {targets}")
            for target in targets:
                socketio.emit('shownotification', {'time': ref_time.timestamp(), 'text': text}, room=target)

        elif actionType == 'mediaaction':

            loop = bool(fields['loop']) if 'loop' in fields else False
            backdrop = bool(fields['backdrop']) if 'backdrop' in fields else False

            media_ids = fields['medialist'] if 'medialist' in fields else []
            if not media_ids:
                for target in targets:
                    socketio.emit('stop', {'time': ref_time.timestamp(), 'backdrop': backdrop}, room=target)
                return []
            media_item = mongo.db.objects.find_one({'id': media_ids[0]}, {'_id': False})
            if not media_item:
                return ['media item not found']

            referenced_items = find_referenced_items(media_item)

            log.debug(f"sending media item {media_item} to {targets}")
            for target in targets:
                socketio.emit('playobject', {
                    'time': ref_time.timestamp(),
                    'object': media_item,
                    'loop': loop,
                    'backdrop': backdrop,
                    'referenced': referenced_items
                }, room=target)

        elif actionType == 'contentaction':

            content_ids = fields.get('content')
            if not content_ids:
                return []
            content = mongo.db.objects.find_one({'id': {'$in': content_ids}}, {'_id': False})
            if not content:
                return ['content not found']

            referenced_items = find_referenced_items(content)

            subject_ids = fields.get('subjects')
            if subject_ids:
                # query objects one by one to preserve order
                subjects = [mongo.db.objects.find_one({'id': subject_id}, {'_id': False}) for subject_id in subject_ids]
            else:
                subjects = context.get('subjects')

            log.debug(f"sending content {content} to {targets}")

            for target in targets:
                socketio.emit('playobject', {
                    'time': ref_time.timestamp(),
                    'object': content,
                    'referenced': referenced_items,
                    'subjects': subjects
                }, room=target)

        elif actionType == 'stateaction':

            if 'property' not in fields or len(fields['property']) < 1:
                return ['no state property defined']
            property_id = fields['property'][0]
            method = fields['method'] if 'method' in fields else 'set'
            value = fields['value'] if 'value' in fields else None
            property_key = get_property_key(property_id, context.get('individual'))
            if not property_key:
                return ['invalid state property']

            if method == 'add':
                previous = mongo.db.propertyvalues.find_one(property_key)
                if previous and 'value' in previous:
                    try:
                        value = float(previous['value']) + float(value)
                    except:
                        pass

            mongo.db.propertyvalues.replace_one(property_key, {
                'individual': property_key['individual'],
                'property': property_key['property'],
                'value': value,
                'time': ref_time.timestamp()
            }, upsert = True)

        elif actionType == 'conditionalaction':

            conditions = fields.get('conditions') or []
            if evaluate_conditions(conditions, context):
                actions = fields.get('actions')
                if actions:
                    # origin does not exist because its not the actions of a scene and interaction is not allowed
                    return schedule_actions(ref_time, actions, None, storyline, context, targets, ignore_ids)
            else:
                actions = fields.get('alternative')
                if actions:
                    # origin does not exist because its not the actions of a scene and interaction is not allowed
                    return schedule_actions(ref_time, actions, None, storyline, context, targets, ignore_ids)

        elif actionType == 'caseaction':

            cases = fields.get('cases') or []
            actions = select_case_actions(cases, context)
            if actions != None:
                # origin does not exist because its not the actions of a scene and interaction is not allowed
                return schedule_actions(ref_time, actions, None, storyline, context, targets, ignore_ids)
            else:
                actions = fields.get('alternative')
                if actions:
                    # origin does not exist because its not the actions of a scene and interaction is not allowed
                    return schedule_actions(ref_time, actions, None, storyline, context, targets, ignore_ids)

        elif actionType == 'controlaction':

            if 'command' not in fields:
                return ['control command missing']
            command = fields['command']

            if command == 'reset':
                for target in targets:
                    socketio.emit('reset', {'time': ref_time.timestamp()}, room=target)
            elif command == 'clearchat':
                for target in targets:
                    socketio.emit('clearchat', {'time': ref_time.timestamp()}, room=target)
            elif command == 'showchat':
                for target in targets:
                    socketio.emit('showchat', {'time': ref_time.timestamp(), 'visible': True, 'forceChatMode': False}, room=target)
            elif command == 'showchatonly':
                for target in targets:
                    socketio.emit('showchat', {'time': ref_time.timestamp(), 'visible': True, 'forceChatMode': True}, room=target)
            elif command == 'hidechat':
                for target in targets:
                    socketio.emit('showchat', {'time': ref_time.timestamp(), 'visible': False}, room=target)
            elif command == 'pause':
                for target in targets:
                    socketio.emit('pause', {'time': ref_time.timestamp()}, room=target)
            elif command == 'resume':
                for target in targets:
                    socketio.emit('resume', {'time': ref_time.timestamp()}, room=target)
            elif command == 'showmenu-a':
                for target in targets:
                    socketio.emit('showmenu', {'time': ref_time.timestamp(), 'slot': 'A', 'visible': True}, room=target)
            elif command == 'showmenu-b':
                for target in targets:
                    socketio.emit('showmenu', {'time': ref_time.timestamp(), 'slot': 'B', 'visible': True}, room=target)
            elif command == 'hidemenu-a':
                for target in targets:
                    socketio.emit('showmenu', {'time': ref_time.timestamp(), 'slot': 'A', 'visible': False}, room=target)
            elif command == 'hidemenu-b':
                for target in targets:
                    socketio.emit('showmenu', {'time': ref_time.timestamp(), 'slot': 'B', 'visible': False}, room=target)
            elif command == 'togglemenu-a':
                for target in targets:
                    socketio.emit('showmenu', {'time': ref_time.timestamp(), 'slot': 'A', 'visible': 'toggle'}, room=target)
            elif command == 'togglemenu-b':
                for target in targets:
                    socketio.emit('showmenu', {'time': ref_time.timestamp(), 'slot': 'B', 'visible': 'toggle'}, room=target)
            elif command == 'resetvisitorstate':
                individual = context.get('individual')
                if individual and individual != 'anyone' and individual != 'global':
                    mongo.db.propertyvalues.delete_many({'individual': individual})
            elif command == 'clearsubjects':
                for target in targets:
                    socketio.emit('setcontext', {'time': ref_time.timestamp(), 'subjects': [], 'referenced': [], 'operation': 'replace'}, room=target)
            elif command == 'showscreensaver':
                for target in targets:
                    socketio.emit('showscreensaver', {'time': ref_time.timestamp()}, room=target)
            elif command == 'resetidletimer':
                for target in targets:
                    socketio.emit('resetidletimer', {'time': ref_time.timestamp()}, room=target)
            else:
                log.warning(f"unknown control command {command}")
                return [f"unknown control command {command}"]

            log.debug(f"control command '{command}' sent to {targets}")


        elif actionType == 'menuaction':

            if not 'slot' in fields or not fields['slot']:
                return ["slot missing"]
            slot = fields['slot']

            menu_ids = fields.get('menu')
            if menu_ids:
                menu = mongo.db.objects.find_one({'id': menu_ids[0]}, {'_id': False})
            else:
                menu = None
            visible = not fields.get('hidden')

            for target in targets:
                socketio.emit('changemenu', {
                    'time': ref_time.timestamp(),
                    'slot': slot,
                    'menu': menu,
                    'visible': visible,
                    'referencedObjects': find_referenced_items(menu) if menu else [],
                    'context' : context
                }, room=target)
        
        else:
            msg = f"unknown action type: {actionType}"
            log.error(msg)
            return [msg]

        # finally indicate that no errors occurred
        return []

    except Exception as e:
        msg = f"action execution error: {e}"
        log.error(msg)
        log.error(traceback.format_exc())
        return [msg]

