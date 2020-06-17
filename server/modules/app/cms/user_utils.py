'''
user utilities

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from app import (app, mongo)


def find_user(user_id):
    return mongo.db.objects.find_one({'type': 'user', 'fields.email': user_id, 'timestamp-deleted': {'$exists': False}}, {'_id': False})
