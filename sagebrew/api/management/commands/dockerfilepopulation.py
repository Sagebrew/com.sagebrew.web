import os

import socket
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    args = 'None.'

    def populate_dockerfiles(self):
        with open ("%s/dockerfile_template" % settings.REPO_DIR,
                   "r") as dockerfile:
            circle_branch = os.environ.get("CIRCLE_BRANCH", None)
            data = dockerfile.read()
            if(circle_branch is not None):
                project_username = os.environ.get("CIRCLE_PROJECT_USERNAME", "")
                project_reponame = os.environ.get("CIRCLE_PROJECT_REPONAME", "")
                data = data.replace("{{PROJECT_REPONAME}}", project_reponame)
                data = data.replace("{{PROJECT_USERNAME}}", project_username)
                if(circle_branch == "staging"):
                    data = data.replace('{{REQUIREMENTS_FILE}}', "production")
                elif("dev" in circle_branch):
                    data = data.replace('{{REQUIREMENTS_FILE}}', "test")
                elif(circle_branch == "master"):
                    data = data.replace('{{REQUIREMENTS_FILE}}', "production")
            else:
                data = data.replace('{{REQUIREMENTS_FILE}}',
                                    os.environ.get(
                                        "REQUIREMENTS_FILE", "production"))
                data = data.replace("{{PROJECT_REPONAME}}",
                                    os.environ.get("PROJECT_REPONAME", ""))
                data = data.replace("{{PROJECT_USERNAME}}",
                                    os.environ.get("PROJECT_USERNAME", ""))
            docker_env = os.environ.get("CIRCLE_BRANCH", None)
            # TODO Still not picking up the correct repo to pull from github
            # on local instances.

            if docker_env is None:
                docker_env = os.environ.get("DOCKER_ENV", "")
            data = data.replace('{{DOCKER_ENV}}', docker_env)
            data = data.replace('{{APP_USER}}', os.environ.get(
                "APP_USER", ""))
            data = data.replace('{{BOMBERMAN_API_KEY}}', os.environ.get(
                "BOMBERMAN_API_KEY", ""))
            data = data.replace('{{NEO4J_REST_URL}}', os.environ.get(
                "$GRAPHEN_NEO4J_REST_URL", ""))
            data = data.replace("{{PROJECT_NAME}}", "sagebrew")
            data = data.replace("{{LOG_ACCOUNT}}", os.environ.get(
                "LOG_ACCOUNT", ""))
            data = data.replace("{{LOG_TOKEN}}", os.environ.get(
                "LOG_TOKEN", ""))
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