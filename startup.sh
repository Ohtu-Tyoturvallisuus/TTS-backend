#!/bin/bash

# Install ffmpeg
apt-get update && apt-get install -y ffmpeg

# Run app
gunicorn --bind=0.0.0.0 --timeout 600 tts.wsgi
