from celery import shared_task

@shared_task()
def check_privileges(username):
    pass