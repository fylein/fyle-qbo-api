#!/bin/bash


# Run db migrations
python manage.py migrate

# Running development server
gunicorn -c gunicorn_config.py fyle_qbo_api.wsgi -b 0.0.0.0:8000
