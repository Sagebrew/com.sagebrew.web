from os import environ
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    args = 'None.'

    def populate_rsys_log(self):
        with open("%s/rsyslog_template.conf" % settings.REPO_DIR,
                  "r") as rsys_log:
            data = rsys_log.read()
            data = data.replace('{{TOKEN}}', environ.get("SYS_LOG_TOKEN", ""))
        f = open("/etc/rsyslog.d/sagebrew.conf", "w")
        f.write(data)
        f.close()

    def handle(self, *args, **options):
        self.populate_rsys_log()
        self.stdout.write("Populate RSYS Log completed")