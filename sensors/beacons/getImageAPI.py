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
from fastapi.responses import FileResponse
import math
import configparser
import requests
import uuid
import socket
import servercommunication

# for exposing the REST API on Station MaskScanner
app = FastAPI()

config = configparser.ConfigParser()
config.read('maskstation.ini')

imagePath = config['maskstation']['imagedir']


# Get MaskScanner Image for further usage in visitor stations
@app.get("/image/{beacon_id}")
async def getImageForId(image_id: str):
scannerImage = findImageWithPrefix(beaconId) 
    if scannerImage is not None:
    	return FileResponse(scannerImage)
    else:
        return	

def findImageWithPrefix(beaconId: str):
for file in os.listdir(imagepath):
    if file.startswith(beaconId):
        return file:
    else:
    	return 




