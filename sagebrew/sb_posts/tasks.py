from uuid import uuid1
from celery import shared_task
from logging import getLogger

from sb_notifications.tasks import create_notification_post_task
from api.utils import spawn_task
from .neo_models import SBPost
from plebs.neo_models import Pleb
from .utils import (save_post, edit_post_info, delete_post_info, flag_post)

logger = getLogger('loggly_logs')

@shared_task()
def delete_post_and_comments(post_info):
    '''
    called by the garbage can to delete each post (and all comments attached
    to post)
    in the can

    :param post_info:
    :return:
    '''
    if delete_post_info(post_info):
        return True
    else:
        raise delete_post_and_comments.retry(exc=Exception, countdown=3,
                                             max_retries=None)

@shared_task()
def create_upvote_post(post_uuid=str(uuid1()), pleb=""):
    '''
    creates an upvote attached to a post

    Unless testing this should only be called from the create_post_vote
    util
    :param post_info:
                    post_uuid = str(uuid)
                    pleb = "" email
    :return:
    '''
    try:
        my_post = SBPost.nodes.get(post_id=post_uuid)
        my_pleb = Pleb.nodes.get(email=pleb)
        my_post.up_vote_number += 1
        my_post.up_voted_by.connect(my_pleb)
        my_post.save()
        return True
    except SBPost.DoesNotExist:
        logger.exception({"function": create_upvote_post.__name__,
                          "exception": "UnhandledException: "})
        raise create_upvote_post.retry(exc=Exception, countdown=3,
                                       max_retries=None)

@shared_task()
def create_downvote_post(post_uuid=str(uuid1()), pleb=""):
    '''
    creates a downvote attached to a post

    Unless testing this should only be called from the create_post_vote
    util
    :param post_info:
                    post_uuid = str(uuid)
                    pleb = "" email
    :return:
    '''
    try:
        my_post = SBPost.nodes.get(post_id=post_uuid)
        my_pleb = Pleb.nodes.get(email=pleb)
        my_post.down_vote_number += 1
        my_post.down_voted_by.connect(my_pleb)
        my_post.save()
        return True
    except SBPost.DoesNotExist:
        logger.exception({"function": create_downvote_post.__name__,
                          "exception": "SBPost.DoesNotExist"})
        raise create_downvote_post.retry(exc=Exception, countdown=3,
                                         max_retries=None)


@shared_task()
def save_post_task(content="", current_pleb="", wall_pleb="",
                   post_uuid=str(uuid1())):
    '''
    Saves the post with the content sent to the task

    If the task fails the failure_dict gets sent to the queue
    :param post_info:
                post_info = {
                    'content': "this is a post",
                    'current_pleb': "tyler.wiersing@gmail.com",
                    'wall_pleb': "devon@sagebrew.com",
                    'post_uuid': str(uuid1())
                }
    :return:
        Returns True if the prepare_post_notification task is spawned and
        the post is successfully created
    '''
    try:
        my_post = save_post(post_uuid=post_uuid, content=content,
                            current_pleb=current_pleb, wall_pleb=wall_pleb)
        if my_post==False:
            return False
        elif my_post is not None:
            notification_data={'post_uuid': my_post.post_id,
                               'from_pleb':current_pleb, 'to_pleb': wall_pleb}
            spawn_task(task_func=create_notification_post_task,
                       task_param=notification_data)
            return True
        raise Exception
    except Exception:
        logger.exception({"function": save_post_task.__name__,
                          "exception": "UnhandledException: "})
        raise save_post_task.retry(exc=Exception, countdown=3, max_retries=None)


@shared_task()
def edit_post_info_task(content="", post_uuid=str(uuid1()),
                        last_edited_on=None, current_pleb=""):
    '''
    Edits the content of the post also updates the last_edited_on value
    if the task returns that it cannot find the post it retries
    :param post_info:
    :return:
        #TODO Log returns
        Return Possibilities:
            {'detail': 'post edited'}
                Returns if there were not problems while attempting to edit
                the post

            {'detail': 'post does not exist yet'}
                Returns if edit_post_info util cannot find the post,
                causes the task to spawn another one of itself. This is here to
                prevent a race condition of a post getting created then
                instantly
                edited causing the task to fail out

            {'detail': 'to be deleted'}
                Returns if the post that is trying to be edited is in the
                garbage
                can waiting to be deleted

                If unexpected:
                    check the posts to_be_deleted property, if it is set to
                    True
                    you will get this return

            {'detail': 'content is the same'}
                Returns if the content of the post is the same as what the user
                attempted to edit it to

            {'detail': 'edit time stamps are the same'}
                Returns if the time that the post is attempted to edited is
                the same as
                the last_edited_on property of the post.

                If you get this return:
                    This is a very unlikely return, if you get this check to
                    make sure your
                    datetime generation is correct

            {'detail': 'there was a more recent edit'}
                Returns if the last_edited_on property of the post is more
                recent than the
                edit attempt timestamp
    '''
    edit_post_return = edit_post_info(content, post_uuid, last_edited_on,
                                      current_pleb)
    if edit_post_return == True:
        return True
    if edit_post_return['detail'] == 'post does not exist yet':
        logger.exception({"function": edit_post_info_task.__name__,
                          "exception": "DoesNotExist: "})
        raise edit_post_info_task.retry(exc=Exception, countdown=3,
                                        max_retries=None)
    if edit_post_return['detail'] == 'content is the same':
        return False
    if edit_post_return['detail'] == 'to be deleted':
        return False
    if edit_post_return['detail'] == 'time stamp is the same':
        return False
    if edit_post_return['detail'] == 'last edit more recent':
        return False

@shared_task()
def flag_post_task(post_uuid, current_user, flag_reason):
    '''
    This task calls the util to add a flag to a post

    :param post_uuid:
    :param current_user:
    :param flag_reason:
    :return:
    '''
    try:
        if flag_post(post_uuid=post_uuid, current_user=current_user,
                     flag_reason=flag_reason):
            return True
        raise Exception
    except Exception:
        logger.exception({"function": flag_post_task.__name__,
                          "exception": "UnhandledException: "})
        raise flag_post_task.retry(exc=Exception, countdown=3,
                                   max_retries=None)