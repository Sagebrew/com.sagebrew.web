import pytz
from uuid import uuid1
from datetime import datetime

from .neo_models import FriendRequest, NotificationBase
from sb_posts.neo_models import SBPost

from plebs.neo_models import Pleb

def create_friend_request_util(data):
    try:
        test_request = FriendRequest.index.get(friend_request_uuid=data['friend_request_uuid'])
    except FriendRequest.DoesNotExist:
        from_citizen = Pleb.index.get(email = data['from_pleb'])
        to_citizen = Pleb.index.get(email = data['to_pleb'])
        data.pop('from_pleb', None)
        data.pop('to_pleb', None)
        friend_request = FriendRequest(**data)
        friend_request.save()
        friend_request.request_from.connect(from_citizen)
        friend_request.request_to.connect(to_citizen)
        friend_request.save()
        from_citizen.friend_requests_sent.connect(friend_request)
        from_citizen.save()
        to_citizen.friend_requests_recieved.connect(friend_request)
        to_citizen.save()