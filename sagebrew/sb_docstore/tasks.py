from celery import shared_task

from django.conf import settings

from neomodel.exception import DoesNotExist, CypherException

from plebs.neo_models import Pleb
from sb_public_official.neo_models import BaseOfficial
from sb_public_official.utils import get_rep_type
from sb_questions.neo_models import SBQuestion

from .utils import (build_question_page, add_object_to_table, build_wall_docs,
                    build_rep_page, build_privileges)

@shared_task()
def build_question_page_task(question_uuid, question_table, solution_table):
    try:
        question = SBQuestion.nodes.get(object_uuid=question_uuid)
    except (SBQuestion.DoesNotExist, DoesNotExist) as e:
        raise build_question_page_task.retry(exc=e, countdown=3,
                                             max_retries=None)
    res = build_question_page(question, question_table, solution_table)
    if isinstance(res, Exception):
        raise build_question_page_task.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def add_object_to_table_task(object_data, table):
    res = add_object_to_table(table_name=table, object_data=object_data)
    if isinstance(res, Exception) is True:
        raise add_object_to_table_task.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def build_wall_task(username):
    try:
        pleb_obj = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        raise build_question_page_task.retry(exc=e, countdown=3,
                                             max_retries=None)
    res = build_wall_docs(pleb_obj)
    if isinstance(res, Exception):
        raise build_wall_task.retry(exc=res, countdown=3, max_retries=None)

    return True


@shared_task()
def build_rep_page_task(rep_id, rep_type=None):
    if rep_type is None:
        try:
            rep = BaseOfficial.nodes.get(object_uuid=rep_id)
        except (BaseOfficial.DoesNotExist, DoesNotExist, CypherException) as e:
            raise build_rep_page_task.retry(exc=e, countdown=3, max_retries=None)
    else:
        r_type = get_rep_type(dict(settings.BASE_REP_TYPES)[rep_type])
        try:
            rep = r_type.nodes.get(object_uuid=rep_id)
        except (r_type.DoesNotExist, DoesNotExist, CypherException) as e:
            return e
    res = build_rep_page(rep)
    if isinstance(res, Exception):
        raise build_rep_page_task.retry(exc=res, countdown=3, max_retries=None)
    return True


@shared_task()
def build_user_privilege_task(username):
    try:
        pleb_obj = Pleb.nodes.get(username=username)
    except (Pleb.DoesNotExist, DoesNotExist, CypherException) as e:
        return e
    res = build_privileges(pleb_obj)
    if isinstance(res, Exception):
        raise build_user_privilege_task.retry(exc=res, countdown=3,
                                              max_retries=None)
    return True