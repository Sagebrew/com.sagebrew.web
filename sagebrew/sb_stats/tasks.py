from celery import shared_task

from .utils import update_view_count

@shared_task()
def update_view_count_task(object_type, object_uuid):
    res = update_view_count_task(object_type, object_uuid)
    if isinstance(res, Exception):
        raise update_view_count.retry(exc=res, countdown=3, max_retries=None)
    return True