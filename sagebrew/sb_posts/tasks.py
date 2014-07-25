from uuid import uuid1

from celery import shared_task

from .neo_models import SBPost
from plebs.neo_models import Pleb
from sb_notifications.tasks import prepare_post_notification_data
from .utils import (save_post, edit_post_info, delete_post_info)


@shared_task()
def delete_post_and_comments(post_info):
    if delete_post_info(post_info):
        return True
    else:
        task_id = str(uuid1())
        delete_post_and_comments.apply_async([post_info,], countdown=2, task_id=task_id)
        return task_id


#TODO only allow plebs to change vote
@shared_task()
def create_upvote_post(post_id=str(uuid1()), pleb=""):
    '''
    creates an upvote attached to a post

    :param post_info:
                    post_uuid = str(uuid)
                    pleb = "" email
    :return:
    '''
    try:
        my_post = SBPost.index.get(post_id = post_id)
        my_pleb = Pleb.index.get(email = pleb)
        my_post.up_vote_number += 1
        my_post.up_voted_by.connect(my_pleb)
        my_post.save()
        return True
    except:
        return False


#TODO only allow plebs to change vote
@shared_task()
def create_downvote_post(post_id=str(uuid1()), pleb=""):
    '''
    creates a downvote attached to a post

    :param post_info:
                    post_uuid = str(uuid)
                    pleb = "" email
    :return:
    '''
    try:
        my_post = SBPost.index.get(post_id = post_id)
        my_pleb = Pleb.index.get(email = pleb)
        my_post.down_vote_number += 1
        my_post.down_voted_by.connect(my_pleb)
        my_post.save()
        return True
    except:
        return False

@shared_task()
def save_post_task(post_info):
    try:
        my_post = save_post(**post_info)
        if my_post is not None:
            #prepare_post_notification_data.apply_async([my_post,])
            return True
        else:
            return False
    except ValueError:
        return False

@shared_task()
def edit_post_info_task(post_info):
    if edit_post_info(**post_info):
        return True
    else:
        task_id = str(uuid1())
        edit_post_info_task.apply_async([post_info,], countdown=1, task_id=task_id)
        return task_id
