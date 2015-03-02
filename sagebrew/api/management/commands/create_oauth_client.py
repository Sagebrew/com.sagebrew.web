from os import environ
from uuid import uuid1
from django.core import signing
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from oauth2_provider.models import Application, get_application_model

class Command(BaseCommand):
    args = 'None.'

    def create_oauth_client(self):
        password = (signing.dumps(str(uuid1()))+signing.dumps(str(uuid1())))[
                                               :128]
        try:
            oauth_user = User.objects.get(username=environ.get("APP_USER",""))
        except User.DoesNotExist:
            oauth_user = User(username=environ.get("APP_USER", ""),
                          password=password)
            oauth_user.save()
        application = Application(client_id=settings.OAUTH_CLIENT_ID,
                                  user=oauth_user,
                                  redirect_uris=settings.WEB_ADDRESS+'/login',
                                  client_type='confidential',
                                  authorization_grant_type="password",
                                  client_secret=settings.OAUTH_CLIENT_SECRET,
                                  name=oauth_user.username)
        application.save()

    def handle(self, *args, **options):
        self.create_oauth_client()
        print "OAuth2.0 Client Created"
