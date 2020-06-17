'''
bluetooth beacon sensor server communication

:authors: Maurizio Tidei, Jens Gruschel
:copyright: © 2020 contexagon GmbH
'''


import requests
from requests.exceptions import HTTPError


def request_sensor_info(server_url, sensor_name):

    url = f"{server_url}/configuration/badgesensor/{sensor_name}"
    print(f"calling url {url}")
    try:
        response = requests.get(url)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None, None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None, None

    else:
        if response.status_code < 300:
            data = response.json()
            beacon_ranges = data.get('ranges') or []
            range_signature = data.get('signature')
            print(f"beacon ranges: {beacon_ranges}")
            return beacon_ranges, range_signature
        
        else:
            print(f"server responded with {response.text}")
            return None, None


def trigger_sensor(server_url, sensor_name, range_index, untrigger, beacon_id, range_signature):

    method = 'leave' if untrigger else 'enter'
    url = f"{server_url}/trigger/badgesensor/{sensor_name}/{range_index}?badge={beacon_id}&method={method}&signature={range_signature}"
    print(f"calling url {url}")
    try:
        response = requests.get(url)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return 999
    except Exception as err:
        print(f'Other error occurred: {err}')
        return 999
    else:
        print(f"server responded with {response.text}")
        return response.status_code


def send_alive_ping(server_url, sensor_name, session_id, ip_address, info=None):
    url = f"{server_url}/alive/{session_id}?type=sensor&name={sensor_name}&ip={ip_address}"
    if info:
        url += "&info=" + info
    print(f"calling url {url}")
    try:
        response = requests.get(url)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print(f"response: {response.text}")