FROM sagebrew/django.web.primary.frontend:v1

MAINTAINER Devon Bleibtrey <devon@sagebrew.com>

RUN apt-get update && apt-get install -y git

RUN mkdir /home/apps/
RUN mkdir /home/apps/logs


RUN git clone -b devon-dev git@github.com:sagebrew/com.sagebrew.web.git /home/apps/sagebrew/
RUN chown -R gandolf:gandolf /home/apps/
RUN mkdir /home/apps/sagebrew/sagebrew/static/
RUN rm -r /root/.ssh
RUN apt-get remove --auto-remove -y openssh-client


WORKDIR /home/apps/sagebrew/sagebrew/sagebrew/static/
RUN bower install --config.interactive=false --allow-root

WORKDIR /home/apps/sagebrew/sagebrew/sagebrew/static/bower_components/flat-ui/
RUN npm install
RUN bower install --config.interactive=false --allow-root

WORKDIR /home/apps/sagebrew/sagebrew/sagebrew/static/bower_components/bootstrapvalidator/
RUN bower install --config.interactive=false --allow-root

RUN pip install -r /home/apps/sagebrew/requirements/test.txt

RUN apt-get remove --auto-remove -y git

CMD chown gandolf /etc/rsyslog.d/ && python /home/apps/sagebrew/sagebrew/manage.py logglypopulation sagebrew 4fe8ecbc-c44a-4ea0-aece-0d4d8eb43fb2 && chown root /etc/rsyslog.d/ && service rsyslog restart && python /home/apps/sagebrew/sagebrew/manage.py collectstatic -c --noinput && python /home/apps/sagebrew/sagebrew/manage.py migrate --noinput --no-initial-data
