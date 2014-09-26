import logging
from uuid import uuid1
from celery import shared_task

from sb_notifications.tasks import create_notification_comment_task
from api.utils import spawn_task
from .utils import (create_upvote_comment_util, create_downvote_comment_util,
                    save_comment_post, edit_comment_util, flag_comment_util)
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb

logger = logging.getLogger('loggly_logs')

@shared_task()
def edit_comment_task(comment_uuid=str(uuid1()), content="",
                      last_edited_on=None, pleb=""):
    '''
    Task to edit a comment and update the last_edited_on value of the comment


    :param comment_uuid:
    :param content:
    :param last_edited_on:
    :param pleb:
    :return:
            Will return True if the comment was succesfully edited

            Will return False if the task failed and spawns another task

            Will return an exception if something else occurred while trying
            to edit
    '''
    edit_response = edit_comment_util(comment_uuid, content, last_edited_on,
                                      pleb)
    if edit_response:
        return True

    elif edit_response['detail'] == 'retry':
        task_param = {'comment_uuid': comment_uuid,
                      'content': content,
                      'last_edited_on': last_edited_on,
                      'pleb': pleb}
        spawn_task(task_func=edit_comment_task, task_param=task_param,
                   countdown=2)
        return False
    else:
        return edit_response['exception']


@shared_task()
def create_vote_comment(pleb="", comment_uuid=str(uuid1()), vote_type=""):
    '''
    The logic to determine if a person has voted on a comment, and if they
    haven't then it creates the vote

    :param pleb:
    :param comment_uuid:
    :param vote_type:
    :return:
            Will return False if the person has already voted

            Will return True if the vote is created
    '''
    try:
        my_pleb = Pleb.nodes.get(email=pleb)
        my_comment = SBComment.nodes.get(comment_id=comment_uuid)
        if my_comment.up_voted_by.is_connected(
                my_pleb) or my_comment.down_voted_by.is_connected(my_pleb):
            return False
        else:
            if vote_type == 'up':
                res = create_upvote_comment_util(pleb=pleb,
                                                 comment_uuid=comment_uuid)
                if res:
                    return True
                elif res is None:
                    return False
                else:
                    raise Exception

            elif vote_type == 'down':
                res = create_downvote_comment_util(pleb=pleb,
                                                   comment_uuid=comment_uuid)
                if res:
                    return True
                elif res is None:
                    return False
                else:
                    raise Exception
    except Pleb.DoesNotExist:
        return False
    except SBComment.DoesNotExist:
        return False
    except Exception:
        logger.exception({"function": create_vote_comment.__name__,
                          "exception": "UnhandledException: "})
        raise create_vote_comment.retry(exc=Exception, countdown=3,
                                                    max_retries=None)



@shared_task()
def submit_comment_on_post(content="", pleb="", post_uuid=str(uuid1())):
    '''
    The task which creates a comment and attaches it to a post

    :param content:
    :param pleb:
    :param post_uuid:
    :return:
            Will return True if the comment was made and the task to spawn a
            notification was created

            Will return false if the comment was not created
    '''
    try:
        my_comment = save_comment_post(content, pleb, post_uuid)
        if my_comment is not None:
            from_pleb_email = my_comment.is_owned_by.all()[0].email
            post = my_comment.commented_on_post.all()[0]
            to_pleb_email = post.owned_by.all()[0].email
            data = {'from_pleb': from_pleb_email, 'to_pleb': to_pleb_email,
                    'comment_on': 'post', 'comment_on_id': post.post_id,
                    'comment_uuid': my_comment.comment_id}
            spawn_task(task_func=create_notification_comment_task,
            task_param=data)
            return True
        elif not my_comment:
            raise Exception
        else:
            return False
    except Exception:
        logger.exception({'function': submit_comment_on_post.__name__,
                    'exception': "UnhandledException: "})
        raise submit_comment_on_post.retry(exc=Exception, countdown=5,
                                     max_retries=None)


@shared_task()
def submit_comment_on_question(comment_info):
    pass


@shared_task()
def submit_comment_on_answer(comment_info):
    pass

@shared_task()
def flag_comment_task(comment_uuid, current_user, flag_reason):
    '''
    Calls the util to handle flagging the comment

    :param comment_uuid:
    :param current_user:
    :param flag_reason:
    :return:
    '''
    try:
        result = flag_comment_util(comment_uuid=comment_uuid, current_user=current_user,
                             flag_reason=flag_reason)
        if not result:
            return False
        elif result is None:
            raise Exception
        else:
            return True
    except Exception:
        logger.exception({"function": flag_comment_task.__name__,
                          "exception": "UnhandledException"})
        raise flag_comment_task.retry(exc=Exception, countdown=5,
                                         max_retries=None)