# Create your views here.
from django.http import Http404
from django.db import DatabaseError
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (SessionAuthentication,
                                                BasicAuthentication)
from rest_framework.decorators import (api_view, permission_classes,
                                            authentication_classes)
from rest_framework.response import Response


SUBMIT_COMMAND = 'Submit Friend Request'
ACCEPT_COMMAND = 'Accept'
DECLINE_COMMAND = 'Decline'
REMOVE_COMMAND = 'Remove'
COMMAND_LIST = (SUBMIT_COMMAND, ACCEPT_COMMAND,
                DECLINE_COMMAND, REMOVE_COMMAND)


def friend_button_press(req_post, user, friend):
    user_profile = user.profile
    if('friend_request' in req_post):
        if(req_post['friend_request'] == SUBMIT_COMMAND):
            user_profile.friends.send_friend_request(friend)
            return False
    for item in req_post:
        if(req_post.get(item, False) in COMMAND_LIST):
            try:
                command = req_post.get(item, False)
                if(command == ACCEPT_COMMAND):
                    user_profile.friends.accept_friend_request(friend)
                elif(command == DECLINE_COMMAND):
                    user_profile.friends.decline_friend_request(friend)
                elif(command == REMOVE_COMMAND):
                    user_profile.friends.remove_friend(friend)
                return True
            except(User.DoesNotExist, DatabaseError):
                raise Http404
    return False


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes([IsAuthenticated, ])
def friend_request_answer(request):
    feedback = request.DATA
    print feedback["action"]
    print feedback["friend_uid"]
    return_json = {"here": "there"}
    return Response(return_json, status=200)
