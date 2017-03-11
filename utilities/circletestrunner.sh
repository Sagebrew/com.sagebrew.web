#!/bin/bash

#
# For whatever reason between the mix of docker-machine and circlci it's tough to get exit codes on these tests to
# return correctly so we have to do this instead of running it directly in the circle script so that we can ensure
# when tests pass or fail it actually returns the correct script exit codes.

set -o nounset
set -o errexit

#
# We can use this same pattern to add the additional flake and coverage tests. (or whatever else we want)
docker-compose -f dev.yml run pycharm flake8 /app/sagebrew/ --ignore C901
docker-compose -f dev.yml run pycharm coverage run --source='/app' manage.py test  -v 3 --failfast  --noinput
#docker-compose -f dev.yml run pycharm coverage html
