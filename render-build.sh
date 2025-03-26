#!/bin/bash

# Install required system packages
apt-get update && apt-get install -y build-essential python3-dev libssl-dev libffi-dev python3-pip

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt