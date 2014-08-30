import os
import socket
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = 'None.'

    def populate_rsys_log(self):
        with open ("../rsyslog_template.conf.txt", "r") as rsys_log:
            data = rsys_log.read().replace('{{ACCOUNT}}', os.environ.get(
                "SB_LOGGLY_ACCOUNT", ""))
            data = data.replace('{{TOKEN}}', os.environ.get(
                "SB_LOGGLY_TOKEN", ""))
            data = data.replace('{{HOST}}', "sb_%s" % socket.gethostname(), "")
        f = open("/etc/rsyslog.d/sagebrew.conf", "w")
        f.write(data)
        f.close()

    def handle(self, *args, **options):
        self.populate_rsys_log()