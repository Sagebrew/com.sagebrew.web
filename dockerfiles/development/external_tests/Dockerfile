FROM ubuntu:14.04
MAINTAINER Kate Smith <ksmith@example.com>

RUN apt-get update && apt-get install -y nginx supervisor git
RUN mkdir /home/apps/
RUN cd /home/apps
RUN git clone git@github.com:Sagebrew/com.sagebrew.web.git@devon-dev
RUN pip install -r sagebrew/requirements/development.txt



