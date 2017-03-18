from celery import shared_task

from sagebrew.sb_tags.utils import limit_offset_query
from .utils import find_news, tag_callback


@shared_task()
def find_tag_news():
    find_news(limit_offset_query,
              'MATCH (tag:Tag) WHERE NOT tag:AutoTag RETURN count(tag)',
              tag_callback)
    return True
