#!/usr/bin/env bash

echo "Installing required bluetooth libraries and a simple Rest server for Mask Scanner..."
sudo apt-get update
sudo apt-get install bluetooth
sudo apt-get install bluez
sudo apt-get install python-bluez

sudo apt-get install python-dev libbluetooth-dev libcap2-bin
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python))
pip3 install beacontools[scan]
sudo pip3 install beacontools[scan]


echo "Installing beaconsensor service..."
sudo cp beaconsensor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable beaconsensor.service

sudo pip install fastapi
sudo pip install "uvicorn[standard]"

