import logging
import socket
import multiprocessing
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('loggly_logs')

class Command(BaseCommand):
    def populate_nginx(self, user):
        hostname = socket.gethostname()
        if('box' in hostname):
            env = "development"
        else:
            env = "production"
        worker_count = str((multiprocessing.cpu_count() *2) + 1)
        with open ("%s/nginx_templates/base.tmpl" % (
                settings.REPO_DIR), "r") as nginx_file:
            data = nginx_file.read()
            data = data.replace("{{WEB_WORKER_COUNT}}", worker_count)
            data = data.replace("{{APP_USER}}", user)

        f = open("/etc/nginx/conf.d/base.conf", "w")
        f.write(data)
        f.close()

        with open ("%s/nginx_templates/nginx.tmpl" % (
                settings.REPO_DIR), "r") as nginx_conf_file:
            data = nginx_conf_file.read()

        f = open("/etc/nginx/nginx.conf", "w")
        f.write(data)
        f.close()

        with open ("%s/nginx_templates/%s.tmpl" % (
                settings.REPO_DIR, env), "r") as site_file:
            data = site_file.read()
            domains = ""
            for item in settings.ALLOWED_HOSTS:
                domains += domains + "|" + item
            domains_pipe = domains[1:]
            domains_space = domains_pipe.replace("|", " ")
            project_name = settings.PROJECT_DIR[settings.PROJECT_DIR.rfind('/') + 1:]
            data = data.replace("{{PROJECT_NAME}}", project_name)
            data = data.replace("{{PROJECT_PATH}}", settings.PROJECT_DIR)
            data = data.replace("{{DOMAINS_PIPE}}", domains_pipe)
            data = data.replace("{{DOMAINS_SPACE}}", domains_space)

        f = open("/etc/nginx/%s.conf", "w")
        f.write(data)
        f.close()

    def handle(self, *args, **options):
        self.populate_nginx(args[0])