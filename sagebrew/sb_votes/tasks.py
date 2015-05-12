from celery import shared_task

from neomodel import CypherException, DoesNotExist

from api.utils import spawn_task
from plebs.tasks import update_reputation
from plebs.neo_models import Pleb
from sb_base.neo_models import get_parent_votable_content


@shared_task()
def vote_object_task(vote_type, current_pleb, object_uuid):
    '''
    This function takes a pleb object, an
    sb_object(Solution, Question, Comment, Post), and a
    vote_type(True, False) it will then call a method to handle the vote
    operations on the sb_object.

    :param vote_type:
    :param current_pleb:
    :param sb_object:
    :return:
    '''
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

    res = spawn_task(update_reputation,
                     {"username": sb_object.owned_by.all()[0].username})

    if isinstance(res, Exception):
        raise vote_object_task.retry(exc=res, countdown=10, max_retries=None)

    return sb_object
