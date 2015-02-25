from celery import shared_task

from .utils import crop_image

@shared_task()
def crop_image_task(image, height, width, x, y, f_uuid=None):
    res = crop_image(image, height, width, x, y, f_uuid)
    if isinstance(res, Exception):
        raise crop_image_task.retry(exc=res, countdown=3, max_retries=None)
    return True