from celery import shared_task

from .utils import (manage_privilege_relation, create_privilege,
                    create_action, create_requirement)


@shared_task()
def check_privileges(username):
    res = manage_privilege_relation(username)
    if isinstance(res, Exception):
        raise check_privileges.retry(exc=res, countdown=3, max_retries=None)
    return True


@shared_task()
def create_privilege_task(privilege_data, actions, requirements):
    res = create_privilege(privilege_data, actions, requirements)
    if isinstance(res, Exception):
        raise create_privilege_task.retry(exc=res, countdown=3,
                                          max_retries=None)
    return True

