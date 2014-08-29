FROM sagebrew/django.web.primary.base:v1
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git
RUN mkdir /home/apps/
RUN cd /home/apps

RUN git clone git@github.com:Sagebrew/com.sagebrew.web.git@devon-dev
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove openssh-client
RUN apt-get remove --auto-remove git

RUN pip install -r sagebrew/requirements/development.txt



