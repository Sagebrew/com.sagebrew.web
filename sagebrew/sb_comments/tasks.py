from celery import shared_task

from neomodel.exception import CypherException, DoesNotExist

from sb_notifications.tasks import spawn_notifications
from api.utils import spawn_task, get_object
from sb_docstore.utils import add_object_to_table
from plebs.neo_models import Pleb

from .utils import save_comment, comment_relations



@shared_task()
def save_comment_on_object(content, username, object_uuid, object_type,
                           comment_uuid):
    '''
    The task which creates a comment and attaches it to an object.

    The objects can be: SBPost, SBSolution, SBQuestion.

    :param content:
    :param current_pleb:
    :param object_uuid:
    :param object_type:
    :return:
            Will return True if the comment was made and the task to spawn a
            notification was created

            Will return false if the comment was not created
    '''
    sb_object = get_object(object_type, object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise save_comment_on_object.retry(exc=sb_object, countdown=5,
                                           max_retries=None)
    elif sb_object is False:
        return sb_object

    my_comment = save_comment(content, comment_uuid)

    if isinstance(my_comment, Exception) is True:
        raise save_comment_on_object.retry(exc=my_comment, countdown=5,
                                           max_retries=None)
    task_data = {"username": username, "comment": my_comment,
                 "sb_object": sb_object}
    spawned = spawn_task(task_func=create_comment_relations,
                         task_param=task_data)
    if isinstance(spawned, Exception) is True:
        raise save_comment_on_object.retry(exc=spawned, countdown=5,
                                           max_retries=None)
    return spawned



@shared_task()
def create_comment_relations(username, comment, sb_object):
    try:
        current_pleb = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise create_comment_relations.retry(exc=e, countdown=3,
                                             max_retries=None)
    res = comment_relations(current_pleb, comment, sb_object)
    to_plebs = []
    if isinstance(res, Exception) is True:
        raise create_comment_relations.retry(exc=res, countdown=3,
                                             max_retries=None)
    dynamo_data = comment.get_single_dict()
    dynamo_data['parent_object'] = sb_object.object_uuid
    res = add_object_to_table(table_name='comments',
                              object_data=dynamo_data)
    if isinstance(res, Exception):
        raise create_comment_relations.retry(exc=res, countdown=3,
                                             max_retries=None)
    try:
        for pleb in sb_object.owned_by.all():
            to_plebs.append(pleb.username)
    except CypherException:
        raise create_comment_relations.retry(exc=res, countdown=3,
                                             max_retries=None)
    data = {'from_pleb': username, 'to_plebs': to_plebs, 'sb_object': comment}
    spawned = spawn_task(task_func=spawn_notifications, task_param=data)
    if isinstance(spawned, Exception) is True:
        raise create_comment_relations.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True
