'''
API for socket communication (boxes and mobile devices)

:authors: Jens Gruschel, Maurizio Tidei
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import os
import logging
from datetime import (datetime)
from flask import (request, jsonify)
from flask_socketio import (join_room, leave_room)

from app import (app, socketio, mongo)
from app.utils.api_utils import (find_box, find_sensor)
from app.utils.api_responses import (json_success, json_bad_request_error)


log = app.logger
socketio_sessions = {}


@socketio.on('connect')
def on_connect():
    global socketio_sessions
    sid = request.sid
    now = datetime.utcnow().timestamp()
    socketio_sessions[sid] = {'sid': sid, 'connected': True, 'connect_time': now, 'alive_time': now}
    log.info(f"socket connected for session {sid}")
    # remove all sessions not alive for more than 10 minutes (maybe put this elsewhere?)
    socketio_sessions = {k: v for k, v in socketio_sessions.items() if now - v['alive_time'] < 600}


@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    log.info(f"socket disconnected for session {sid}")
    if sid in socketio_sessions:
        now = datetime.utcnow().timestamp()
        socketio_sessions[sid]['connected'] = False
        socketio_sessions[sid]['disconnect_time'] = now


@socketio.on('pongbox')
def on_pong_box(data):
    now = datetime.utcnow().timestamp()
    ping_time = datetime.utcfromtimestamp(data['time'])
    roundtrip_duration = now - ping_time
    log.info(f"ping to {data['boxname']} on {data['target']} took {roundtrip_duration}")


@socketio.on('pingserver')
def on_ping_server(data):
    emit('pongserver', data)
    log.info("server pinged")


@socketio.on('alive')
def on_alive(data):
    now = datetime.utcnow().timestamp()
    sid = request.sid
    if sid not in socketio_sessions: socketio_sessions[sid] = {'sid': sid, 'connect_time': now}
    socketio_sessions[sid]['connected'] = True
    socketio_sessions[sid]['alive_time'] = now
    socketio_sessions[sid]['active'] = data.get('active') if data else None
    activity = data.get('activity') if data else None
    if activity:
        socketio_sessions[sid]['activity'] = activity


@socketio.on('joinbox')
def on_join_box(data):
    sid = request.sid
    if 'name' not in data:
        log.error(f"box without name cannot join for session {sid}")
        return
    now = datetime.utcnow().timestamp()
    box_name = data['name']
    box = find_box(box_name)
    if box and 'id' in box:
        channels = set(box['fields']['channels']) if 'fields' in box and 'channels' in box['fields'] else set()
        channels.add(box['id'])
        channels.add('channel.allboxes')
        channels.add('channel.broadcast')
        for channel in channels:
            join_room(channel)
        if sid not in socketio_sessions: socketio_sessions[sid] = {'sid': sid, 'connect_time': now}
        socketio_sessions[sid]['connected'] = True
        socketio_sessions[sid]['alive_time'] = now
        socketio_sessions[sid]['type'] = 'box'
        socketio_sessions[sid]['name'] = box_name
        socketio_sessions[sid]['channels'] = channels
        socketio_sessions[sid]['env'] = extract_env(request.environ)
        log.info(f"box {box_name} joined {list(channels)} for session {sid}")
    else:
        if sid not in socketio_sessions: socketio_sessions[sid] = {'sid': sid, 'connect_time': now}
        socketio_sessions[sid]['connected'] = True
        socketio_sessions[sid]['alive_time'] = now
        socketio_sessions[sid]['error'] = f"box {box_name} not found"
        log.error(f"box {box_name} not found")


@app.route('/state/connections', methods=['GET'])
def on_get_connection_state():
    return jsonify({'connections': list(socketio_sessions.values()), 'time': datetime.utcnow().timestamp()}), 200


@app.route('/box/halt/<sid>', methods=['GET'])
def on_halt_box(sid):
    if sid in socketio_sessions:
        channels = socketio_sessions[sid].get('channels') or []
        for channel in channels:
            leave_room(channel, sid = sid, namespace = '/')
        socketio_sessions[sid]['channels'] = []
        socketio.emit('halt', {}, room=sid)
        log.info(f"device {socketio_sessions[sid].get('name')} halted leaving channels {list(channels)} for session {sid}")


@app.route('/alive/<sid>', methods=['GET'])
def on_update_alive(sid):

    if 'type' not in request.args:
        return json_bad_request_error("ARGUMENT_MISSING", "device type missing")
    device_type = request.args['type']
    if device_type not in ['box', 'sensor', 'mobile']:
        return json_bad_request_error("INVALID_ARGUMENT", "invalid device type")

    if 'name' not in request.args:
        return json_bad_request_error("ARGUMENT_MISSING", "device name missing")
    device_name = request.args['name']

    now = datetime.utcnow().timestamp()
    if sid not in socketio_sessions: socketio_sessions[sid] = {'sid': sid, 'connect_time': now, 'env': {}}
    socketio_sessions[sid]['type'] = device_type
    socketio_sessions[sid]['name'] = device_name
    socketio_sessions[sid]['connected'] = True
    socketio_sessions[sid]['alive_time'] = now
    socketio_sessions[sid]['env']['REMOTE_ADDR'] = request.args.get('ip', default='-')

    info = request.args.get('info')
    activity_description = info + " " + str(datetime.utcnow()) if info else request.args.get('activity')
    if activity_description:
        socketio_sessions[sid]['activity'] = activity_description

    return json_success("alive state updated")


def extract_env(env):
    return {
        # 'SERVER_NAME': env.get('SERVER_NAME'),
        # 'SERVER_PORT': env.get('SERVER_PORT'),
        # 'HTTP_ACCEPT_LANGUAGE': env.get('HTTP_ACCEPT_LANGUAGE'),
        # 'HTTP_REFERER': env.get('HTTP_REFERER'),
        # 'HTTP_ORIGIN': env.get('HTTP_ORIGIN'),
        'REMOTE_ADDR': env.get('REMOTE_ADDR'),
        'REMOTE_PORT': env.get('REMOTE_PORT'),
        'HTTP_HOST': env.get('HTTP_HOST'),
        'HTTP_USER_AGENT': env.get('HTTP_USER_AGENT')
    }