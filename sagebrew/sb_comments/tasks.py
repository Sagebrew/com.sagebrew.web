from celery import shared_task

from neomodel import DoesNotExist, CypherException

from api.utils import spawn_task
from sb_notifications.tasks import spawn_notifications
from sb_base.neo_models import SBContent

from .neo_models import Comment
from .serializers import CommentSerializer


@shared_task()
def spawn_comment_notifications(object_uuid, parent_object_uuid,
                                from_pleb, notification_id):
    try:
        comment = Comment.nodes.get(object_uuid=object_uuid)
        parent_object = SBContent.nodes.get(object_uuid=parent_object_uuid)
    except (Comment.DoesNotExist, DoesNotExist, CypherException, IOError) as e:
        raise spawn_comment_notifications.retry(exc=e, countdown=3,
                                                max_retries=None)
    comment_data = CommentSerializer(comment).data
    parent_object_type = parent_object.get_child_label().lower()
    spawn_task(task_func=spawn_notifications, task_param={
                'from_pleb': from_pleb,
                'to_plebs': [owner.username for owner in
                             parent_object.owned_by.all()],
                'sb_object': comment.object_uuid,
                'notification_id': notification_id,
                'url': comment_data['url'],
                'action_name': "%s %s" % (comment.action_name,
                                          parent_object_type)
            })