import logging
from celery import shared_task
from neomodel.exception import CypherException, DoesNotExist

from api.utils import spawn_task
from sb_docstore.tasks import add_object_to_table_task
from plebs.neo_models import Pleb
from sb_questions.neo_models import SBQuestion

logger = logging.getLogger("loggly_logs")


@shared_task()
def create_object_relations_task(sb_object, current_pleb, question=None,
                                 wall_pleb=None):
    try:
        current_pleb = Pleb.nodes.get(username=current_pleb)
        if wall_pleb is not None:
            wall_pleb = Pleb.nodes.get(username=wall_pleb)
            wall = wall_pleb.wall.all()[0]
        else:
            wall = None
    except (CypherException, DoesNotExist, Pleb.DoesNotExist, IndexError) as e:
        raise create_object_relations_task.retry(exc=e, countdown=3,
                                                 max_retries=None)

    if question is not None:
        try:
            question = SBQuestion.nodes.get(object_uuid=question)
        except(CypherException, DoesNotExist, SBQuestion.DoesNotExist) as e:
            raise create_object_relations_task.retry(exc=e, countdown=3,
                                                     max_retries=None)
    res = sb_object.create_relations(current_pleb, question, wall)
    if isinstance(res, Exception) is True:
        raise create_object_relations_task.retry(exc=res, countdown=3,
                                                 max_retries=None)

    res = sb_object.create_view_count()
    if isinstance(res, Exception) is True:
        raise create_object_relations_task.retry(exc=res, countdown=3,
                                                 max_retries=None)

    object_data = sb_object.get_single_dict()
    if isinstance(object_data, Exception) is True:
        raise create_object_relations_task.retry(exc=object_data, countdown=3,
                                                 max_retries=None)
    try:
        object_data['parent_object'] = question.object_uuid
    except AttributeError:
        pass
    table_data = {'table': sb_object.get_table(),
                  'object_data': object_data}
    res = spawn_task(task_func=add_object_to_table_task,
                     task_param=table_data)
    if isinstance(res, Exception) is True:
        raise create_object_relations_task.retry(exc=res, countdown=3,
                                                 max_retries=None)
    return res