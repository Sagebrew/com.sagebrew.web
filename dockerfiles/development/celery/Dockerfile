FROM sagebrew/django.web.primary.base:v2
MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git python-dev
RUN mkdir /home/apps/

RUN git clone -b devon-dev git@github.com:Sagebrew/com.sagebrew.web.git /home/apps/sagebrew/
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove -y openssh-client
RUN apt-get remove --auto-remove -y git

RUN apt-get install -y python-pip

# Could potentially take PSQL out of this Dockerfile and link it to w/e container needs it
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y python-software-properties software-properties-common postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3 postgresql-server-dev-9.3

USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER admin WITH SUPERUSER PASSWORD 'admin';" &&\
    createdb -O sagebrew_db sagebrew_db

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/9.3/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Set the default command to run when starting the container
CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]

USER root

RUN pip install -r /home/apps/sagebrew/requirements/celery/base.txt