#!/bin/sh
rm -rf /app/celerybeat.pid
python manage.py migrate
python manage.py install_labels
python manage.py runserver_plus 0.0.0.0:8000
