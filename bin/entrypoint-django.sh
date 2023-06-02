#!/bin/sh

python manage.py migrate
python manage.py create_cache_folders
python manage.py collectstatic --noinput
exec gunicorn EcgAnalysis.wsgi:application --bind 0.0.0.0:8000 --workers 3
