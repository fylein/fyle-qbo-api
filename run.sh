#!/bin/bash


# Setting environment variables
source setup.sh

# Run db migrations
python3 manage.py migrate

# Running development server
python3 manage.py runserver 0.0.0.0:8000
