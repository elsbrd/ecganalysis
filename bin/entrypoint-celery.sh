#!/bin/sh

python manage.py migrate
python manage.py create_cache_folders

celery -A EcgAnalysis worker --loglevel=info