#!/bin/sh

python manage.py create_cache_folders
python manage.py initial_setup

docker-compose up -d --build