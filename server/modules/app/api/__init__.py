'''
Flask APIs and socket.io APIs initialization

:author: Sascha Lorenz
:copyright: © 2018 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import os
import glob

from flask_cors import CORS

from app import app


CORS(app)

__all__ = [os.path.basename(f)[:-3]
    for f in glob.glob(os.path.dirname(__file__) + "/*.py")]