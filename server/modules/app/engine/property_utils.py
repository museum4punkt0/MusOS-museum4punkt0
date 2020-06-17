'''
state property utilities

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


import random
from datetime import datetime
from app import (app, mongo)


log = app.logger


def get_property_key(property_id, individual = None):

    property_definition = mongo.db.objects.find_one({'id': property_id}, {'_id': False})
    if not property_definition or 'fields' not in property_definition:
        log.warning(f"state property with ID {property_id} not found")
        return None

    category = property_definition['fields']['category'] if 'category' in property_definition['fields'] else None
    if category == 'globalstate':
        return {'individual': 'global', 'property': property_id}
    else:
        return {'individual': individual, 'property': property_id}


def get_property_key_by_name(property_name, individual = None):

    property_definition = mongo.db.objects.find_one({'type': 'stateproperty', 'fields.name': property_name}, {'_id': False})
    if not property_definition or 'fields' not in property_definition:
        log.warning(f"state property with name {property_name} not found")
        return None

    property_id = property_definition['id']
    category = property_definition['fields']['category'] if 'category' in property_definition['fields'] else None
    if category == 'globalstate':
        return {'individual': 'global', 'property': property_id}
    else:
        return {'individual': individual, 'property': property_id}


def find_property_value_for_key(property_key):

    if not property_key:
        return None

    property_item = mongo.db.propertyvalues.find_one(property_key)
    if property_item:
        return property_item.get('value')
    else:
        log.debug(f"property value for {property_key} not available")
        return None
    

def find_property_value_for_id(property_id, individual = None):

    if not property_id:
        log.warning("property ID missing")
        return None

    property_key = get_property_key(property_id, individual)
    return find_property_value_for_key(property_key)


def find_property_value_by_name(property_name, individual = None):

    if not property_name:
        log.warning("property name missing")
        return None

    property_key = get_property_key_by_name(property_name, individual)
    return find_property_value_for_key(property_key)


def parseMinutesFromTime(value):

    try:
        parsed = datetime.strptime(value, '%H:%M')
        return parsed.hour * 60 + parsed.minute; 
    except:
        return None

def evaluate_conditions(conditions, context):

    for condition in conditions:
        if 'type' not in condition or 'fields' not in condition: continue
        conditionType = condition['type']
        fields = condition['fields']
        inverse = fields.get('inverse') or False
    
        if conditionType == 'exactvaluecondition':
            property_ids = fields.get('property') or [None]
            property_value = find_property_value_for_id(property_ids[0], context.get('individual')) or 0
            value = fields.get('value') or 0
            try:
                if (float(property_value) == float(value)) == inverse:
                    return False
            except:
                if (str(property_value) == str(value)) == inverse:
                    return False

        elif conditionType == 'rangecondition':
            property_ids = fields.get('property') or [None]
            property_value = find_property_value_for_id(property_ids[0], context.get('individual')) or 0
            min_value = fields.get('min') or 0
            max_value = fields.get('max') or 0
            log.debug(f"rangecondition {min_value} <= {property_value} <= {max_value} ({'inverse' if inverse else 'normal'})")
            try:
                if (float(min_value) <= float(property_value) <= float(max_value)) == inverse:
                    return False
            except:
                if not inverse:
                    return False

        elif conditionType == 'randomcondition':
            probability = fields.get('probability') or 0
            number = random.random() * 100
            if number >= probability:
                return False

        elif conditionType == 'timecondition':
            from_time_minutes = parseMinutesFromTime(fields.get('from'))
            to_time_minutes = parseMinutesFromTime(fields.get('to'))
            if from_time_minutes is not None and to_time_minutes is not None:
                local_now = datetime.now()
                now_minutes = local_now.hour * 60 + local_now.minute
                log.info(f"time condition {from_time_minutes} - {to_time_minutes} at {now_minutes} ({local_now})")
                if from_time_minutes > to_time_minutes:
                    if (to_time_minutes <= now_minutes < from_time_minutes) == inverse:
                        return False
                else:
                    if (from_time_minutes <= now_minutes < to_time_minutes) == inverse:
                        return False


    return True
