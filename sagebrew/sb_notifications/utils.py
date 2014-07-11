import pytz
from uuid import uuid1
from datetime import datetime

from .neo_models import NotificationBase
from sb_posts.neo_models import SBPost
from sb_comments.neo_models import SBComment
from plebs.neo_models import Pleb


def create_notification_post_util(data):
    try:
        from_citizen = Pleb.index.get(email = data['from_pleb'])
        to_citizen = Pleb.index.get(email = data['to_pleb'])
    except Pleb.DoesNotExist:
        return False
    try:
        post = SBPost.index.get(post_id = data['post_id'])
        data.pop('from_pleb', None)
        data.pop('to_pleb', None)
        data['notification_uuid'] = str(uuid1())
        data['notification_about_id'] = data['post_id']
        data.pop('post_id', None)
        data['notification_about'] = 'post'
        notification = NotificationBase(**data)
        notification.save()
        notification.notification_from.connect(from_citizen)
        notification.notification_to.connect(to_citizen)
        notification.save()
        to_citizen.notifications.connect(notification)
        to_citizen.save()
        print "Notification created from post"
        return True
    except SBPost.DoesNotExist:
        print "Notification not created!"
        return False

def create_notification_comment_util(data):
    try:
        from_citizen = Pleb.index.get(email = data['from_pleb'])
        to_citizen = Pleb.index.get(email = data['to_pleb'])
    except Pleb.DoesNotExist:
        return False
    try:
        comment = SBComment.index.get(comment_id = data['comment_id'])
        data.pop('from_pleb', None)
        data.pop('to_pleb', None)
        data['notification_uuid'] = str(uuid1())
        data['notification_about_id'] = data['comment_id']
        data.pop('comment_id', None)
        data['notification_about'] = 'comment'
        notification = NotificationBase(**data)
        notification.notification_from.connect(from_citizen)
        notification.notification_to.connect(to_citizen)
        notification.save()
        to_citizen.notifications.connect(notification)
        to_citizen.save()
        print "Notification created from comment"
    except SBComment.DoesNotExist:
        return
