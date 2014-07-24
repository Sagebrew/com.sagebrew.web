from uuid import uuid1

from celery import shared_task

from .neo_models import SBGarbageCan
from .utils import (delete_comments_util, delete_posts_util)
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb


@shared_task()
def empty_garbage_can():
    try:
        print "utils begun"
        garbage_can = SBGarbageCan.index.get(garbage_can='garbage')
        delete_posts_util(garbage_can)
        delete_comments_util(garbage_can)
        #delete_plebs_util(garbage_can)
        #delete_questions_util(garbage_can)
        #delete_answers_util(garbage_can)
        #delete_notifications_util(garbage_can)
    except SBGarbageCan.DoesNotExist:
        garbage_can = SBGarbageCan(garbage_can='garbage')
        print "garbage_can created and utils begun"
        garbage_can.save()
        delete_posts_util(garbage_can)
        delete_comments_util(garbage_can)
        #delete_plebs_util(garbage_can)
        #delete_questions_util(garbage_can)
        #delete_answers_util(garbage_can)
        #delete_notifications_util(garbage_can)