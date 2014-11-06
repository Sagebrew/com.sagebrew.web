import logging
from json import dumps
from celery import shared_task

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task

from .utils import save_comment_post

logger = logging.getLogger('loggly_logs')


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
