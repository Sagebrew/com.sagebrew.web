from celery import shared_task

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from sb_notifications.tasks import spawn_notifications
from sb_base.neo_models import SBContent

from .neo_models import Comment
from .serializers import CommentSerializer

from logging import getLogger
logger = getLogger('loggly_logs')


@shared_task()
def spawn_comment_notifications(object_uuid, parent_object_uuid,
                                from_pleb, notification_id,
                                comment_on_comment_id=None):
    try:
        comment = Comment.nodes.get(object_uuid=object_uuid)
        parent_object = SBContent.nodes.get(object_uuid=parent_object_uuid)
    except (Comment.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise spawn_comment_notifications.retry(exc=e, countdown=3,
                                                max_retries=None)
    comment_data = CommentSerializer(comment).data
    parent_object_type = parent_object.get_child_label().lower()
    # have to do this list comprehension to make it into a JSON
    # serializable object for spawning the task
    spawn_task(task_func=spawn_notifications, task_param={
        'from_pleb': from_pleb,
        'to_plebs': [parent_object.owner_username],
        'sb_object': comment.object_uuid,
        'notification_id': notification_id,
        'url': comment_data['url'],
        'action_name': "%s %s" % (comment.action_name,
                                  parent_object_type)
    })
    if comment_on_comment_id is not None:
        to_plebs = [username[0] for username in
                    parent_object.get_participating_users()]
        if parent_object.owner_username in to_plebs:
            to_plebs.remove(parent_object.owner_username)
        spawn_task(task_func=spawn_notifications, task_param={
            'from_pleb': from_pleb,
            'to_plebs': to_plebs,
            'sb_object': comment.object_uuid,
            'notification_id': comment_on_comment_id,
            'url': comment_data['url'],
            'action_name':
                "also commented on a %s you commented on!" % parent_object_type
        })
    return True
