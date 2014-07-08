import pytz
from uuid import uuid1

from datetime import datetime

from sb_comments.neo_models import SBComment
from sb_posts.neo_models import SBPost
from plebs.neo_models import Pleb

from celery import shared_task

@shared_task()
def save_comment_task(comment_info):
    pass

@shared_task()
def edit_comment_task(comment_info):
    pass

@shared_task()
def delete_comment_task(comment_info):
    pass

@shared_task()
def create_upvote_comment(comment_info):
    pass

@shared_task()
def create_downvote_comment(comment_info):
    pass

@shared_task()
def submit_comment_on_post(comment_info):
    pass

@shared_task()
def submit_comment_on_question(comment_info):
    pass

@shared_task()
def submit_comment_on_answer(comment_info):
    pass