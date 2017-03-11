# Sagebrew / Application

## Information
This Django app is used for the generic multi-tenant SaaS solution used by the primary frontend application.


## Branch Details
| Branch  | Used For |
| ------------- | ------------- |
| master  | This branch is what you make PRs against and develop off of.  |
| production  | This branch is what production runs off of.  |

Due to the way the deployment processes work we need to basically setup specific branches for specific environments. 
Typically a human would git tag and make a release of the softwareand then from there deploy that specific release,
but because we want to limit human interaction with the software we automatic the deployment of both QA and Production.
So instead of a human doing git tagging we do PRs from master into production which then cause a deployment.

## Local Development
Local development of this application is done using docker. There are minor differences in setup depending on the base platform and how docker is implemented.

### Setup

#### Using OSX
There are two ways to setup docker on OSX.

Docker for mac is a "new" beta application developed by Docker that removes a number of external dependencies. It uses a more native osx virtualization strategy to remove the virtualbox requirements, along with providing a simple GUI to manage the box and Kitematic easily install third party docker containers if you desire to experiment with other applications.

The older way uses docker-machine and virtualbox.

The key difference between the two is with Docker for mac exposed ports are forwarded to your local machine meaning it runs on something like localhost:8000. Whereas with docker-machine you would access using the machine's IP address.

**Getting the Environment**
You'll need to get the env file from someone who has it. (See Devon Bleibtrey) Rename it to '.env' and add it to your repo locally.

**Install Instructions**
- [Docker For Mac Install Guide] https://docs.docker.com/docker-for-mac/
- [Docker Toolbox Install Guide] https://docs.docker.com/toolbox/toolbox_install_mac/ 

**Starting w/ Docker For Mac**
```bash
docker-compose -f dev.yml build
docker-compose -f dev.yml up
```

**Starting w/ Docker Machine**
```bash
docker-machine start default
eval $(docker-machine env)
docker-compose -f dev.yml build
docker-compose -f dev.yml up
```


#### Using Linux
This documentation is not yet completed. If you develop Sagebrew using linux please add setup instructions here.

#### Using Windows
This documentation is not yet completed. If you develop Sagebrew using Windows please add setup instructions here.

### Working With
You'll need to get the env file from someone who has it. (See Devon Bleibtrey)

You can run management commands using:
```bash
docker-compose -f dev.yml run pycharm python manage.py
```

**Running Tests**
```bash
docker-compose -f dev.yml run pycharm python manage.py test --noinput
```

**Connecting To DB w/ CLI**
```bash
docker-compose -f dev.yml run postgres psql -h postgres -U sagebrew
```

**Code Quality**
```bash
docker-compose -f dev.yml run pycharm coverage run --source='/app' manage.py test --failfast
docker-compose -f dev.yml run pycharm flake8 /app/sagebrew. --ignore C901
```

**Connecting To Pycharm**
For docker-machine instructions see: https://github.com/pydanny/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/docs/pycharm/configuration.rst

Docker for mac is a slightly more challenging requires an additional command to be kept running while developing.
```bash
socat TCP-LISTEN:6999,range=127.0.0.1/32,reuseaddr,fork UNIX-CLIENT:/var/run/docker.sock
```

Pycharm's docker integration must use: `tcp://localhost:6999` as the API url.

From there the instructions for setting up the python remote interrupters are the same for both docker for mac and docker-machine.

### Known Issues
- [ ] https://github.com/docker/compose/issues/1013 (use pycharm not django for running management commands.)
- [X] Pycharm + Docker isn't always able to create project skeletons. However it seems to work okay if you've already got pycharm setup, have it closed, start docker, then start pycharm.
- [X] At this point in time Pycharm does not work with Docker For Mac Beta due to being unable to connect. Until it is resolved it is recommended to use docker-machine for local development.


### References
- [PyCharm Setup] https://github.com/pydanny/cookiecutter-django/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/docs/pycharm/configuration.rst
- [Docker Docs] https://docs.docker.com/
- [Docker Compose] https://docs.docker.com/compose/overview/

