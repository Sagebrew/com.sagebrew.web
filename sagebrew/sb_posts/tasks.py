from uuid import uuid1
from django.conf import settings

from celery import shared_task

from .neo_models import SBPost
from api.utils import assign_data
from plebs.neo_models import Pleb
from sb_notifications.tasks import prepare_post_notification_data
from .utils import (save_post, edit_post_info, delete_post_info)


@shared_task()
def delete_post_and_comments(post_info):
    '''
    called by the garbage can to delete each post (and all comments attached to post)
    in the can

    :param post_info:
    :return:
    '''
    if delete_post_info(post_info):
        return {'detail': 'post and comments deleted'}
    else:
        task_id = str(uuid1())
        assign_data(post_info, delete_post_and_comments, 2, task_id)
        delete_post_and_comments.apply_async([post_info,], countdown=2, task_id=task_id)
        return {'detail': 'failed to delete', 'response': 'retrying'}



#TODO only allow plebs to change vote
@shared_task()
def create_upvote_post(post_uuid=str(uuid1()), pleb=""):
    '''
    creates an upvote attached to a post

    :param post_info:
                    post_uuid = str(uuid)
                    pleb = "" email
    :return:
    '''
    try:
        my_post = SBPost.index.get(post_id = post_uuid)
        my_pleb = Pleb.index.get(email = pleb)
        my_post.up_vote_number += 1
        my_post.up_voted_by.connect(my_pleb)
        my_post.save()
        return {'detail': 'upvote created'}
    except SBPost.DoesNotExist:
        create_upvote_post.apply_async(args=[post_uuid,pleb])
        return {'detail': 'post not found', 'response': 'retrying'}
    except Exception, e:
        return {'detail': 'unknown exception', 'exception': e, 'response': 'logging'}


#TODO only allow plebs to change vote
@shared_task()
def create_downvote_post(post_uuid=str(uuid1()), pleb=""):
    '''
    creates a downvote attached to a post

    :param post_info:
                    post_uuid = str(uuid)
                    pleb = "" email
    :return:
    '''
    try:
        my_post = SBPost.index.get(post_id = post_uuid)
        my_pleb = Pleb.index.get(email = pleb)
        my_post.down_vote_number += 1
        my_post.down_voted_by.connect(my_pleb)
        my_post.save()
        return {'detail': 'downvote created'}
    except SBPost.DoesNotExist:
        create_downvote_post.apply_async(args=[post_uuid,pleb])
        return {'detail': 'post not found', 'response': 'retrying'}
    except Exception, e:
        return {'detail': 'unknown exception', 'exception': e, 'response': 'logging'}

@shared_task()
def save_post_task(post_info):
    '''
    Saves the post with the content sent to the task

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
        my_post = save_post(**post_info)
        if my_post is not None:
            #prepare_post_notification_data.apply_async([my_post,])
            return {'detail': 'post saved', 'response': 'spawning notification task'}
        else:
            return {'detail': 'post save failed', 'response': 'logging'}
    except Exception, e:
        return {'detail': 'post save failed', 'exception': e, 'response': 'logging'}

@shared_task()
def edit_post_info_task(post_info):
    '''
    Edits the content of the post also updates the last_edited_on value
    if the task returns that it cannot find the post it retries
    :param post_info:
    :return:
        #TODO Log returns
        Return Possibilities:
            {'detail': 'post edited'}
                Returns if there were not problems while attempting to edit the post

            {'detail': 'post does not exist yet'}
                Returns if edit_post_info util cannot find the post,
                causes the task to spawn another one of itself. This is here to
                prevent a race condition of a post getting created then instantly
                edited causing the task to fail out

            {'detail': 'to be deleted'}
                Returns if the post that is trying to be edited is in the garbage
                can waiting to be deleted

                If unexpected:
                    check the posts to_be_deleted property, if it is set to True
                    you will get this return

            {'detail': 'content is the same'}
                Returns if the content of the post is the same as what the user
                attempted to edit it to

            {'detail': 'edit time stamps are the same'}
                Returns if the time that the post is attempted to edited is the same as
                the last_edited_on property of the post.

                If you get this return:
                    This is a very unlikely return, if you get this check to make sure your
                    datetime generation is correct

            {'detail': 'there was a more recent edit'}
                Returns if the last_edited_on property of the post is more recent than the
                edit attempt timestamp
    '''
    edit_post_return = edit_post_info(**post_info)
    if edit_post_return['detail'] == 'post edited':
        return True
    if edit_post_return['detail'] == 'post does not exist yet':
        task_id = str(uuid1())
        edit_post_info_task.apply_async([post_info,], countdown=1, task_id=task_id)
        return {'detail': 'waiting for next task', 'task_id': task_id}
    if edit_post_return['detail'] == 'content is the same':
        return {'detail': edit_post_return['detail']}
    if edit_post_return['detail'] == 'to be deleted':
        return {'detail': 'post to be deleted'}
    if edit_post_return['detail'] == 'time stamp is the same':
        return {'detail': 'edit time stamps are the same'}
    if edit_post_return['detail'] == 'last edit more recent':
        return {'detail': 'there was a more recent edit'}
