from json import dumps

from celery import shared_task
from logging import getLogger

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task
from plebs.neo_models import Pleb
from .utils import (save_post, edit_post_info, delete_post_info)

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
    response = delete_post_info(post_info)
    if isinstance(response, Exception) is True:
        raise delete_post_and_comments.retry(exc=response, countdown=3,
                                             max_retries=None)
    else:
        return response


@shared_task()
def save_post_task(content, current_pleb, wall_pleb, post_uuid=None):
    '''
    Saves the post with the content sent to the task

    If the task fails the failure_dict gets sent to the queue
    :param content: "this is a post",
    :param current_pleb: "tyler.wiersing@gmail.com",
    :param wall_pleb: "devon@sagebrew.com",
    :param post_uuid: String version of a UUID
    :return:
        Returns True if the prepare_post_notification task is spawned and
        the post is successfully created
    '''
    try:
        my_post = save_post(post_uuid=post_uuid, content=content,
                            current_pleb=current_pleb, wall_pleb=wall_pleb)
        if isinstance(my_post, Exception) is True:
            raise save_post_task.retry(exc=my_post, countdown=3,
                                       max_retries=None)
        elif my_post is False:
            return False

        else:
            # TODO maybe we should pass the entire
            # pleb rather than just the email, since just do another query in
            # the util anyways and will need to do one for the notification
            notification_data={'sb_object': my_post,
                               'from_pleb': Pleb.nodes.get(email=current_pleb),
                               'to_plebs': [Pleb.nodes.get(email=wall_pleb),]}
            spawn_task(task_func=spawn_notifications,
                       task_param=notification_data)
            return True
    except Exception as e:
        logger.exception(dumps({"function": save_post_task.__name__,
                                "exception": "Unhandled Exception"}))
        raise save_post_task.retry(exc=e, countdown=3, max_retries=None)


@shared_task()
def edit_post_info_task(post_uuid, content, last_edited_on):
    '''
    Edits the content of the post also updates the last_edited_on value
    if the task returns that it cannot find the post it retries
    :param last_edited_on:
    :param post_uuid
    :param content
    :return:
    '''
    edit_post_return = edit_post_info(post_uuid, content, last_edited_on)
    if isinstance(edit_post_return, Exception):
        raise edit_post_info_task.retry(exc=edit_post_return, countdown=3,
                                        max_retries=None)
    else:
        return edit_post_return