from celery import shared_task

from sb_news.utils import find_news
from .utils import limit_offset_query, quest_callback


@shared_task()
def find_tag_news():
    find_news(limit_offset_query, 'MATCH (quest:Quest) RETURN count(quest)',
              quest_callback)
