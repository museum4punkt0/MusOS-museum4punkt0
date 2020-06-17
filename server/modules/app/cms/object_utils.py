'''
object handling utilities

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import os
from urllib.parse import urlparse
from datetime import (datetime, timedelta)

from app import (app, mongo)
from app.media.media_utils import (IMAGE_EXTENSIONS)

from .object_type_management import (
    get_medialist_fields
)


log = app.logger


def get_time_stamp():
    time_stamp = datetime.utcnow().isoformat()
    return time_stamp


def find_image_and_thumbnail_url(item):

    item_type = item.get('type')
    if item_type == 'mediaitem':
        return get_media_item_image_and_thumbnail_url(item)

    item_fields = item.get('fields') or {}

    # not all fields of type mediaurl are interesting
    # (for example we don't want to use object type icons as images)
    # but as a convention fields with ID imageurl or mediaurl
    # are used as suitable images
    for url_field_id in ['mediaurl', 'imageurl']:
        if url_field_id in item_fields:
            url = item_fields[url_field_id]
            if is_image_url(url):
                log.info(f"using {url} from field {url_field_id} as image for {item.get('id')}")
                return url, url # sorry, no thumbnail in this case

    # if the item does not contain direct image URL fields,
    # have a look at the media items referenced by this item
    medialist_fields = get_medialist_fields(item_type)
    for media_field_id in medialist_fields:
        if media_field_id in item_fields:
            image_url, thumbnail_url = find_media_image_and_thumbnail_url(item_fields[media_field_id])
            if image_url:
                log.info(f"using {image_url} (thumbnail {thumbnail_url}) from field {media_field_id} as image for {item.get('id')}")
                return image_url, (thumbnail_url or image_url)

    return None, None


def find_media_image_and_thumbnail_url(media_item_ids):

    for media_item_id in media_item_ids:

        # fetch items one by one to preserve order (first item first)
        media_item = mongo.db.objects.find_one({'id': media_item_id}, {'_id': False})
        if not media_item:
            continue

        image_url = media_item.get('imageurl')
        thumbnail_url = media_item.get('thumbnailurl')
        if image_url and thumbnail_url:
            return image_url, thumbnail_url

        if 'fields' in media_item:
            image_url, thumbnail_url = get_media_item_image_and_thumbnail_url(media_item)
            if image_url:
                return image_url, thumbnail_url

    return None, None


def get_media_item_image_and_thumbnail_url(item):

    # find image URL if available
    item_fields = item.get('fields') or {}
    url = item_fields.get('url')
    image_url = url if url and is_image_url(url) else None

    # also return thumbnail URL if available
    # (videos might have a thumbnail but no image)
    media_info = item.get('mediainfo') or {}
    thumbnail_url = media_info.get('thumbnail')
    return (image_url or thumbnail_url), (thumbnail_url or image_url)


def is_image_url(url):
    if not url: return False
    name, extension = os.path.splitext(os.path.basename(urlparse(url).path))
    return extension and extension[1:].lower() in IMAGE_EXTENSIONS


def check_user_exists(email):
    check_user = mongo.db.objects.find_one({'fields.email': email}, {"_id": False})
    if check_user:
        return True
    else:
        return False


def strip_item(item):
    # only return relevant information for presentation etc. (without users, timestamps etc.)
    item_type = item.get('type')
    if item_type == 'mediaitem':
        return {
            'id': item.get('id'),
            'type': item.get('type'),
            'title': item.get('title'),
            'fields': item.get('fields') or {},
            'tags': item.get('tags') or [],
            'imageurl': item.get('imageurl'),
            'mediainfo': item.get('mediainfo')
        }
    else:
        return {
            'id': item.get('id'),
            'type': item.get('type'),
            'title': item.get('title'),
            'fields': item.get('fields') or {},
            'tags': item.get('tags') or [],
            'imageurl': item.get('imageurl')
        }


def fetch_single_referenced_item(reference_ids):
    if not reference_ids:
        return None
    else:
        return mongo.db.objects.find_one({'id': reference_ids[0]}, {'_id': False})


def fetch_multiple_referenced_items(reference_ids):
    if not reference_ids:
        return None
    else:
        return list(mongo.db.objects.find({'id': {'$in': reference_ids}}, {'_id': False}))


def extract_referenced_item_ids(item):

    if not item or 'type' not in item or 'fields' not in item:
        return []
    fields = item['fields']
    referenced_ids = []

    if item['type'] == 'textslide':
        referenced_ids.extend(fields.get('images') or [])
        referenced_ids.extend(fields.get('backgroundImage') or [])
        referenced_ids.extend(fields.get('style') or [])

    elif item['type'] == 'objectinfopanel':
        referenced_ids.extend(fields.get('style') or [])

    elif item['type'] in ['menuframe', 'submenu']:
        subitems = fields.get('items') or []
        for subitem in subitems:
            referenced_ids.extend(extract_referenced_item_ids(subitem))

    elif item['type'] == 'menuobjectselection':
        subject_ids = fields.get('items') or []
        referenced_ids.extend(subject_ids)
        tags = fields.get('imagetags')
        if subject_ids and tags:
            subject_media_cursor = mongo.db.objects.find(
                {'id': {'$in': subject_ids}},
                {'fields.medialist': True, '_id': False}
            ) # TODO: does not work for media item fields with other name (also see MenuFrame.js)
            subject_media_ids = [
                media_id for subject in subject_media_cursor for media_id in (subject['fields'].get('medialist') or [])
            ] # TODO: does not work for media item fields with other name (also see MenuFrame.js)
            tagged_media_items_cursor = mongo.db.objects.find(
                {'id': {'$in': subject_media_ids}, 'tags': {'$all': tags}},
                {'_id': False}
            )
            tagged_media_ids = [
                media_item['id'] for media_item in tagged_media_items_cursor
            ]
            referenced_ids.extend(tagged_media_ids)

    return referenced_ids


def find_referenced_items(item, stripped = True):

    referenced_ids = extract_referenced_item_ids(item)
    if referenced_ids:
        cursor = mongo.db.objects.find({'id': {'$in': referenced_ids}}, {'_id': False})
        if stripped:
            return [strip_item(item) for item in cursor]
        else:
            return [item for item in cursor]
    else:
        return []

