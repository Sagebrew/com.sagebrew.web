import shortuuid
from django.db import models
from oauth2_provider.models import AbstractApplication


def generate_client_id():
    return shortuuid.ShortUUID().random(length=50)


def generate_client_secret():
    return shortuuid.ShortUUID().random(length=124)


class SBApplication(AbstractApplication):
    web_hook = models.URLField()
    AbstractApplication._meta.get_field(
        'client_id').default = generate_client_id
    AbstractApplication._meta.get_field(
        'client_secret').default = generate_client_secret