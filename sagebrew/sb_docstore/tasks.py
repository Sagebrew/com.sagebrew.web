from celery import shared_task

from neomodel.exception import DoesNotExist, CypherException

from .utils import (build_question_page, add_object_to_table, build_wall_docs,
                    build_rep_page, build_privileges)
from plebs.neo_models import Pleb


@shared_task()
def build_question_page_task(question_uuid, question_table, solution_table):
    res = build_question_page(question_uuid, question_table, solution_table)
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
        return e
    res = build_wall_docs(pleb_obj)
    if isinstance(res, Exception):
        raise build_wall_task.retry(exc=res, countdown=3, max_retries=None)

    return True


@shared_task()
def build_rep_page_task(rep_id, rep_type=None):
    res = build_rep_page(rep_id, rep_type)
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