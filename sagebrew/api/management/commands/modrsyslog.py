import os
import pwd
import grp
import socket
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    args = 'None.'
    def add_arguments(self, parser):
        parser.add_argument('user', nargs='+', type=str)

    def prep_rsys(self, user):
        path = "/etc/rsyslog.d/"
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(user).gr_gid
        for root, dirs, files in os.walk(path):
          for directory in dirs:
            os.chown(os.path.join(root, directory), uid, gid)

    def handle(self, *args, **options):
        self.prep_rsys(options['user'])

