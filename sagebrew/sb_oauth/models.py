from logging import getLogger

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

from rest_framework.authtoken.models import Token
from oauth2_provider.models import AbstractApplication

logger = getLogger('loggly_logs')


class SBApplication(AbstractApplication):
    web_hook = models.URLField()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        logger.critical("creating token")
        Token.objects.create(user=instance)
