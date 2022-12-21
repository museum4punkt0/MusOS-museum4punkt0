'''
bluetooth beacon sensor for MusOS / Pulsar mit Erweiterung zur Integration der Station Maskenscanner. 
Der Bluetooth Beacon sensor wurde erweitert, um ankommende Besucher*innen zu registrieren, deren 
Übermittelte UUID zu ermitteln und per REST-Interface dem Maskenscanner zur Verfügung zu stellen. 
Diese wird dem Bild-File als Prefix angehängt und ist so der Besucher*in eindeutig zuzuordnen für eine
spätere Verwendung in der Ausstellung des Fasnachtsmusuem Schloss Langenstein. 
:authors: Maurizio Tidei, Jens Gruschel, Sascha Lorenz
:copyright: © 2019, 2022 contexagon GmbH
'''


import time
from beacontools import BeaconScanner, IBeaconFilter
from collections import deque
from fastapi import FastAPI
import math
import configparser
import requests
import uuid
import socket
import servercommunication

# for exposing the REST API on Beacon sensor RaspPi
app = FastAPI()

config = configparser.ConfigParser()
config.read('beaconsensor.ini')

sensor_name = config['beaconsensor']['sensorName']
server_url = config['beaconsensor']['serverUrl']
# threshold_near_low  = float(config['beaconsensor']['thresholdNearLow'])
# threshold_near_high = float(config['beaconsensor']['thresholdNearHigh'])
beaconIdAsPrefix = None
beacon_ranges = []
range_signature = None
triggered = []

def fetch_configuration():
    global beacon_ranges, range_signature, triggered
    print(f"waiting for {server_url}...")
    while True:
        beacon_ranges, range_signature = servercommunication.request_sensor_info(server_url, sensor_name)
        if beacon_ranges:
            triggered = [{} for beacon_range in beacon_ranges]
            break
        time.sleep(5)

fetch_configuration()


time.sleep(15)


ring_buffer_size = int(config['beaconsensor']['ringBufferSize'])
buffer = dict()
distance_buffer = dict()

filter_uuid = config['beaconsensor'].get('filterUuid')
filter_major = config['beaconsensor'].get('filterMajor')
filter_minor = config['beaconsensor'].get('filterMinor')
if filter_major:
    filter_major = int(filter_major)
if filter_minor:
    filter_minor = int(filter_minor)


session_id = str(uuid.uuid1()).replace("-","")

print(f"starting Beacon Sensor named {sensor_name}...")


# a beacon packet was received
def callback(bt_addr, rssi, packet, additional_info):

    beacon_id = create_beacon_id(additional_info)
    baeconIdAsPrefix = beacon_id
    if beacon_id not in buffer:
        buffer[beacon_id] = deque(maxlen=ring_buffer_size)
        distance_buffer[beacon_id] = deque(maxlen=ring_buffer_size)

    buffer[beacon_id].append(rssi)
    #print("buffer: %s" % buffer)

    distance = calculate_distance(rssi, packet.tx_power)
    if distance < 0:
        return

    distance_buffer[beacon_id].append(distance)
    #print("distance_buffer: %s" % distance_buffer)

    if len(distance_buffer[beacon_id]) < ring_buffer_size:
        return # wait for more values

    avg_rssi = sum(buffer[beacon_id]) / float(len(buffer[beacon_id]))
    avg_distance = sum(distance_buffer[beacon_id]) / float(len(distance_buffer[beacon_id]))

    for index, beacon_range in enumerate(beacon_ranges):
        if avg_distance <= beacon_range['nearthreshold'] and not triggered[index].get(beacon_id, False):
            trigger(beacon_id, index)
            triggered[index][beacon_id] = True # already fired
        elif avg_distance > beacon_range['farthreshold'] and triggered[index].get(beacon_id, False):
            trigger(beacon_id, index, untrigger=True)
            triggered[index][beacon_id] = False # ready to fire again


# create beacon id from info dict
def create_beacon_id(info):
    #print(info)
    return str(info['uuid']) + "-" + str(info['major']) + "-" + str(info['minor'])


# calculate distance based on rssi and tx_power
def calculate_distance(rssi, tx_power):
    if rssi == 0 or tx_power == 0:
        return -1
    else:
        ratio_db = tx_power - rssi
        ratio_linear = 10 ** (ratio_db / 10.0)
        r = math.sqrt(ratio_linear)
        return r


# trigger/untrigger beacon/badge
def trigger(beacon_id, range_index, untrigger=False):
    global beacon_ranges, range_signature, triggered
    code = servercommunication.trigger_sensor(server_url, sensor_name, range_index, untrigger, beacon_id, range_signature)
    if code == 410:
        print(f"signature is not valid any more, ranges have changed")
        fetch_configuration()
    elif code < 300:
        ping_server(f"{'untriggered' if untrigger else 'triggered'} {beacon_id} range {range_index}")


# heartbeat signal
def ping_server(info=None):
    servercommunication.send_alive_ping(server_url, sensor_name, session_id, ip_address, info)


# get own primary ip
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = 'unknown'
    finally:
        s.close()
    return ip

# Get Beacon ID as Prefix for MaskScanner_Image
@app.get("/getbeaconid")
async def getBeaconId():
    if beaconIdAsPrefix is not None:
    	return beaconIdAsPrefix
    else:
        return	
        

# scan for all iBeacon advertisements from beacons with the specified uuid
scanner = BeaconScanner(callback,
    device_filter=IBeaconFilter(uuid=filter_uuid, major=filter_major, minor=filter_minor)
)

ip_address = get_ip()
print("ip: " + ip_address)

try:
    scanner.start()

    while True:
        ping_server()
        time.sleep(5)
except Exception as e:
    print(e)
    scanner.stop()
except KeyboardInterrupt:
    scanner.stop()
