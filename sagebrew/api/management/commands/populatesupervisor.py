from os import environ
import logging
import multiprocessing

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('loggly_logs')

class Command(BaseCommand):
    def populate_supervisor(self, env, user):
        worker_count = (multiprocessing.cpu_count() *2) + 1
        if(environ.get("CIRCLECI", False)):
            worker_count = 2
        worker_count = str(worker_count)
        if(env == "web"):
            with open ("%s/supervisor_confs/web_template.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()

                data = populate_general_values(data, user, worker_count)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        elif(env == "worker"):
            with open ("%s/supervisor_confs/worker_template.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()
                data = populate_general_values(data, user, worker_count)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        elif(env == "worker-test"):
            with open ("%s/supervisor_confs/worker_template_circle.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()
                data = populate_general_values(data, user, worker_count)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        else:
            pass

    def handle(self, *args, **options):
        self.populate_supervisor(args[0], args[1])


def populate_general_values(data, user, worker_count):
    data = data.replace("%(ENV_APP_USER)s", user)
    data = data.replace("%(NUMBER_OF_WORKERS)s", worker_count)
    data = data.replace("%(ENV_REPO_NAME)s",
                        environ.get("REPO_NAME", "sagebrew"))
    data = data.replace("%(ENV_CIRCLE_ARTIFACTS)s",
                        environ.get("CIRCLE_ARTIFACTS", "/home/apps/logs/"))
    data = data.replace("%(ENV_PROJECT_DIR)s", settings.PROJECT_DIR)
    data = data.replace("%(ENV_PROJECT_NAME)s", "sagebrew")
    data = data.replace("%(ENV_NUMBER_OF_WORKERS)s", worker_count)
    data = data.replace("%(ENV_APPLICATION_SECRET_KEY)s",
                             environ.get("APPLICATION_SECRET_KEY", ""))
    data = data.replace("%(ENV_NEO4J_REST_URL)s",
                             environ.get("NEO4J_REST_URL", ""))
    data = data.replace("%(ENV_BOMBERMAN_API_KEY)s",
                             environ.get("BOMBERMAN_API_KEY", ""))
    data = data.replace("%(ENV_AWS_S3_BUCKET)s",
                             environ.get("AWS_S3_BUCKET", ""))
    data = data.replace("%(ENV_AWS_SECRET_ACCESS_KEY)s",
                             environ.get("AWS_SECRET_ACCESS_KEY", ""))
    data = data.replace("%(ENV_AWS_ACCESS_KEY_ID)s",
                             environ.get("AWS_ACCESS_KEY_ID", ""))
    data = data.replace("%(ENV_LOG_TOKEN)s",
                             environ.get("LOG_TOKEN", ""))
    data = data.replace("%(ENV_LOG_ACCOUNT)s",
                             environ.get("LOG_ACCOUNT", ""))
    data = data.replace("%(ENV_ALCHEMY_API_KEY)s",
                             environ.get("ALCHEMY_API_KEY", ""))
    data = data.replace("%(ENV_ADDRESS_VALIDATION_ID)s",
                             environ.get("ADDRESS_VALIDATION_ID", ""))
    data = data.replace("%(ENV_ADDRESS_VALIDATION_TOKEN)s",
                             environ.get("ADDRESS_VALIDATION_TOKEN", ""))
    data = data.replace("%(ENV_ELASTIC_SEARCH_HOST)s",
                             environ.get("ELASTIC_SEARCH_HOST", ""))
    data = data.replace("%(ENV_ELASTIC_SEARCH_PORT)s",
                             environ.get("ELASTIC_SEARCH_PORT", ""))
    data = data.replace("%(ENV_ELASTIC_SEARCH_USER)s",
                             environ.get("ELASTIC_SEARCH_USER", ""))
    data = data.replace("%(ENV_ELASTIC_SEARCH_KEY)s",
                             environ.get("ELASTIC_SEARCH_KEY", ""))
    data = data.replace("%(ENV_REDIS_PORT)s",
                             environ.get("REDIS_PORT", ""))
    data = data.replace("%(ENV_REDIS_LOCATION)s",
                             environ.get("REDIS_LOCATION", ""))
    data = data.replace("%(ENV_QUEUE_USERNAME)s",
                             environ.get("QUEUE_USERNAME", ""))
    data = data.replace("%(ENV_QUEUE_PASSWORD)s",
                             environ.get("QUEUE_PASSWORD", ""))
    data = data.replace("%(ENV_QUEUE_HOST)s", environ.get("QUEUE_HOST", ""))
    data = data.replace("%(ENV_QUEUE_PORT)s", environ.get("QUEUE_PORT", ""))

    return data