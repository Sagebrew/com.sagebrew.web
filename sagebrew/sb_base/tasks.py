import logging
from celery import shared_task
from neomodel.exception import CypherException, DoesNotExist
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion

from .utils import defensive_exception

logger = logging.getLogger("loggly_logs")


@shared_task()
def create_object_relations_task(sb_object, current_pleb, question=None,
                                 wall_pleb=None):
    try:
        current_pleb = Pleb.nodes.get(email=current_pleb)
        if wall_pleb is not None:
            wall_pleb = Pleb.nodes.get(email=wall_pleb)
            wall = wall_pleb.wall.all()[0]
        else:
            wall = None
    except (CypherException, DoesNotExist, Pleb.DoesNotExist) as e:
        raise create_object_relations_task.retry(exc=e, countdown=3,
                                                 max_retries=None)
    except IndexError as e:
        raise create_object_relations_task.retry(exc=e, countdown=3,
                                                 max_retries=None)

    if question is not None:
        try:
            question = SBQuestion.nodes.get(sb_id=question)
        except(CypherException, DoesNotExist, SBQuestion.DoesNotExist) as e:
            raise create_object_relations_task.retry(exc=e, countdown=3,
                                                     max_retries=None)
        res = sb_object.create_relations(current_pleb, question, wall)
        if isinstance(res, Exception) is True:
            raise create_object_relations_task.retry(exc=res, countdown=3,
                                                     max_retries=None)
        return True
