from os import environ

import multiprocessing

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('env', nargs='+', type=str)
        parser.add_argument('user', nargs='+', type=str)

    def populate_supervisor(self, env, user):
        worker_count = (multiprocessing.cpu_count() * 3) + 2
        if environ.get("CIRCLECI", "false").lower() == "true":
            worker_count = 2
        worker_count = str(worker_count)
        if env == "web":
            with open("%s/supervisor_confs/web_template.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()

                data = populate_general_values(data, user, worker_count)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        elif env == "worker":
            with open("%s/supervisor_confs/worker_template.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()
                data = populate_general_values(data, user, worker_count)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        elif env == "worker-test":
            with open("%s/supervisor_confs/worker_template_circle.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()
                data = populate_general_values(data, user, worker_count)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        else:
            pass

    def handle(self, *args, **options):
        self.populate_supervisor(options['env'][0], options['user'][0])
        self.stdout.write("Supervisor population complete")


def populate_general_values(data, user, worker_count):
    data = data.replace("%(ENV_SHA1)s", environ.get("SHA1", ""))
    data = data.replace("%(ENV_APP_USER)s", user)
    data = data.replace("%(ENV_APP_NAME)s", environ.get("APP_NAME", ""))
    data = data.replace("%(NUMBER_OF_WORKERS)s", worker_count)
    data = data.replace("%(ENV_PROJECT_REPONAME)s",
                        environ.get("PROJECT_REPONAME",
                                    environ.get("CIRCLE_PROJECT_REPONAME", "")))
    data = data.replace("%(ENV_CIRCLECI)s",
                        environ.get("CIRCLECI", "false").lower())
    data = data.replace("%(ENV_CIRCLE_BRANCH)s",
                        environ.get("CIRCLE_BRANCH", "master"))
    data = data.replace("%(ENV_CIRCLE_ARTIFACTS)s",
                        environ.get("CIRCLE_ARTIFACTS", "/home/apps/logs/"))
    data = data.replace("%(ENV_PROJECT_DIR)s", settings.PROJECT_DIR)
    data = data.replace("%(ENV_PROJECT_NAME)s", "sagebrew")
    data = data.replace("%(ENV_NUMBER_OF_WORKERS)s", worker_count)
    data = data.replace("%(ENV_LOGENT_TOKEN)s",
                        environ.get("LOGENT_TOKEN", ""))
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
    data = data.replace("%(ENV_ALCHEMY_API_KEY)s",
                        environ.get("ALCHEMY_API_KEY", ""))
    data = data.replace("%(ENV_ADDRESS_VALIDATION_ID)s",
                        environ.get("ADDRESS_VALIDATION_ID", ""))
    data = data.replace("%(ENV_ADDRESS_VALIDATION_TOKEN)s",
                        environ.get("ADDRESS_VALIDATION_TOKEN", ""))
    data = data.replace("%(ENV_ADDRESS_AUTH_ID)s",
                        environ.get("ADDRESS_AUTH_ID", ""))
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
    data = data.replace("%(ENV_RDS_DB_NAME)s", environ.get("RDS_DB_NAME", ""))
    data = data.replace("%(ENV_RDS_USERNAME)s",
                        environ.get("RDS_USERNAME", ""))
    data = data.replace("%(ENV_RDS_PASSWORD)s",
                        environ.get("RDS_PASSWORD", ""))
    data = data.replace("%(ENV_RDS_HOSTNAME)s",
                        environ.get("RDS_HOSTNAME", ""))
    data = data.replace("%(ENV_RDS_PORT)s", environ.get("RDS_PORT", ""))
    data = data.replace("%(ENV_DYNAMO_IP)s", environ.get("DYNAMO_IP", ""))
    data = data.replace("%(ENV_STRIPE_PUBLIC_KEY)s",
                        environ.get("STRIPE_PUBLIC_KEY", ""))
    data = data.replace("%(ENV_STRIPE_SECRET_KEY)s",
                        environ.get("STRIPE_SECRET_KEY", ""))
    data = data.replace("%(ENV_MASKED_NAME)s",
                        environ.get("MASKED_NAME", ""))
    data = data.replace("%(ENV_AWS_DEFAULT_REGION)s",
                        environ.get("AWS_DEFAULT_REGION", ""))
    data = data.replace("%(ENV_OPBEAT_ORG_ID)s",
                        environ.get("OPBEAT_ORG_ID", ""))
    data = data.replace("%(ENV_OPBEAT_APP_ID)s",
                        environ.get("OPBEAT_APP_ID", ""))
    data = data.replace("%(ENV_OPBEAT_SECRET_TOKEN)s",
                        environ.get("OPBEAT_SECRET_TOKEN", ""))
    data = data.replace("%(ENV_OAUTH_CLIENT_ID)s",
                        environ.get("OAUTH_CLIENT_ID", ""))
    data = data.replace("%(ENV_OAUTH_CLIENT_SECRET)s",
                        environ.get("OAUTH_CLIENT_SECRET", ""))
    data = data.replace("%(ENV_CRED_USER_PUBLIC)s",
                        environ.get("CRED_USER_PUBLIC", ""))
    data = data.replace("%(ENV_CRED_PASSWORD_PUBLIC)s",
                        environ.get("CRED_PASSWORD_PUBLIC", ""))
    data = data.replace("%(ENV_OAUTH_CLIENT_SECRET_CRED_PUBLIC)s",
                        environ.get("OAUTH_CLIENT_SECRET_CRED_PUBLIC",
                                    ""))
    data = data.replace("%(ENV_OAUTH_CLIENT_ID_CRED_PUBLIC)s",
                        environ.get("OAUTH_CLIENT_ID_CRED_PUBLIC", ""))
    data = data.replace("%(ENV_GOOGLE_MAPS_API)s",
                        environ.get("GOOGLE_MAPS_API", ""))
    data = data.replace("%(ENV_GOOGLE_MAPS_JS)s",
                        environ.get("GOOGLE_MAPS_JS", ""))
    data = data.replace("%(ENV_SUNLIGHT_FOUNDATION_KEY)s",
                        environ.get("SUNLIGHT_FOUNDATION_KEY", ""))
    data = data.replace("%(ENV_WEBHOSE_KEY)s", environ.get("WEBHOSE_KEY", ""))
    data = data.replace("%(ENV_INTERCOM_API_KEY)s",
                        environ.get("INTERCOM_API_KEY", ""))
    data = data.replace("%(ENV_INTERCOM_APP_ID)s",
                        environ.get("INTERCOM_APP_ID", ""))
    data = data.replace("%(ENV_INTERCOM_ADMIN_ID_DEVON)s",
                        environ.get("INTERCOM_ADMIN_ID_DEVON", ""))
    return data
