FROM sagebrew/django.web.primary.base:v2
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git
RUN mkdir /home/apps/

RUN git clone -b devon-dev git@github.com:Sagebrew/com.sagebrew.web.git /home/apps/sagebrew/
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove -y openssh-client
RUN apt-get remove --auto-remove -y git

RUN apt-get install -y python-pip
RUN pip install -r /home/apps/sagebrew/requirements/base.txt



