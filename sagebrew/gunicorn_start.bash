#!/bin/bash

PROJECT_PATH=/home/apps/$PROJECT_REPONAME/$APP_NAME/
NAME=$APP_NAME
DJANGODIR=/home/apps/$PROJECT_REPONAME/$APP_NAME/
SOCKFILE=/home/apps/$PROJECT_REPONAME/$APP_NAME/run/gunicorn.sock
USER=$APP_USER
GROUP=$APP_USER
NUM_WORKERS=$WEB_WORKER_COUNT
DJANGO_SETTINGS_MODULE=$APP_NAME.settings
DJANGO_WSGI_MODULE=$APP_NAME.wsgi
 
echo "Starting $NAME"
 
# Activate the virtual environment
cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH
export NEW_RELIC_CONFIG_FILE=/home/apps/newrelic.ini

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec newrelic-admin run-program gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --bind=unix:$SOCKFILE
