import os
import multiprocessing
from subprocess32 import call
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    def populate_nginx(self, user, worker="web"):
        circle_branch = os.environ.get("CIRCLE_BRANCH", None)
        circle_ci = os.environ.get("CIRCLECI", "false").lower()
        if circle_ci == "false":
            circle_ci = False
        else:
            circle_ci = True
        if('dev' in circle_branch):
            env = "development"
        # This elif is there so that on Circle the dev nginx file is used
        # but once deployed to aws the production nginx config is used
        # This is due to the differences in SSL management. AWS handles it
        # for us but on circle we have to include it in our nginx files.
        elif circle_ci is True:
            env = "development"
        else:
            env = "production"
            if worker == "worker":
                env = "production_worker"
        worker_count = (multiprocessing.cpu_count() * 2) + 1
        if worker_count > 12 and circle_ci:
            worker_count = 12
        worker_count = str(worker_count)
        call("sudo chown -R %s:%s /etc/nginx/" % (user, user), shell=True)
        with open("%s/nginx_templates/base.tmpl" % (
                settings.REPO_DIR), "r") as nginx_file:
            data = nginx_file.read()
            data = data.replace("{{WEB_WORKER_COUNT}}", worker_count)
            data = data.replace("{{APP_USER}}", user)

        f = open("/etc/nginx/conf.d/base.conf", "w")
        f.write(data)
        f.close()

        with open("%s/nginx_templates/nginx.tmpl" % (
                settings.REPO_DIR), "r") as nginx_conf_file:
            data = nginx_conf_file.read()

        f = open("/etc/nginx/nginx.conf", "w")
        f.write(data)
        f.close()

        with open("%s/nginx_templates/%s.tmpl" % (
                settings.REPO_DIR, env), "r") as site_file:
            data = site_file.read()
            domains = ""
            if settings.ALLOWED_HOSTS == ["*"]:
                domains_pipe = "localhost"
                domains_space = "localhost"
            else:
                for item in settings.ALLOWED_HOSTS:
                    domains += "|" + item
                domains_pipe = domains[1:]
                domains_space = domains_pipe.replace("|", " ")
            project_name = settings.PROJECT_DIR[settings.PROJECT_DIR.rfind(
                '/') + 1:]
            data = data.replace("{{APP_NAME}}", os.environ.get("APP_NAME", ""))
            data = data.replace("{{PROJECT_NAME}}", project_name)
            data = data.replace("{{PROJECT_PATH}}", settings.PROJECT_DIR)
            data = data.replace("{{APP_PATH}}", settings.PROJECT_DIR)
            data = data.replace("{{PROJECT_DIRECTORY}}", settings.REPO_DIR)
            data = data.replace("{{DOMAINS_PIPE}}", domains_pipe)
            data = data.replace("{{DOMAINS_SPACE}}", domains_space)
            data = data.replace("{{STATIC_URL}}", settings.STATIC_URL)
            data = data.replace("{{SSL_CERT_LOCATION}}",
                                "/home/apps/%s/certs/cert.pem" %
                                os.environ.get("PROJECT_REPONAME", ""))
            data = data.replace("{{SSL_KEY_LOCATION}}",
                                "/home/apps/%s/certs/key.pem" %
                                os.environ.get("PROJECT_REPONAME", ""))
        f = open("/etc/nginx/sites-available/%s.conf" % env, "w")
        f.write(data)
        f.close()
        if os.path.isfile("/etc/nginx/sites-enabled/%s.conf" % env):
            os.remove("/etc/nginx/sites-enabled/%s.conf" % env)
        call("sudo ln -s /etc/nginx/sites-available/%s.conf" % (env) +
             " /etc/nginx/sites-enabled/%s.conf" % (env), shell=True)
        call("sudo chown -R root:root /etc/nginx/", shell=True)
        return True

    def handle(self, *args, **options):
        self.populate_nginx(args[0], args[1])
        self.stdout.write("NGINX Files populated")
