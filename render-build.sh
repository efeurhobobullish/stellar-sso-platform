#!/usr/bin/env bash
set -o errexit  

# Install system dependencies
apt-get update && apt-get install -y python3.11-dev libpq-dev gcc build-essential

# Upgrade pip & install dependencies
pip install --upgrade pip  
pip install --no-cache-dir -r requirements.txt