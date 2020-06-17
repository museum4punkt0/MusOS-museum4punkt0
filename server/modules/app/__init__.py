'''
application intialization, setting up Flask, MongoDB
and starting background threads

:authors: Sascha Lorenz, Jens Gruschel, Maurizio Tidei
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import os
import json
import datetime
import sys
from bson.objectid import ObjectId
from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from engineio.payload import Payload


# increase the number of packets (16 is a bit low), see
# https://github.com/miguelgrinberg/python-engineio/issues/142
Payload.max_decode_packets = 64


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


# create the flask object
app = Flask(__name__, static_folder=None)
app.config['MONGO_URI'] = os.environ.get('DB')
app.config['JWT_SECRET_KEY'] = os.environ.get('JSON_WEB_TOKEN_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
mongo = PyMongo(app)
flask_bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.json_encoder = JSONEncoder
socketio = SocketIO(app, cors_allowed_origins='*')


from app.api import *  # pylint: disable=W0401,C0413
from app.engine.action_engine import (action_timer_thread)
from app.cms.recycle_bin import (recycle_timer_thread)
from app.cms.authorization_management import (refresh_type_access_map, refresh_role_info_map)
from app.cms.object_type_management import (refresh_all_object_types)


# log uncaught exceptions
def musos_exception_handler(type, value, traceback):
    app.logger.exception(f"Uncaught exception {type}: {value}")
    app.logger.exception(f"Exception traceback: {traceback}")

sys.excepthook = musos_exception_handler


# initialize global data
with app.app_context():
    refresh_type_access_map()
    refresh_role_info_map()
    refresh_all_object_types()


# start threads
socketio.start_background_task(action_timer_thread)
socketio.start_background_task(recycle_timer_thread)