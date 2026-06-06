#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput --clear
cp -r /app/collect_static/. /backend_static/static/

exec "$@"