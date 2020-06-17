'''
configuration access utilities

:author: Jens Gruschel
:copyright: © 2020 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


from app import mongo


def fetch_global_config_fields():

    config_object = mongo.db.objects.find_one({'id': 'configuration.active'})
    if not config_object:
        return {}
    else:
        return config_object.get('fields') or {}


def get_parameter_key(parameter_item):

    fields = parameter_item.get('fields') or {}
    return fields.get('key')


def get_parameter_value(parameter_item):

    fields = parameter_item.get('fields') or {}
    return fields.get('value')


def create_config_parameter_map(config_fields):

    config_parameters = config_fields.get('parameters') or []
    return {get_parameter_key(item): get_parameter_value(item) for item in config_parameters}
