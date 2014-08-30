import os

import socket
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    args = 'None.'

    def prep_rsys(self):
        path = "/etc/rsyslog.d/"
        for root, dirs, files in os.walk(path):
          for directory in dirs:
            os.chown(os.path.join(root, directory), 502, 20)

    def handle(self, *args, **options):
        self.prep_rsys()

