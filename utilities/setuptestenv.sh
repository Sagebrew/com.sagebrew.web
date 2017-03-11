#!/bin/bash

#
# This script is really bad, so basically we need to dynamically generate the .env file for tests prior to running the
# Docker commands.
# Problems:
#  1) Process of greping the entire env misses some vars
#  2) If the grep fails to find anything it returns back exit code 1 resulting in a failed build. but fails silently and no easy way to debug.
#  3) Not sure if just env piping the entire env to .env would result in something going haywire or not. (should probably just test that as it would be a lot easier, but i'm not confident it won't break things.)

touch ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep CIRCLE_  > ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep DJANGO_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep SAGEBREW  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep DATABASE_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep APPLICATION_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep REDIS  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep ADDRESS  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep ADMIN  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep ALCHEMY  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep AMAZON  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep APP_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep AWS_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep CACHE_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep BOMBERMAN_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep CELERY_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep COVERALLS_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep CRED_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep DOCKER_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep ELASTIC  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep GOOGLE  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep INTERCOM  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep LOGENT  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep MASKED  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep NEO4J  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep NEW  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep OAUTH  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep OPBEAT  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep PROJECT  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep PX  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep QUEUE  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep RDS  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep REPO  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep STRIPE  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep SYS  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep TEST  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep WEB  >> ~/$CIRCLE_PROJECT_REPONAME/.env
