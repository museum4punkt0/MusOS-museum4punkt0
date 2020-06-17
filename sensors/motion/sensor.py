#!/usr/bin/python

'''
Lightweight Raspberry Pi sensor for MusOS / Pulsar

use sensor.ini for configuration

:author: Maurizio Tidei
:copyright: © 2019 contexagon GmbH
'''


import RPi.GPIO as GPIO
import time
import configparser
import requests

TRIG = 0
ECHO = 0
PIR = 0

mode = ""
distanceThreshold = 0
restUrl = ""
retriggerTime = 0

lastTriggerTime = 0
startTime = 0
triggered = False


def setup():
    
    global restUrl, retriggerTime, distanceThreshold, TRIG, ECHO, PIR, mode
    
    config = configparser.ConfigParser()
    config.read('sensor.ini')
    restUrl = config['sensor']['url']
    distanceThreshold = int(config['sensor']['distance'])
    retriggerTime = int(config['sensor']['time'])
    TRIG = int(config['sensor']['trig'])
    ECHO = int(config['sensor']['echo'])
    PIR = int(config['sensor']['pir'])
    mode = config['sensor']['mode']
    
    print("Starting Sensor with Configuration:")
    print("mode:" + mode)
    print("url:" + restUrl)
    print("distance:" + str(distanceThreshold))
    print("time:" + str(retriggerTime))
    print("TRIG:" + str(TRIG))
    print("ECHO:" + str(ECHO))
    print("PIR:" + str(PIR), flush=True)
    
    if(mode == "PIR"):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(PIR, GPIO.IN)
    else:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)


def trigger():
    global triggered, lastTriggerTime
    timePassed = time.time() - lastTriggerTime
    print('Time passed: ' + str(timePassed) + 's', flush=True)
    if not triggered and timePassed >= retriggerTime:
        print('--> Triggering sensor ' + restUrl, flush=True)
        # call REST API
        response = requests.get(restUrl)
        print(' response:' + response.text[:500], flush=True)
        triggered = True
        lastTriggerTime = time.time()


def untrigger():
    global triggered
    triggered = False


def get_distance():
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(ECHO) == 1:
        a = 1
    time2 = time.time()

    diff = time2 - time1
    return diff * 340 / 2 * 100


def loop_ultrasonic():
    while True:
        dis = get_distance()
        print(dis + 'cm', flush=True)
        if dis < distanceThreshold:
            trigger()
        elif dis < 500: # real distance, not timeout
            untrigger()
        time.sleep(0.3)


def trigger_pir(arg):
    print('PIR 1', flush=True)
    print('Time since start: ' + str(time.time() - startTime) , flush=True)
    trigger()
    # wait for no motion
    while(GPIO.input(PIR)):
        print('PIR still 1', flush=True)
        time.sleep(1)
    print('PIR 0', flush=True)
    untrigger()


def loop_pir():
    GPIO.add_event_detect(PIR, GPIO.RISING, callback=trigger_pir, bouncetime=100)
    while True:
        time.sleep(1)


def destroy():
    GPIO.cleanup()


startTime = time.time()
print('Sensor started.', flush=True)
if __name__ == "__main__":
    setup()
    try:
        if(mode == "PIR"):
            loop_pir()
        else:
            loop_ultrasonic()
    except KeyboardInterrupt:
        destroy()
