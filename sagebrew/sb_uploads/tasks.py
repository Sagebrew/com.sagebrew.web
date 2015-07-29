"""
from django.core.cache import cache

from celery import shared_task
from neomodel import (DoesNotExist, CypherException)

from plebs.neo_models import Pleb
from .utils import crop_image


@shared_task()
def crop_image_task(image, height, width, x, y, pleb, f_uuid=None):
    try:
        pleb = Pleb.get(username=pleb)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise crop_image_task.retry(exc=e, countdown=3, max_retries=None)
    res = crop_image(image, int(height), int(width), int(x), int(y), f_uuid)
    if isinstance(res, Exception):
        raise crop_image_task.retry(exc=res, countdown=3, max_retries=None)
    try:
        pleb.profile_pic = res
        pleb.save()
        pleb.refresh()
        cache.set(pleb.username, pleb)
    except (CypherException, IOError) as e:
        raise crop_image_task.retry(exc=e, countdown=3, max_retries=None)
    return True
"""