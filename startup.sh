#!/bin/bash

# Install ffmpeg
apt-get update && apt-get install -y ffmpeg

# Apply database migrations
python manage.py makemigrations || exit 1
python manage.py migrate || exit 1

# Run app
gunicorn --bind=0.0.0.0 --timeout 600 tts.wsgi
