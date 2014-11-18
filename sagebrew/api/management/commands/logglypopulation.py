import socket

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    args = 'None.'

    def populate_rsys_log(self, account, token_value):
        with open ("%s/rsyslog_template.conf" % settings.REPO_DIR,
                   "r") as rsys_log:
            data = rsys_log.read().replace('{{LOG_ACCOUNT}}', account)
            data = data.replace('{{TOKEN}}', token_value)
            data = data.replace('{{HOST}}', "sb_%s" % socket.gethostname())
        f = open("/etc/rsyslog.d/sagebrew.conf", "w")
        f.write(data)
        f.close()

    def handle(self, *args, **options):
        self.populate_rsys_log(args[0], args[1])
        self.stdout.write("Populate RSYS Log completed")