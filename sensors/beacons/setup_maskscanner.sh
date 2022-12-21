#!/usr/bin/env bash

echo "Setting up Mask Scanner Environment for integration in MusOS..."

sudo pip install fastapi
sudo pip install "uvicorn[standard]"
sudo mkdir /scannerimages

