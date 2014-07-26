import pytz
from json import loads
from urllib2 import HTTPError
from datetime import datetime
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from sb_posts.neo_models import SBPost
#from .tasks import ()
from api.utils import get_post_data, comment_to_garbage
from .utils import (get_post_comments, create_comment_vote, save_comment, edit_comment_util,
                    delete_comment_util)
from .forms import SaveCommentForm, EditCommentForm

#TODO document all possible dictionary returns from api views

#TODO swap decorators and uncomment permissions
#@permission_classes([IsAuthenticated, ])
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_comment_view(request):
    '''
    Creates the comment, connects it to whatever parent it was posted on(posts,
    questions, answers)

    Transition from spawning tasks to calling utils to prevent race conditions.

        ex. User creates comment then deletes before the comment creation task is
        handled by a worker. This is more likely in a distributed worker queue
        when we have multiple celery workers on multiple servers.

    :param request:
    :return:
    '''
    try:
        post_info = get_post_data(request)
        comment_form = SaveCommentForm(post_info)
        if comment_form.is_valid():
            save_comment(**comment_form.cleaned_data)
            return Response({"here": "Comment succesfully created"}, status=200)
        else:
            return Response({'detail': comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                            status=408)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edit_comment(request): #task
    '''
    Allow plebs to edit their comment

    :param request:
    :return:
    '''
    try:
        post_info = get_post_data(request)
        last_edited_on =datetime.now(pytz.utc)
        post_info['last_edited_on'] = last_edited_on
        comment_form = EditCommentForm(post_info)
        if comment_form.is_valid():
            edit_comment_util(**comment_form.cleaned_data)
            return Response({"detail": "Comment succesfully edited"}, status=200)
        else:
            print comment_form.errors
            return Response({'detail': comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({'detail': 'Failed to edit comment'},
                        status=408)
    # do stuff with post_info

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_comment(request): #task
    '''
    Allow plebs to delete their comment

    :param request:
    :return:
    '''
    try:
        comment_info = get_post_data(request)
        comment_to_garbage(comment_info['comment_uuid'])
        return Response({"detail": "Comment deleted"})
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to delete comment"})
    # do stuff with post_info

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
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
@permission_classes((IsAuthenticated,))
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
