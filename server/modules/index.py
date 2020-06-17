'''
server application index file

:authors: Sascha Lorenz, Maurizio Tidei, Jens Gruschel
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import os
import sys

from flask import (jsonify, send_from_directory)

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
os.environ.update({'ROOT_PATH': ROOT_PATH})
sys.path.append(os.path.join(ROOT_PATH, 'modules'))

LOGFILE_PATH = os.path.join(os.environ.get('SERVERLOG_PATH', '/var/log/server'), 'server.log')

import logging
import logging.handlers
from app import (app, socketio)
from flask.logging import default_handler

# configure flask logger
debug = os.environ.get('ENV', 'development') == 'development'
log = app.logger

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s')

ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

fh = logging.handlers.RotatingFileHandler(LOGFILE_PATH, maxBytes=1024 * 1024 * 2, backupCount=20)
fh.setFormatter(formatter)
log.addHandler(fh)

log.setLevel(logging.DEBUG if debug else logging.INFO)


# remove flask's default handler, since we want to use our own
app.logger.removeHandler(default_handler)


# Port variable to run the server on.
PORT = os.environ.get('PORT')


@app.errorhandler(404)
def not_found(error):
    """ error handler """
    log.error(error)
    response = {'error_id': 'NOT_FOUND', 'message': 'requested resource could not be found'}
    return jsonify(response), 404


@socketio.on_error()
def error_handler(e):
    log.error(e)


@app.route('/')
def on_get_index():
    """ static files serve """
    log.info("serving static index file")
    return send_from_directory('/appdata/public', 'index.html')


@app.route('/<path:path>')
def on_get_static_proxy(path):
    """ static folder serve """
    log.info("serving static path " + path)
    path_parts = path.split('/')
    file_name = path_parts[-1]
    # use special folder for customer content if path starts with "content"
    if path_parts[0] == 'content':
        dir_name = '/'.join(path_parts[1:-1])
        local_dir_name = os.path.join('/var/usercontent', dir_name)
        log.debug("serving local content file " + file_name + " from " + local_dir_name)
        return send_from_directory(local_dir_name, file_name)
    # otherwise serve files from public folder
    else:
        dir_name = '/'.join(path_parts[:-1])
        local_dir_name = os.path.join('/appdata/public', dir_name)
        log.debug("serving local file " + file_name + " from " + local_dir_name)
        return send_from_directory(local_dir_name, file_name)


@app.route('/server/pyinfo')
def on_get_server_info():
    import pyinfo
    return pyinfo.info_as_html()


if __name__ == '__main__':
    log.info('MusOS Server started. Running environment: %s', os.environ.get('ENV'))
    app.config['DEBUG'] = os.environ.get('ENV') == 'development'  # Debug mode if development env
    app.config['LOGFILE_PATH'] = LOGFILE_PATH

    # app.run(host='0.0.0.0', port=int(PORT), threaded=True) # Run the app (threaded does not work with socketio)

    # run the app wrapped by socketio
    socketio.run(app, host='0.0.0.0', port=int(PORT))
