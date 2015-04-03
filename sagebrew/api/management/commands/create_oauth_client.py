from os import environ
from uuid import uuid1
from django.core import signing
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from sb_oauth.models import SBApplication


class Command(BaseCommand):
    args = 'None.'

    def create_oauth_client(self):
        password = (signing.dumps(str(uuid1()))+signing.dumps(str(uuid1())))[
                   :128]
        try:
            oauth_user = User.objects.get(username=environ.get("APP_USER",""))
        except User.DoesNotExist:
            oauth_user = User.objects.create_user(username=environ.get(
                "APP_USER", ""), password=password)

        try:
            SBApplication.objects.get(client_id=settings.OAUTH_CLIENT_ID)
        except SBApplication.DoesNotExist:
            SBApplication.objects.create(
                client_id=settings.OAUTH_CLIENT_ID,
                user=oauth_user, redirect_uris="%s%s" % (
                    settings.WEB_ADDRESS, '/login'),
                client_type='confidential',
                authorization_grant_type="password",
                client_secret=settings.OAUTH_CLIENT_SECRET,
                name=oauth_user.username)

        try:
            oauth_user2 = User.objects.get(username=environ.get(
                "CRED_USER", ""))
        except User.DoesNotExist:
            oauth_user2 = User.objects.create_user(
                username=environ.get("CRED_USER", ""),
                password=environ.get("CRED_PASSWORD"))
            oauth_user2.is_superuser = True
            oauth_user2.is_staff = True
            oauth_user2.save()
        try:
            SBApplication.objects.get(client_id=settings.OAUTH_CLIENT_ID_CRED)
        except SBApplication.DoesNotExist:
            SBApplication.objects.create(
                client_id=settings.OAUTH_CLIENT_ID_CRED, user=oauth_user2,
                redirect_uris="%s%s" % (settings.WEB_ADDRESS, '/login'),
                client_type='confidential',
                authorization_grant_type="password",
                client_secret=settings.OAUTH_CLIENT_SECRET_CRED,
                name=oauth_user2.username, web_hook="http://localhost")

    def handle(self, *args, **options):
        self.create_oauth_client()
        print "OAuth2.0 Client Created"
