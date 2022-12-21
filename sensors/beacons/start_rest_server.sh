#!/usr/bin/env bash

echo "Starting ASGI Server to enable Rest calls..."

sudo uvicorn main:app --reload

