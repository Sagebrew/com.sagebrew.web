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
env | grep MYSQL  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep APPLICATION_  >> ~/$CIRCLE_PROJECT_REPONAME/.env
env | grep REDIS  >> ~/$CIRCLE_PROJECT_REPONAME/.env
