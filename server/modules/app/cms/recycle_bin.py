'''
recycle bin thread

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from datetime import (datetime, timedelta)

from app import (app, mongo, socketio)
from app.utils.config_utils import (fetch_global_config_fields)
from app.utils.api_utils import (get_field_time_seconds)


log = app.logger


def recycle_timer_thread():

    while True:
        socketio.sleep(30 * 60)
        try:
            with app.app_context():
                clean_recycle_bin()
        except Exception as e:
            log.error("recycle timer thread error: " + str(e))


def clean_recycle_bin():

    config_fields = fetch_global_config_fields()
    now = datetime.utcnow()
    autoCleanSeconds = get_field_time_seconds(config_fields, 'recylebinAutocleanInterval', 28, 'd')
    past = now - timedelta(seconds=autoCleanSeconds)
    cursor = mongo.db.objects.find({'timestamp-deleted': {'$lte': past.isoformat()}})
    for item in cursor:
        mongo.db.deletedobjects.insert_one(item)
    result = mongo.db.objects.delete_many({'timestamp-deleted': {'$lte': past.isoformat()}})
    if (result.acknowledged):
        log.info(f"deleted {result.deleted_count} objects from recycle bin before {past}")
    else:
        log.info(f"error deleting objects from recycle bin before {past}")
