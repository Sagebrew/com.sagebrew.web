FROM sagebrew/django.web.primary.base:v3
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git python-dev
RUN mkdir /home/apps/

RUN git clone -b devon-dev git@github.com:Sagebrew/com.sagebrew.web.git /home/apps/sagebrew/
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove -y openssh-client
RUN apt-get remove --auto-remove -y git

RUN apt-get install -y python-pip

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y python-software-properties software-properties-common postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3 postgresql-server-dev-9.3


RUN pip install -r /home/apps/sagebrew/requirements/development.txt
RUN pip pip install git+https://github.com/robinedwards/neomodel.git@0.3.6

CMD sudo service supervisor start
CMD sudo supervisorctl reload
CMD sudo supervisorctl restart all