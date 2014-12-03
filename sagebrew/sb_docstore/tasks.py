from celery import shared_task

from .utils import build_question_page

@shared_task()
def build_question_page_task(question_uuid, question_table, solution_table):
    #TODO review this task
    res = build_question_page(question_uuid, question_table, solution_table)
    if isinstance(res, Exception):
        raise build_question_page_task.retry(exc=res, countdown=3,
                                             max_retries=None)

    return True