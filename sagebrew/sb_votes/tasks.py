from uuid import uuid1
from celery import shared_task

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from plebs.tasks import update_reputation
from plebs.neo_models import Pleb
from sb_base.neo_models import get_parent_votable_content
from sb_notifications.tasks import spawn_notifications

from logging import getLogger
logger = getLogger("loggly_logs")

@shared_task()
def vote_object_task(vote_type, current_pleb, object_uuid):
    """
    This function takes a pleb object, an
    sb_object(Solution, Question, Comment, Post), and a
    vote_type(True, False) it will then call a method to handle the vote
    operations on the sb_object.

    :param vote_type:
    :param current_pleb:
    :param sb_object:
    :return:
    """
    try:
        current_pleb = Pleb.get(username=current_pleb)
    except (DoesNotExist, Pleb.DoesNoteExist, CypherException, IOError) as e:
        raise vote_object_task.retry(exc=e, countdown=10, max_retries=None)
    sb_object = get_parent_votable_content(object_uuid)
    if isinstance(sb_object, Exception) is True:
        raise vote_object_task.retry(exc=sb_object, countdown=10,
                                     max_retries=None)

    res = sb_object.vote_content(vote_type, current_pleb)

    if isinstance(res, Exception) is True:
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    res = spawn_task(update_reputation, {"username": sb_object.owner_username})

    if isinstance(res, Exception):
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)
    logger.info(sb_object)
    logger.info({
        'from_pleb': current_pleb,
        'to_plebs': [sb_object.owner_username],
        'sb_object': sb_object.object_uuid,
        'notification_id': str(uuid1()),
        'url': "",
        'action_name': "%s %s %s %s " % (current_pleb.first_name,
                                         current_pleb.last_name, "voted on your",
                                         sb_object.get_child_label())
    })
    res = spawn_task(spawn_notifications, task_param={
        'from_pleb': current_pleb,
        'to_plebs': [sb_object.owner_username],
        'sb_object': sb_object.object_uuid,
        'notification_id': str(uuid1()),
        'url': "",
        'action_name': "%s %s %s %s " % (current_pleb.first_name,
                                         current_pleb.last_name, "voted on your",
                                         sb_object.get_child_label())
    })

    if isinstance(res, Exception):
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    return sb_object
