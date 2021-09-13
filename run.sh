#!/bin/bash


# Run db migrations
python3 manage.py migrate

# Creating the cache table
python3 manage.py createcachetable --database cache_db

# Running development server
python3 manage.py runserver 0.0.0.0:8000
