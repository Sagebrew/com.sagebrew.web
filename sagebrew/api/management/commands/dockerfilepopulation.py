import os

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    args = 'None.'

    def populate_dockerfiles(self):
        with open("%s/dockerfile_template" % settings.REPO_DIR,
                   "r") as dockerfile:
            circle_branch = os.environ.get("CIRCLE_BRANCH", None)
            data = dockerfile.read()
            if(circle_branch is not None):
                data = data.replace("{{PROJECT_REPONAME}}",
                                    os.environ.get("CIRCLE_PROJECT_REPONAME",
                                                   ""))
                data = data.replace("{{PROJECT_USERNAME}}",
                                    os.environ.get("CIRCLE_PROJECT_USERNAME",
                                                   ""))
                data = data.replace("{{CIRCLE_BRANCH}}",
                                    os.environ.get("CIRCLE_BRANCH", ""))

                data = populate_general_env(data)
                if(circle_branch == "staging"):
                    data = populate_staging_env(data)
                elif("dev" in circle_branch):
                    data = populate_test_env(data)
                elif(circle_branch == "master"):
                    data = populate_prod_env(data)
            else:
                data = data.replace("{{PROJECT_REPONAME}}",
                                    os.environ.get("PROJECT_REPONAME", ""))
                data = data.replace("{{PROJECT_USERNAME}}",
                                    os.environ.get("PROJECT_USERNAME", ""))
                circle_branch = os.environ.get("DOCKER_ENV", "staging")
            data = data.replace('{{APPLICATION_SECRET_KEY}}',
                                os.environ.get("APPLICATION_SECRET_KEY", ""))
            data = data.replace('{{REQUIREMENTS_FILE}}',
                                    os.environ.get(
                                        "REQUIREMENTS_FILE", "base"))
            data = data.replace('{{DOCKER_ENV}}', circle_branch)
            data = data.replace("{{PROJECT_NAME}}", "sagebrew")
            data = data.replace("{{CIRCLECI}}",
                                os.environ.get("CIRCLECI", ""))
            web_docker = data.replace('{{SUPER_TEMPLATE}}', "web")
            web_docker = web_docker.replace('{{IMAGE_TYPE}}', "frontend")
            web_docker = web_docker.replace('{{VERSION}}', "3")
            worker_docker = data.replace('{{SUPER_TEMPLATE}}', "worker")
            worker_docker = worker_docker.replace('{{IMAGE_TYPE}}', "base")
            worker_docker = worker_docker.replace('{{VERSION}}', "14")

        f = open("%s/dockerfiles/web_app/Dockerfile" % settings.REPO_DIR, "w")
        f.write(web_docker)
        f.close()
        f = open("%s/dockerfiles/worker/Dockerfile" % settings.REPO_DIR, "w")
        f.write(worker_docker)
        f.close()
        with open("%s/docker_sys_util" % settings.REPO_DIR,
                  "r") as dockerfile:
            circle_branch = os.environ.get("CIRCLE_BRANCH", None)
            data = dockerfile.read()
            if(circle_branch is not None):
                data = data.replace("{{PROJECT_REPONAME}}",
                                    os.environ.get("CIRCLE_PROJECT_REPONAME",
                                                   ""))
                data = data.replace("{{PROJECT_USERNAME}}",
                                    os.environ.get("CIRCLE_PROJECT_USERNAME",
                                                   ""))
                data = populate_general_env(data)
                if(circle_branch == "staging"):
                    data = populate_staging_env(data)
                elif("dev" in circle_branch):
                    data = populate_test_env(data)
                elif(circle_branch == "master"):
                    data = populate_prod_env(data)
            else:
                data = data.replace("{{PROJECT_REPONAME}}",
                                    os.environ.get("PROJECT_REPONAME", ""))
                data = data.replace("{{PROJECT_USERNAME}}",
                                    os.environ.get("PROJECT_USERNAME", ""))
                circle_branch = os.environ.get("DOCKER_ENV", "staging")
            data = data.replace('{{REQUIREMENTS_FILE}}',
                                    os.environ.get(
                                        "REQUIREMENTS_FILE", "base"))
            data = data.replace('{{APPLICATION_SECRET_KEY}}',
                                os.environ.get("APPLICATION_SECRET_KEY", ""))
            data = data.replace('{{DOCKER_ENV}}', circle_branch)
            data = data.replace("{{PROJECT_NAME}}", "sagebrew")
            sys_docker = data.replace("{{CIRCLECI}}",
                                      os.environ.get("CIRCLECI", ""))
        f = open("%s/dockerfiles/sys_util/Dockerfile" % settings.REPO_DIR, "w")
        f.write(sys_docker)
        f.close()

    def handle(self, *args, **options):
        self.populate_dockerfiles()
        self.stdout.write("Dockerfiles populated")


def populate_general_env(data):
    data = data.replace('{{APP_USER}}', os.environ.get("APP_USER", ""))
    data = data.replace("{{APP_NAME}}", os.environ.get("APP_NAME", ""))
    data = data.replace('{{NEW_RELIC_LICENSE}}', os.environ.get(
        "NEW_RELIC_LICENSE", ""))
    data = data.replace('{{CIRCLE_BRANCH}}', os.environ.get(
        "CIRCLE_BRANCH", ""))
    data = data.replace('{{SSL_CERT_LOCATION}}', os.environ.get(
        "SSL_CERT_LOCATION", ""))
    data = data.replace('{{SSL_KEY_LOCATION}}', os.environ.get(
        "SSL_KEY_LOCATION", ""))
    return data


def populate_test_env(data):
    data = data.replace('{{REQUIREMENTS_FILE}}', "test")
    data = data.replace('{{BOMBERMAN_API_KEY}}', os.environ.get(
        "BOMBERMAN_API_KEY", ""))
    data = data.replace('{{NEO4J_REST_URL}}',
                        os.environ.get("NEO4J_REST_URL", ""))
    data = data.replace("{{AWS_S3_BUCKET}}", os.environ.get(
        "AWS_S3_BUCKET", ""))
    data = data.replace("{{AWS_SECRET_ACCESS_KEY}}",
                        os.environ.get("AWS_SECRET_ACCESS_KEY", ""))
    data = data.replace("{{AWS_ACCESS_KEY_ID}}",
                        os.environ.get("AWS_ACCESS_KEY_ID", ""))
    data = data.replace("{{ALCHEMY_API_KEY}}",
                        os.environ.get("ALCHEMY_API_KEY", ""))
    data = data.replace("{{ADDRESS_VALIDATION_ID}}",
                        os.environ.get("ADDRESS_VALIDATION_ID", ""))
    data = data.replace("{{ADDRESS_VALIDATION_TOKEN}}",
                        os.environ.get("ADDRESS_VALIDATION_TOKEN", ""))
    data = data.replace("{{ELASTIC_SEARCH_HOST}}",
                        os.environ.get("ELASTIC_SEARCH_HOST", ""))
    data = data.replace("{{ELASTIC_SEARCH_PORT}}",
                        os.environ.get("ELASTIC_SEARCH_PORT", ""))
    data = data.replace("{{ELASTIC_SEARCH_USER}}",
                        os.environ.get("ELASTIC_SEARCH_USER", ""))
    data = data.replace("{{ELASTIC_SEARCH_KEY}}",
                        os.environ.get("ELASTIC_SEARCH_KEY", ""))
    data = data.replace("{{REDIS_LOCATION}}",
                        os.environ.get("REDIS_LOCATION", ""))
    data = data.replace("{{REDIS_PORT}}", os.environ.get("REDIS_PORT", ""))
    data = data.replace("{{QUEUE_USERNAME}}",
                        os.environ.get("QUEUE_USERNAME", ""))
    data = data.replace("{{QUEUE_PASSWORD}}",
                        os.environ.get("QUEUE_PASSWORD", ""))
    data = data.replace("{{QUEUE_HOST}}", os.environ.get("QUEUE_HOST", ""))
    data = data.replace("{{QUEUE_PORT}}", os.environ.get("QUEUE_PORT", ""))

    return data


def populate_prod_env(data):
    data = data.replace('{{REQUIREMENTS_FILE}}', "production")
    data = data.replace('{{BOMBERMAN_API_KEY}}', os.environ.get(
        "BOMBERMAN_API_KEY_PROD", ""))
    data = data.replace('{{NEO4J_REST_URL}}',
                        os.environ.get("NEO4J_REST_URL_PROD", ""))
    data = data.replace("{{AWS_S3_BUCKET}}", os.environ.get(
        "AWS_S3_BUCKET_PROD", ""))
    data = data.replace("{{AWS_SECRET_ACCESS_KEY}}",
                        os.environ.get("AWS_SECRET_ACCESS_KEY_PROD", ""))
    data = data.replace("{{AWS_ACCESS_KEY_ID}}",
                        os.environ.get("AWS_ACCESS_KEY_ID_PROD", ""))
    data = data.replace("{{ALCHEMY_API_KEY}}",
                        os.environ.get("ALCHEMY_API_KEY_PROD", ""))
    data = data.replace("{{ADDRESS_VALIDATION_ID}}",
                        os.environ.get("ADDRESS_VALIDATION_ID_PROD", ""))
    data = data.replace("{{ADDRESS_VALIDATION_TOKEN}}",
                        os.environ.get("ADDRESS_VALIDATION_TOKEN_PROD", ""))
    data = data.replace("{{ELASTIC_SEARCH_HOST}}",
                        os.environ.get("ELASTIC_SEARCH_HOST_PROD", ""))
    data = data.replace("{{ELASTIC_SEARCH_PORT}}",
                        os.environ.get("ELASTIC_SEARCH_PORT_PROD", ""))
    data = data.replace("{{ELASTIC_SEARCH_USER}}",
                        os.environ.get("ELASTIC_SEARCH_USER_PROD", ""))
    data = data.replace("{{ELASTIC_SEARCH_KEY}}",
                        os.environ.get("ELASTIC_SEARCH_KEY_PROD", ""))
    data = data.replace("{{REDIS_LOCATION}}",
                        os.environ.get("REDIS_LOCATION_PROD", ""))
    data = data.replace("{{REDIS_PORT}}", os.environ.get("REDIS_PORT_PROD", ""))
    data = data.replace("{{QUEUE_USERNAME}}",
                        os.environ.get("QUEUE_USERNAME_PROD", ""))
    data = data.replace("{{QUEUE_PASSWORD}}",
                        os.environ.get("QUEUE_PASSWORD_PROD", ""))
    data = data.replace("{{QUEUE_HOST}}", os.environ.get("QUEUE_HOST_PROD", ""))
    data = data.replace("{{QUEUE_PORT}}", os.environ.get("QUEUE_PORT_PROD", ""))
    data = data.replace("{{OPBEAT_ORG_ID}}",
                        os.environ.get("OPBEAT_ORG_ID_PROD", ""))
    data = data.replace("{{OPBEAT_APP}}",
                        os.environ.get("OPBEAT_APP_ID_PROD", ""))
    data = data.replace("{{OPBEAT_SECRET_TOKEN}}",
                        os.environ.get("OPBEAT_SECRET_TOKEN_PROD", ""))
    return data


def populate_staging_env(data):
    data = data.replace('{{REQUIREMENTS_FILE}}', "production")
    data = data.replace('{{BOMBERMAN_API_KEY}}', os.environ.get(
        "BOMBERMAN_API_KEY_STAGING", ""))
    data = data.replace('{{NEO4J_REST_URL}}',
                        os.environ.get("NEO4J_REST_URL_STAGING", ""))
    data = data.replace("{{AWS_S3_BUCKET}}", os.environ.get(
        "AWS_S3_BUCKET_STAGING", ""))
    data = data.replace("{{AWS_SECRET_ACCESS_KEY}}",
                        os.environ.get("AWS_SECRET_ACCESS_KEY_STAGING", ""))
    data = data.replace("{{AWS_ACCESS_KEY_ID}}",
                        os.environ.get("AWS_ACCESS_KEY_ID_STAGING", ""))
    data = data.replace("{{ALCHEMY_API_KEY}}",
                        os.environ.get("ALCHEMY_API_KEY_STAGING", ""))
    data = data.replace("{{ADDRESS_VALIDATION_ID}}",
                        os.environ.get("ADDRESS_VALIDATION_ID_STAGING", ""))
    data = data.replace("{{ADDRESS_VALIDATION_TOKEN}}",
                        os.environ.get("ADDRESS_VALIDATION_TOKEN_STAGING", ""))
    data = data.replace("{{ELASTIC_SEARCH_HOST}}",
                        os.environ.get("ELASTIC_SEARCH_HOST_STAGING", ""))
    data = data.replace("{{ELASTIC_SEARCH_PORT}}",
                        os.environ.get("ELASTIC_SEARCH_PORT_STAGING", ""))
    data = data.replace("{{ELASTIC_SEARCH_USER}}",
                        os.environ.get("ELASTIC_SEARCH_USER_STAGING", ""))
    data = data.replace("{{ELASTIC_SEARCH_KEY}}",
                        os.environ.get("ELASTIC_SEARCH_KEY_STAGING", ""))
    data = data.replace("{{REDIS_LOCATION}}",
                        os.environ.get("REDIS_LOCATION_STAGING", ""))
    data = data.replace("{{REDIS_PORT}}", os.environ.get("REDIS_PORT_STAGING",
                                                         ""))
    data = data.replace("{{QUEUE_USERNAME}}",
                        os.environ.get("QUEUE_USERNAME_STAGING", ""))
    data = data.replace("{{QUEUE_PASSWORD}}",
                        os.environ.get("QUEUE_PASSWORD_STAGING", ""))
    data = data.replace("{{QUEUE_HOST}}",
                        os.environ.get("QUEUE_HOST_STAGING", ""))
    data = data.replace("{{QUEUE_PORT}}",
                        os.environ.get("QUEUE_PORT_STAGING", ""))
    data = data.replace("{{OPBEAT_ORG_ID}}",
                        os.environ.get("OPBEAT_ORG_ID_STAGING", ""))
    data = data.replace("{{OPBEAT_APP_ID}}",
                        os.environ.get("OPBEAT_APP_ID_STAGING", ""))
    data = data.replace("{{OPBEAT_SECRET_TOKEN}}",
                        os.environ.get("OPBEAT_SECRET_TOKEN_STAGING", ""))
    return data