FROM sagebrew/django.web.primary.base:v2
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git
RUN mkdir /home/apps/
RUN cd /home/apps

RUN git clone -b devon-dev git@github.com:Sagebrew/com.sagebrew.web.git
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove openssh-client
RUN apt-get remove --auto-remove git

RUN pip install -r sagebrew/requirements/development.txt



