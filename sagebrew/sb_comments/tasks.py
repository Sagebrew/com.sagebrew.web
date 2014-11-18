from celery import shared_task

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task, get_object
from sb_base.utils import defensive_exception

from .utils import save_comment, comment_relations


@shared_task()
def save_comment_on_object(content, current_pleb, object_uuid, object_type):
    '''
    The task which creates a comment and attaches it to an object.

    The objects can be: SBPost, SBAnswer, SBQuestion.

    :param content:
    :param current_pleb:
    :param object_uuid:
    :param object_type:
    :return:
            Will return True if the comment was made and the task to spawn a
            notification was created

            Will return false if the comment was not created
    '''
    try:
        sb_object = get_object(object_type, object_uuid)
        if isinstance(sb_object, Exception) is True:
            raise save_comment_on_object.retry(exc=sb_object, countdown=5,
                                               max_retries=None)

        my_comment = save_comment(content)

        if isinstance(my_comment, Exception) is True:
            raise save_comment_on_object.retry(exc=my_comment, countdown=5,
                                               max_retries=None)
        elif my_comment is False:
            return my_comment
        else:
            task_data = {"current_pleb": current_pleb, "comment": my_comment,
                         "sb_object": sb_object}
            spawn_task(task_func=create_comment_relations,
                       task_param=task_data)
            return True
    except Exception as e:
        raise defensive_exception(save_comment_on_object.__name__, e,
                                  save_comment_on_object.retry(
                                      exc=e, countdown=5, max_retries=None))


@shared_task()
def create_comment_relations(current_pleb, comment, sb_object):
    try:
        res = comment_relations(current_pleb, comment, sb_object)

        if isinstance(res, Exception) is True:
            raise create_comment_relations.retry(exc=res, countdown=3,
                                                 max_retries=None)

        to_plebs = sb_object.owned_by.all()
        data = {'from_pleb': current_pleb, 'to_plebs': to_plebs,
                'sb_object': comment}
        spawn_task(task_func=spawn_notifications, task_param=data)
        return True
    except Exception as e:
        raise defensive_exception(create_comment_relations.__name__, e,
                                  create_comment_relations.retry(
                                      exc=e, countdown=3, max_retries=None))
