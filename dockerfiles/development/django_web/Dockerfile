FROM sagebrew/django.web.primary.base:v2
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git
RUN mkdir /home/apps/
RUN cd /home/apps

RUN git clone -b devon-dev git@github.com:Sagebrew/com.sagebrew.web.git
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove -y openssh-client
RUN apt-get remove --auto-remove -y git

RUN apt-get install python-pip
RUN pip install virtualenv
RUN virtualenv venv
RUN source /home/apps/venv/bin/activate
RUN pip install -r com.sagebrew.web/requirements/development.txt



