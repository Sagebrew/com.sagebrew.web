import logging
from json import dumps
from celery import shared_task

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task

from .utils import (save_comment_post, edit_comment_util)

logger = logging.getLogger('loggly_logs')


@shared_task()
def edit_comment_task(comment_uuid, content, last_edited_on):
    '''
    Task to edit a comment and update the last_edited_on value of the comment


    :param comment_uuid:
    :param content:
    :param last_edited_on:
    :return:
            Will return True if the comment was succesfully edited

            Will return False if the task failed and spawns another task

            Will return an exception if something else occurred while trying
            to edit
    '''
    try:
        response = edit_comment_util(comment_uuid, content, last_edited_on)
        if response is True:
            return True
        elif isinstance(response, Exception) is True:
            raise edit_comment_task.retry(exc=response, countdown=3,
                                          max_retries=None)
        else:
            return False
    except Exception as e:
        logger.exception(dumps({"function": edit_comment_task.__name__,
                                "exception": "Unhandled Exception"}))
        raise edit_comment_task.retry(exc=e, countdown=3,
                                      max_retries=None)


@shared_task()
def submit_comment_on_post(content, pleb, post_uuid):
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
    # TODO can't this be generalized to just create a comment on a given
    # object?
    try:
        my_comment = save_comment_post(content, pleb, post_uuid)
        if isinstance(my_comment, Exception) is True:
            raise submit_comment_on_post.retry(exc=my_comment, countdown=5,
                                               max_retries=None)
        elif my_comment is False:
            return False
        else:
            from_pleb = my_comment.is_owned_by.all()[0]
            post = my_comment.commented_on_post.all()[0]
            to_plebs = post.owned_by.all()
            data = {'from_pleb': from_pleb, 'to_plebs': to_plebs,
                    'sb_object': my_comment}
            spawn_task(task_func=spawn_notifications, task_param=data)
            return True
    except IndexError as e:
        raise submit_comment_on_post.retry(exc=e, countdown=5, max_retries=None)
    except Exception as e:
        logger.exception(dumps({'function': submit_comment_on_post.__name__,
                                'exception': "Unhandled Exception"}))
        raise submit_comment_on_post.retry(exc=e, countdown=5, max_retries=None)


@shared_task()
def submit_comment_on_question(comment_info):
    pass


@shared_task()
def submit_comment_on_answer(comment_info):
    pass
