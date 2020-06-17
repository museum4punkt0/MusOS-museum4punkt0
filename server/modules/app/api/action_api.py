'''
API for storytelling / action processing

:authors: Jens Gruschel, Maurizio Tidei
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import uuid
from datetime import (datetime, timedelta)
from flask import (request, jsonify)

from app import (app, socketio, mongo)
from app.cms.object_utils import (find_referenced_items, fetch_single_referenced_item)
from app.engine.action_utils import (get_avatar)
from app.engine.action_engine import (execute_scene_id, execute_scene, execute_stories, execute_story, execute_interaction_option,
                            schedule_actions)
from app.utils.api_responses import (json_success, json_bad_request_error, json_not_found_error, json_not_acceptable_error,
                            json_no_command_target_found_error, json_action_execution_error)
from app.utils.api_utils import (find_box, find_channel, get_storyline, get_individual, get_target, get_visitor_type, get_field_time_seconds)


log = app.logger


@app.route('/box/<box_name>/refresh', methods=['GET'])
def on_refresh_box(box_name):

    box = find_box(box_name)
    if not box or 'id' not in box or 'fields' not in box:
        return json_not_found_error('NO_CONFIGURATION_FOUND', 'no configuration for box found')

    fields = box['fields']

    background_color = fields['backgroundcolor'] if 'backgroundcolor' in fields else '#000000'

    chat_display = fields.get('chatdisplay') or 'exclusive'

    background_media_item = fetch_single_referenced_item(fields.get('chatbackground'))
    background_media_url = background_media_item['fields']['url'] if background_media_item else None

    chat_stylesheet_item = fetch_single_referenced_item(fields.get('chatstyle'))
    chat_stylesheet = chat_stylesheet_item['fields']['definition'] if chat_stylesheet_item else None

    menu_stylesheet_item = fetch_single_referenced_item(fields.get('menustyle'))
    menu_stylesheet = menu_stylesheet_item['fields']['definition'] if menu_stylesheet_item else None

    menu_a = fetch_single_referenced_item(fields.get('menuA'))
    menu_b = fetch_single_referenced_item(fields.get('menuB'))

    shortcuts = None if fields.get('shortcutsactive') is False else [shortcut.get('fields').get('keys') for shortcut in fields.get('shortcuts', [])]

    avatar_id = fields['avatar'][0] if 'avatar' in fields and fields['avatar'] else None
    avatar = get_avatar(avatar_id)

    chat_properties = {
        'display': chat_display,
        'backgroundMediaUrl': background_media_url,
        'stylesheet': chat_stylesheet,
        'avatar': avatar
    }

    menu_properties = {
        'stylesheet': menu_stylesheet,
        'menus': {
            'A': {
                'menu': menu_a,
                'flags': {'visible': not fields.get('hideMenuB')},
                'referencedObjects': find_referenced_items(menu_a) if menu_a else []
            },
            'B': {
                'menu': menu_b,
                'flags': {'visible': not fields.get('hideMenuA')},
                'referencedObjects': find_referenced_items(menu_b) if menu_b else []
            }
        },
    }

    properties = {
        'backgroundColor': background_color,
        'chat': chat_properties,
        'menu': menu_properties,
        'shortcuts': shortcuts
    }

    configuration = {
        'logReduxActions': fields.get('logReduxActions'),
        'logReduxState': fields.get('logReduxState')
    }

    content = []
    referenced_items = []
    screensaver = {
        'timeout': 0,
        'content': None,
        'referenced': []
    }

    content_ids = fields.get('content')
    if content_ids:
        box_id = box['id']
        targets = [box_id]
        content_items = list(mongo.db.objects.find({'id': {'$in': content_ids}}, {'_id': False}))
        if content_items:
            # handle scenes specially (maybe find a better solution than mixing scenes and other content)
            storyline = str(uuid.uuid4())
            now = datetime.utcnow() + timedelta(seconds=2) # dirty hack to make sure the response for this request is sent first, and the scene is executed afterwards
            for content_item in content_items:
                if content_item['type'] == 'scene':
                    execute_scene(now, content_item, storyline, {'individual': box_id, 'avatar': avatar_id}, targets)
            # proceed with real content excluding scenes
            content = [content_item for content_item in content_items if content_item['type'] != 'scene']
            referenced_items.extend([referenced_item for content_item in content_items for referenced_item in find_referenced_items(content_item)])

    screensaver_content_ids = fields.get('screensavercontent')
    screensaver_timeout = get_field_time_seconds(fields, 'screensavertimeout', 0, "min")
    if screensaver_content_ids and screensaver_timeout > 0:
        screensaver_content = mongo.db.objects.find_one({'id': {'$in': screensaver_content_ids}}, {'_id': False})
        screensaver = {
            'timeout': screensaver_timeout,
            'content': screensaver_content,
            'referenced': [referenced_item for referenced_item in find_referenced_items(screensaver_content)]
        }

    response = {
        'content': content,
        'screensaver': screensaver,
        'referenced': referenced_items,
        'properties': properties,
        'configuration': configuration
    }
    return jsonify(response), 200


@app.route('/box/ping', methods=['GET'])
def on_send_ping_command():

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    now = datetime.utcnow()
    socketio.emit('pingbox', {'target': target, 'time': now.timestamp()}, room=target)
    log.info("pinging target " + target)
    return json_success("ping command sent to " + target)


@app.route('/box/reload', methods=['GET'])
def on_send_reload_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    socketio.emit('reload', {'time': now.timestamp()}, room=target)
    return json_success("box reload command sent to " + target)


@app.route('/box/reset', methods=['GET'])
def on_send_reset_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    socketio.emit('reset', {'time': now.timestamp()}, room=target)
    return json_success("box reset command sent to " + target)


@app.route('/chat/message', methods=['GET'])
def on_send_chat_text_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    text = request.args.get('text')
    socketio.emit('chatmessage', {'time': now.timestamp(), 'text': text, 'objects': []}, room=target)
    return json_success("chat message command sent to " + target)


@app.route('/notification/show', methods=['GET'])
def on_send_show_notification_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    text = request.args.get('text')
    socketio.emit('shownotification', {'time': now.timestamp(), 'text': text}, room=target)
    return json_success("notification command sent to " + target)


@app.route('/play/mediaurl', methods=['GET'])
def on_send_play_media_url_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    url = request.args.get('url')
    log.debug(f"playing media URL {url}")
    socketio.emit('playmedia', {'time': now.timestamp(), 'url': url}, room=target)
    return json_success("media playback command sent to " + target)


@app.route('/play/object/<object_id>', methods=['GET'])
def on_send_play_object_id_command(object_id):

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # find object
    item = mongo.db.objects.find_one({'id': object_id}, {'_id': False})
    if not item:
        return json_not_found_error('OBJECT_NOT_FOUND', 'object not found')
    referenced_items = find_referenced_items(item)

    # send command
    log.debug(f"playing object {item} with {len(referenced_items)} referenced item(s)")
    socketio.emit('playobject', {'time': now.timestamp(), 'object': item, 'loop': False, 'referenced': referenced_items}, room=target)
    return json_success("object playback command sent to " + target)


@app.route('/play/story', methods=['POST'])
def on_send_play_story_command():

    # find visitor type and target
    visitor_type = get_visitor_type(request.args)
    target = get_target(request.args)
    method = request.args.get('method')

    # execute story
    story = request.get_json()
    errors = execute_story(story, 'anyone', visitor_type, [target] if target else [], method == 'leave')
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success(f"story {'stopped' if method == 'leave' else 'started'} successfully")

@app.route('/play/scene/<scene_id>', methods=['GET'])
def on_send_play_scene_id_command(scene_id):

    # find visitor type
    visitor_type = get_visitor_type(request.args)
    visitor_type_id = visitor_type['id'] if visitor_type else None

    # find target
    target = get_target(request.args)

    # find avatar
    avatars = visitor_type['fields']['avatar'] if visitor_type and 'fields' in visitor_type and 'avatar' in visitor_type['fields'] else []
    avatar_id = avatars[0] if avatars else None

    # execute scene
    targets = [target] if target else []
    now = datetime.utcnow()
    storyline = str(uuid.uuid4())
    errors = execute_scene_id(now, scene_id, storyline, {'individual': 'anyone', 'avatar': avatar_id}, targets)
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("scene played")


@app.route('/play/scene', methods=['POST'])
def on_play_scene_json():

    # find visitor type
    visitor_type = get_visitor_type(request.args)
    visitor_type_id = visitor_type['id'] if visitor_type else None

    # find target
    target = get_target(request.args)

    # find avatar
    avatars = visitor_type['fields']['avatar'] if visitor_type and 'fields' in visitor_type and 'avatar' in visitor_type['fields'] else []
    avatar_id = avatars[0] if avatars else None

    # execute scene
    scene = request.get_json()
    targets = [target] if target else []
    now = datetime.utcnow()
    storyline = str(uuid.uuid4())
    errors = execute_scene(now, scene, storyline, {'individual': 'anyone', 'avatar': avatar_id}, targets)
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("scene played")


@app.route('/play/pause', methods=['GET'])
def on_send_pause_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    socketio.emit('pause', {'time': now.timestamp()}, room=target)
    return json_success("pause command sent to " + target)


@app.route('/play/resume', methods=['GET'])
def on_send_resume_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    socketio.emit('resume', {'time': now.timestamp()}, room=target)
    return json_success("resume command sent to " + target)


@app.route('/play/stop', methods=['GET'])
def on_send_stop_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # send command
    socketio.emit('stop', {'time': now.timestamp()}, room=target)
    return json_success("stop command sent to " + target)


@app.route('/play/volume', methods=['GET'])
def on_send_adjust_volume_command():

    now = datetime.utcnow()

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # get parameters
    if 'percent' not in request.args:
        return json_bad_request_error('ARGUMENT_MISSING', 'no volume argument specified')
    percent = request.args.get('percent')

    # send command
    socketio.emit('setvolume', {'time': now.timestamp(), 'volume': percent}, room=target)
    return json_success("volume command sent to " + target)


@app.route('/interaction/<scene_id>/<int:index>/<int:answer>', methods=['POST'])
def on_answer_interaction(scene_id, index, answer):

    # validate arguments
    assert index >= 0 and answer >= 0

    # get body data
    body = request.get_json()
    log.info(f"got interaction answer {answer} of {scene_id} with {body}")

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()

    # find scene
    scene = mongo.db.objects.find_one({'id': scene_id}, {'_id': False})
    if not scene or 'fields' not in scene:
        return json_not_found_error('SCENE_NOT_FOUND', 'scene not found')
    scene_fields = scene['fields']
    if 'actions' not in scene_fields:
        return json_not_acceptable_error('INVALID_ANSWER', 'invalid answer')
    log.debug(f"picked scene {scene}")

    # find action
    actions = scene_fields['actions']
    if not actions or index >= len(actions):
        return json_not_acceptable_error('INVALID_ANSWER', 'invalid answer')
    action = actions[index]
    if not action or 'fields' not in action or 'type' not in action or action['type'] != 'interaction':
        return json_not_acceptable_error('INVALID_ANSWER', 'invalid answer')
    log.debug(f"picked action {action}")

    # find option
    action_fields = action['fields']
    if 'options' not in action_fields:
        return json_not_acceptable_error('INVALID_ANSWER', 'invalid answer')
    options = action_fields['options']
    if not options or answer >= len(options):
        return json_not_acceptable_error('INVALID_ANSWER', 'invalid answer')
    option = options[answer]
    if not option or 'fields' not in option or 'type' not in option or option['type'] != 'interactioncase':
        return json_not_acceptable_error('INVALID_ANSWER', 'invalid answer')
    log.debug(f"picked option {option}")

    # find visitor type
    visitor_type = get_visitor_type(request.args)
    visitor_type_id = visitor_type['id'] if visitor_type else None

    # find avatar
    avatars = visitor_type['fields']['avatar'] if visitor_type and 'fields' in visitor_type and 'avatar' in visitor_type['fields'] else []
    avatar_id = avatars[0] if avatars else None

    # execute option
    context = body.get('context')
    errors = execute_interaction_option(datetime.utcnow(), option, context, [target])
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("interaction executed")


def find_menu_item_and_parent_by_index_list(menu, index_list):

    # check menu
    menu_fields = menu['fields']
    if 'items' not in menu_fields: return None, None
    items = menu_fields['items']

    # check index
    if len(index_list) < 1: return None, None
    index = index_list[0]
    if not items or index < 0 or index >= len(items):
        return None, None

    # find item
    item = items[index]
    if not item or 'fields' not in item: return None, None

    # return item or go deeper
    if len(index_list) > 1:
        result, parent = find_menu_item_and_parent_by_index_list(item, index_list[1:])
        return result, parent or item
    else:
        return item, None


@app.route('/menuaction/<menu_id>/<index>', methods=['POST'])
def on_post_menu_action(menu_id, index):

    # parse index
    try:
        index_list = [int(i) for i in index.split(";")]
    except:
        return json_bad_request_error('INVALID_ARGUMENTS', 'arguments must be numeric')

    # get body data
    body = request.get_json()
    log.info(f"executing menu action {index} of {menu_id} with {body}")

    # find target
    target = get_target(request.args)
    if not target:
        return json_no_command_target_found_error()
    targets = [target]

    # find object
    menu = mongo.db.objects.find_one({'id': menu_id}, {'_id': False})
    if not menu or 'fields' not in menu:
        return json_not_found_error('MENU_NOT_FOUND', 'menu not found')
    log.debug(f"picked menu {menu}")
    menu_fields = menu['fields']

    # find item
    item, parent = find_menu_item_and_parent_by_index_list(menu, index_list)
    if parent and parent.get('type') == 'menuobjectselection':
        item = parent
    if not item or 'fields' not in item:
        return json_not_acceptable_error('INVALID_ITEM', 'invalid menu item')
    item_fields = item.get('fields') or {}
    log.debug(f"picked item {item}")

    # alternative targets defined?
    # currently not possible and probably a bad idea
    # if 'target' in menu_fields and menu_fields['target']:
    #     targets = menu_fields['target']

    context = body.get('context') or {} if body else {}
    context['individual'] = context.get('individual') or 'anyone'

    # find visitor type
    visitor_type = get_visitor_type(request.args)
    visitor_type_id = visitor_type['id'] if visitor_type else None

    # find avatar
    avatars = visitor_type['fields']['avatar'] if visitor_type and 'fields' in visitor_type and 'avatar' in visitor_type['fields'] else []
    avatar_id = avatars[0] if avatars else None
    context['avatar'] = avatar_id

    # find subjects
    if item['type'] == 'menuobjectselection':
        subject_ids = item_fields.get('items') or []
        subject_id = subject_ids[index_list[-1]]
        context['subjects'] = [mongo.db.objects.find_one({'id': subject_id}, {'_id': False})]

    # execute actions
    if item['type'] == 'submenu':
        header = item_fields.get('header')
        if header:
            header_fields = header[0].get('fields') or {}
            actions = header_fields.get('actions') or []
        else:
            actions = []
    else:
        actions = item_fields.get('actions') or []
    additional_actions = menu_fields.get('additionalactions') or []
    errors = schedule_actions(datetime.utcnow(), actions + additional_actions, None, None, context, targets)
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("menu actions executed")


@app.route('/changemenu/<slot>', methods=['POST'])
def on_post_change_menu(slot):

    # find target
    target = get_target(request.args)
    if not target:
        return json_bad_request_error('TARGET_MISSING', "target missing")

    # send command
    menu = request.get_json()
    socketio.emit('changemenu', {
        'time': datetime.utcnow().timestamp(),
        'slot': slot,
        'menu': menu,
        'visible': True,
        'referencedObjects': find_referenced_items(menu)
    }, room=target)
    return json_success("menu changed")


@app.route('/showmenu/<slot>', methods=['GET'])
def on_show_menu(slot):

    # find target
    target = get_target(request.args)
    if not target:
        return json_bad_request_error('TARGET_MISSING', "target missing")

    # get parameters
    if 'visible' not in request.args:
        return json_bad_request_error('ARGUMENT_MISSING', 'no visibility argument specified')
    visibleParam = str(request.args.get('visible')).lower()
    if visibleParam in ['true', '1', 'yes']:
        visible = True
    elif visibleParam in ['false', '0', 'no']:
        visible = False
    else:
        return json_bad_request_error('INVALID_ARGUMENT', 'visibility argument invalid')

    # send command
    socketio.emit('showmenu', {'time': datetime.utcnow().timestamp(), 'slot': slot, 'visible': visible}, room=target)
    return json_success("menu shown")


@app.route('/shortcutaction/<cbox_name>/<index>', methods=['POST'])
def on_shortcut(cbox_name, index):

    try:
        index = int(index)
    except:
        return json_bad_request_error('INVALID_ARGUMENTS', 'index argument must be numeric')

    # find cbox by name
    cbox = find_box(cbox_name)
    if not cbox or 'fields' not in cbox:
        return json_not_found_error('CBOX_NOT_FOUND', 'cbox not found')
    log.debug(f"picked cbox {cbox}")

    # get body data
    body = request.get_json()
    log.info(f"executing shortcut action {index} of {cbox} with {body}")

    # find shortcut
    shortcut = cbox.get('fields').get('shortcuts')[index] if cbox.get('fields').get('shortcuts') and len(cbox.get('fields').get('shortcuts')) > index else None
    if not shortcut or 'fields' not in shortcut:
        return json_not_acceptable_error('INVALID_ITEM', 'invalid shortcut item')
    log.debug(f"picked shortcut {shortcut}")

    # execute actions
    context = body.get('context') if body else {}
    individual = context.get('individual') if context else None
    shortcut_fields = shortcut['fields']
    actions = shortcut_fields.get('actions') or []
    targets = [cbox['id']]
    errors = schedule_actions(datetime.utcnow(), actions, None, None, {'individual': individual or 'anyone'}, targets)
    if errors:
        return json_action_execution_error(errors)
    else:
        return json_success("shortcut actions executed")
