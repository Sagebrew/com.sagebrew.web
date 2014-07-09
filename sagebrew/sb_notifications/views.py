from uuid import uuid1
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from .neo_models import FriendRequest
from .tasks import create_friend_request_task
from plebs.neo_models import Pleb
from api.utils import get_post_data

@api_view(['POST'])
def create_friend_request(request):
    '''
    calls the task which creates a friend request, it also creates the id for the
    request here

    :param request:
    :return:
    '''
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
    '''
    gets all friend requests attached to the user and returns
    a list of dictionaries of requests
    :param request:
    :return:
    '''
    requests = []
    citizen = Pleb.index.get(email = request.DATA['email'])
    print citizen.email
    friend_requests = citizen.traverse('friend_requests_recieved').where('seen','=', False).run()
    for request in friend_requests:
        request_id = request.friend_request_uuid
        print request_id
        request_sender = request.traverse('request_from').run()[0]
        request_dict = {'from_name':request_sender.first_name+' '+request_sender.last_name, 'from_email': request_sender.email,'request_id': request_id}
        requests.append(request_dict)
    print requests
    return Response(requests, status=200)

@api_view(['POST'])
def respond_friend_request(request):
    '''
    finds the friend request which is attached to both the from and to user
    then, depending on the response type, either attaches the friend relationship
    in each pleb and deletes the request, deletes the request, or lets the friend
    request exist to stop the user from sending more but does not notify the user
    which blocked them that they have a friend request from them.

    :param request:
    :return:
    '''
    request = request.DATA
    print request
    try:
        friend_request = FriendRequest.index.get(friend_request_uuid = request['request_id'])
        to_pleb = friend_request.traverse('request_to').run()[0]
        from_pleb = friend_request.traverse('request_from').run()[0]
    except (FriendRequest.DoesNotExist, Pleb.DoesNotExist):
        print 'Either the pleb no longer exists or the request does not exist'
        return Response(status=408)

    if request['response']=='accept':
        rel1 = to_pleb.friends.connect(from_pleb)
        rel2 = from_pleb.friends.connect(to_pleb)
        rel1.save()
        rel2.save()
        friend_request.delete()
        to_pleb.save()
        from_pleb.save()
        return Response(status=200)
    elif request['response']=='deny':
        friend_request.delete()
        return Response(status=200)
    elif request['response']=='block':
        friend_request.seen = True
        friend_request.response = 'block'
        friend_request.save()
        return Response(status=200)




