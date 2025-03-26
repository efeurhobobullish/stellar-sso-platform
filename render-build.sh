#!/usr/bin/env bash
set -o errexit

# Install system dependencies
apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    cargo \
    gcc \
    g++

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput