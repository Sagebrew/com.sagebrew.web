FROM sagebrew/django.web.primary.base:v2
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git python-dev
RUN mkdir /home/apps/

RUN git clone -b devon-dev git@github.com:Sagebrew/com.sagebrew.web.git /home/apps/sagebrew/
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove -y openssh-client
RUN apt-get remove --auto-remove -y git

RUN apt-get install -y python-pip

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y libpq-dev postgresql postgresql-contrib

RUN pip install -r /home/apps/sagebrew/requirements/celery/base.txt
RUN pip install git+https://github.com/robinedwards/neomodel.git@0.3.6