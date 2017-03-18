from celery import shared_task

from sagebrew.sb_privileges.utils import manage_privilege_relation


@shared_task()
def check_privileges(username):
    res = manage_privilege_relation(username)
    if isinstance(res, Exception):  # pragma: no cover
        # Not covered because we cannot programmaticly reproduce this in a
        # consistent manner. - Devon Bleibtrey
        raise check_privileges.retry(exc=res, countdown=3, max_retries=None)
    return True
