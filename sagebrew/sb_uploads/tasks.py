from celery import shared_task

from django.core.cache import cache

from neomodel import CypherException, DoesNotExist

from api.utils import generate_summary

from .neo_models import URLContent


@shared_task()
def create_url_content_summary_task(object_uuid):
    try:
        url_content = URLContent.nodes.get(object_uuid=object_uuid)
    except (DoesNotExist, URLContent.DoesNotExist,
            CypherException, IOError) as e:
        raise create_url_content_summary_task.retry(exc=e, countdown=5,
                                                    max_retries=None)
    summary = generate_summary(url_content.description)
    url_content.description = summary
    url_content.save()
    cache.delete(url_content.object_uuid)

    return url_content
