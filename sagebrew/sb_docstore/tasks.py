from celery import shared_task

from .utils import (build_question_page, add_object_to_table, build_wall_docs,
                    build_rep_page)


@shared_task()
def build_question_page_task(question_uuid, question_table, solution_table):
    res = build_question_page(question_uuid, question_table, solution_table)
    if isinstance(res, Exception):
        raise build_question_page_task.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def add_object_to_table_task(object_data, table):
    print object_data
    res = add_object_to_table(table_name=table, object_data=object_data)
    if isinstance(res, Exception) is True:
        raise add_object_to_table_task.retry(exc=res, countdown=3,
                                             max_retries=None)
    return True


@shared_task()
def build_wall_task(pleb):
    res = build_wall_docs(pleb)
    if isinstance(res, Exception):
        raise build_wall_task.retry(exc=res, countdown=3, max_retries=None)

    return True


@shared_task()
def build_rep_page_task(rep_id):
    res = build_rep_page(rep_id)
    if isinstance(res, Exception):
        raise build_rep_page_task.retry(exc=res, countdown=3, max_retries=None)
    return True