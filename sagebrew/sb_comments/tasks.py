from celery import shared_task
from rest_framework.reverse import reverse

from neo4j.v1 import CypherError
from neomodel import DoesNotExist

from sagebrew.api.utils import spawn_task
from sagebrew.sb_notifications.tasks import spawn_notifications
from sagebrew.sb_base.neo_models import SBContent

from sagebrew.sb_comments.neo_models import Comment


@shared_task()
def spawn_comment_notifications(object_uuid, parent_object_uuid,
                                from_pleb, notification_id,
                                comment_on_comment_id=None):
    try:
        comment = Comment.nodes.get(object_uuid=object_uuid)
        parent_object = SBContent.nodes.get(object_uuid=parent_object_uuid)
    except (Comment.DoesNotExist, DoesNotExist, CypherError, IOError) as e:
        raise spawn_comment_notifications.retry(exc=e, countdown=3,
                                                max_retries=None)
    parent_object_type = parent_object.get_child_label().lower()
    to_plebs = [parent_object.owner_username]
    if parent_object_type == "question" or parent_object_type == "solution":
        mission = parent_object.get_mission(parent_object_uuid)
        if mission:
            to_plebs.append(mission['owner_username'])
    task_id = spawn_task(task_func=spawn_notifications, task_param={
        'from_pleb': from_pleb,
        'to_plebs': to_plebs,
        'sb_object': comment.object_uuid,
        'notification_id': notification_id,
        'url': reverse('single_%s_page' % parent_object_type,
                       kwargs={'object_uuid': parent_object.object_uuid}),
        'action_name': "%s %s" % (comment.action_name,
                                  parent_object_type)
    })
    to_plebs = parent_object.get_participating_users()
    comment_on_comment_task = None
    if parent_object.owner_username in to_plebs:
        to_plebs.remove(parent_object.owner_username)
    if to_plebs:
        comment_on_comment_task = spawn_task(
            task_func=spawn_notifications,
            task_param={'from_pleb': from_pleb, 'to_plebs': to_plebs,
                        'sb_object': comment.object_uuid,
                        'notification_id': comment_on_comment_id,
                        'url': reverse(
                            'single_%s_page' % parent_object_type,
                            kwargs={'object_uuid': parent_object.object_uuid}),
                        'action_name': "commented on a %s you commented on"
                                       % parent_object_type})
    return {"comment_on_task": task_id,
            "comment_on_comment_task": comment_on_comment_task}
