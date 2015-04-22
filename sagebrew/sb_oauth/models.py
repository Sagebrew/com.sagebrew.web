from django.db import models
from oauth2_provider.models import AbstractApplication


class SBApplication(AbstractApplication):
    web_hook = models.URLField()
