from celery import shared_task

from .neo_models import SBGarbageCan
from .utils import (delete_comments_util, delete_posts_util)


@shared_task()
def empty_garbage_can():
    try:
        garbage_can = SBGarbageCan.index.get(garbage_can='garbage')
        delete_posts_util(garbage_can)
        delete_comments_util(garbage_can)
        # delete_plebs_util(garbage_can)
        #delete_questions_util(garbage_can)
        #delete_answers_util(garbage_can)
        #delete_notifications_util(garbage_can)
    except SBGarbageCan.DoesNotExist:
        garbage_can = SBGarbageCan(garbage_can='garbage')
        garbage_can.save()
        empty_garbage_can()
        # delete_plebs_util(garbage_can)
        #delete_questions_util(garbage_can)
        #delete_answers_util(garbage_can)
        #delete_notifications_util(garbage_can)