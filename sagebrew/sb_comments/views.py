from json import loads
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from sb_posts.neo_models import SBPost
#from .tasks import ()
from api.utils import get_post_data
from .utils import (get_post_comments, create_comment_vote, save_comment, edit_comment_util,
                    delete_comment_util)

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
        save_comment(post_info)
        return Response({"here": "Comment succesfully created"}, status=200)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                            status=408)

@api_view(['POST'])
def edit_comment(request): #task
    '''
    Allow plebs to edit their comment

    :param request:
    :return:
    '''
    try:
        post_info = get_post_data(request)
        edit_comment_util(post_info)
        return Response({"detail": "Comment succesfully edited"})
    except(HTTPError, ConnectionError):
        return Response({'detail': 'Failed to edit comment'},
                        status=408)
    # do stuff with post_info

@api_view(['POST'])
def delete_comment(request): #task
    '''
    Allow plebs to delete their comment

    :param request:
    :return:
    '''
    try:
        comment_info = get_post_data(request)
        delete_comment_util(comment_info)
        return Response({"detail": "Comment deleted"})
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to delete comment"})
    # do stuff with post_info

@api_view(['POST'])
def vote_comment(request): #task
    '''
    Allow plebs to up/down vote comments

    :param request:
    :return:
    '''
    try:
        post_info = get_post_data(request)
        print post_info
        create_comment_vote(post_info)
        return Response({"detail": "Vote created"})
    except:
        return Response({"detail": "Vote could not be created"})

@api_view(['POST'])
def flag_comment(request): #task
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
def share_comment(request): #task
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
def reference_comment(request): #task
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
    my_post = SBPost.index.get(post_id=request.DATA['post_id'])
    comments = get_post_comments(my_post)
    return Response(comments, status=200)
