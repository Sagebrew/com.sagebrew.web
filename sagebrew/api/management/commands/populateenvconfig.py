from os import environ
import logging
import multiprocessing

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('loggly_logs')

class Command(BaseCommand):

    def populate_config(self, web_env, worker_env):
        with open("%s/aws_environment_config/base.config" % (
                settings.REPO_DIR), "r") as dockerfile:
            data = dockerfile.read()

            data = populate_general_values(data)
        f = open("%s" % (web_env), "w")
        f.write(data)
        f.close()
        f = open("%s" % (worker_env), "w")
        f.write(data)
        f.close()


    def handle(self, *args, **options):
        self.populate_config(args[0], args[1])


def populate_general_values(data):
    data = data.replace("<APP_USER>", environ.get("APP_USER", ""))
    data = data.replace("<REPO_NAME>", environ.get("REPO_NAME", ""))
    data = data.replace("<PROJECT_NAME>", environ.get("PROJECT_NAME"))
    data = data.replace("<LOG_ACCOUNT>", environ.get("LOG_ACCOUNT", ""))
    data = data.replace("<LOG_TOKEN>", environ.get("LOG_TOKEN", ""))
    data = data.replace("<STAGING_NEO4J_REST_URL>",
                             environ.get("STAGING_NEO4J_REST_URL", ""))
    data = data.replace("<CIRCLE_BRANCH>", environ.get("CIRCLE_BRANCH", ""))
    data = data.replace("<APPLICATION_SECRET_KEY>",
                        environ.get("APPLICATION_SECRET_KEY", ""))
    data = data.replace("<BOMBERMAN_API_KEY>",
                        environ.get("BOMBERMAN_API_KEY", ""))
    data = data.replace("<SSL_CERT_LOCATION>",
                        environ.get("SSL_CERT_LOCATION", ""))
    data = data.replace("<SSL_KEY_LOCATION>", environ.get("SSL_KEY_LOCATION", ""))
    data = data.replace("<AWS_S3_BUCKET>", environ.get("AWS_S3_BUCKET", ""))
    data = data.replace("<AWS_SECRET_ACCESS_KEY>",
                        environ.get("AWS_SECRET_ACCESS_KEY", ""))
    data = data.replace("<ALCHEMY_API_KEY>", environ.get("ALCHEMY_API_KEY", ""))
    data = data.replace("<ADDRESS_VALIDATION_ID>",
                        environ.get("ADDRESS_VALIDATION_ID", ""))
    data = data.replace("<ADDRESS_VALIDATION_TOKEN>",
                        environ.get("ADDRESS_VALIDATION_TOKEN", ""))
    data = data.replace("<ELASTIC_SEARCH_HOST>",
                        environ.get("ELASTIC_SEARCH_HOST", ""))
    data = data.replace("<ELASTIC_SEARCH_PORT>",
                        environ.get("ELASTIC_SEARCH_PORT", ""))
    data = data.replace("<ELASTIC_SEARCH_USER>",
                        environ.get("ELASTIC_SEARCH_USER", ""))
    data = data.replace("<ELASTIC_SEARCH_KEY>",
                        environ.get("ELASTIC_SEARCH_KEY", ""))
    data = data.replace("<REDIS_LOCATION>", environ.get("REDIS_LOCATION", ""))
    data = data.replace("<REDIS_PORT>", environ.get("REDIS_PORT", ""))
    data = data.replace("<QUEUE_USERNAME>", environ.get("QUEUE_USERNAME", ""))
    data = data.replace("<QUEUE_PASSWORD>", environ.get("QUEUE_PASSWORD", ""))
    data = data.replace("<QUEUE_HOST>", environ.get("QUEUE_HOST", ""))
    data = data.replace("<QUEUE_PORT>", environ.get("QUEUE_PORT", ""))

    return data