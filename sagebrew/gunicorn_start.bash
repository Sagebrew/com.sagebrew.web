#!/bin/bash

PROJECT_PATH=/home/apps/$REPO_NAME/$REPO_NAME/
NAME=$REPO_NAME
DJANGODIR=$PROJECT_PATH/
SOCKFILE=$PROJECT_PATH/run/gunicorn.sock
USER=$APP_USER
GROUP=$APP_USER
NUM_WORKERS=$WEB_WORKER_COUNT
DJANGO_SETTINGS_MODULE=$PROJECT_NAME.settings
DJANGO_WSGI_MODULE=$PROJECT_NAME.wsgi
 
echo "Starting $NAME"
 
# Activate the virtual environment
cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec NEW_RELIC_CONFIG_FILE=/home/apps/newrelic.ini newrelic-admin run-program gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --bind=unix:$SOCKFILE
