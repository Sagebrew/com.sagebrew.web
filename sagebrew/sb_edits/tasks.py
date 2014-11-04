from celery import shared_task


@shared_task()
def edit_object_task(object_uuid, object_type, current_pleb, content,
                     question_title=None):
    pass