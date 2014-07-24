from uuid import uuid1

from celery import shared_task

from .utils import (create_notification_post_util, create_notification_comment_util)
from .neo_models import NotificationBase
from plebs.neo_models import Pleb



@shared_task()
def prepare_post_notification_data(instance):
    try:
        from_pleb = instance.traverse('owned_by').run()[0]
        from_pleb_email = from_pleb.email
        to_wall = instance.traverse('posted_on_wall').run()[0]
        to_pleb = to_wall.traverse('owner').run()[0]
        to_pleb_email = to_pleb.email
        data = {'post_id': instance.post_id, 'from_pleb': from_pleb_email, 'to_pleb': to_pleb_email}
        create_notification_post_task.apply_async([data,])
    except:
        print "post not ready yet, retrying"
        prepare_post_notification_data.apply_async([instance,], countdown=3)

@shared_task()
def create_notification_post_task(data):
    if create_notification_post_util(data):
        print "Notification created"
        return True
    else:
        return False

@shared_task()
def create_notification_comment_task(data):
    if create_notification_comment_util(data):
        return True
    else:
        return False