from celery import shared_task


@shared_task()
def vote_object_task(vote_type, current_pleb, sb_object):

    pass
