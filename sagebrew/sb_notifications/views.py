from uuid import uuid1
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from .tasks import create_friend_request_task
from plebs.neo_models import Pleb
from api.utils import get_post_data

@api_view(['POST'])
def create_friend_request(request):
    try:
        friend_request_data = get_post_data(request)
        friend_request_data['friend_request_uuid'] = str(uuid1())
        create_friend_request_task.apply_async([friend_request_data,])
        return Response({"action": "Friend Request Sent"}, status=200)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to send friend request"}, status=408)

@api_view(['POST'])
def create_notification(request):
    pass

@api_view(['POST'])
def get_notifications(request):
    citizen = Pleb.index.get(email = request.DATA['email'])
    notifications = citizen.traverse('notifications').where('seen', '=', False).run()
    return Response(notifications, status=200)

@api_view(['POST'])
def get_friend_requests(request):
    citizen = Pleb.index.get(email = request.DATA['email'])
    friend_requests = citizen.traverse('friend_requests_recieved').where('seen','=', False).run()
    return Response(friend_requests, status=200)


