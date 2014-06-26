from json import loads
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from .tasks import save_comment
from api.utils import get_post_data

#do bomberman here or in javascript

#TODO swap decorators and uncomment permissions
#@permission_classes([IsAuthenticated, ])
@api_view(['POST'])
def save_comment_view(request):
    '''
    Creates the comment, connects it to whatever parent it was posted on(posts,
    questions, answers)

    :param request:
    :return:
    '''
    try:
        post_info = get_post_data(request)
        save_comment.apply_async([post_info,])
        return Response({"here": "hello world"}, status=200)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                            status=408)

@api_view(['POST'])
def edit_comment(request):
    '''
    Allow plebs to edit their comment

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info

@api_view(['POST'])
def delete_comment(request):
    '''
    Allow plebs to delete their comment

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info

@api_view(['POST'])
def flag_comment(request):
    '''
    Allow plebs to flag comments

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info

@api_view(['POST'])
def vote_comment(request):
    '''
    Allow plebs to up/down vote comments

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info

@api_view(['POST'])
def share_comment(request):
    '''
    Allow plebs to share comments with other plebs

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info

@api_view(['POST'])
def reference_comment(request):
    '''
    Allow users to reference comments in other comments/posts/questions/answers

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info

#@permission_classes([IsAuthenticated, ])
@api_view(['POST'])
def get_comments(request):
    '''
    Use to return the most recent/top comments, used as a filter
    to show comments on profile page

    :param request:
    :return:
    '''
    post_info = get_post_data(request)
    if(post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
    # do stuff with post_info
