import os

import socket
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    args = 'None.'

    def populate_dockerfiles(self):
        with open ("%s/dockerfile_template" % settings.REPO_DIR,
                   "r") as dockerfile:
            data = dockerfile.read().replace('{{DOCKER_ENV}}', os.environ.get(
                "DOCKER_ENV", ""))
            data = data.replace('{{APP_USER}}', os.environ.get(
                "APP_USER", ""))
            data = data.replace('{{REQUIREMENTS_FILE}}', os.environ.get(
                "REQUIREMENTS_FILE", ""))
            web_docker = data.replace('{{SUPER_TEMPLATE}}', "web")
            worker_docker = data.replace('{{SUPER_TEMPLATE}}', "worker")
        f = open("%s/dockerfiles/web_app/Dockerfile" % settings.REPO_DIR, "w")
        f.write(web_docker)
        f.close()
        f = open("%s/dockerfiles/worker/Dockerfile" % settings.REPO_DIR, "w")
        f.write(worker_docker)
        f.close()



    def handle(self, *args, **options):
        self.populate_dockerfiles()