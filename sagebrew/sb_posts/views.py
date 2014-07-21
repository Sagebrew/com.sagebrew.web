from uuid import uuid1
from json import loads
from urllib2 import HTTPError
from requests import ConnectionError

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.shortcuts import render

from api.utils import get_post_data, language_filter
from plebs.neo_models import Pleb
from .tasks import save_post_task, edit_post_info_task, delete_post_and_comments
from .utils import (get_pleb_posts, save_post, edit_post_info,
                    create_post_vote)

@api_view(['POST'])
def save_post_view(request):
    '''
    Creates the post, connects it to the Pleb which posted it

    :param request:
    :return:
    '''
    try:
        post_data = get_post_data(request)
        print post_data
        #post_data['content'] = language_filter(post_data['content'])
        post_data['post_id'] = str(uuid1())
        save_post_task.apply_async([post_data,])
        return Response({"action": "filtered", "filtered_content": post_data}, status=200)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create post"},
                            status=408)

@api_view(['POST'])
def get_user_posts(request):
    '''
    If the user wants to create a post this calls the util to create the post

    :param request:
    :return:
    '''
    citizen = Pleb.index.get(email=request.DATA['email'])
    posts = get_pleb_posts(citizen)
    return Response(posts, status=200)

#TODO Only allow users to edit their comment, unless they have admin status
@api_view(['POST'])
def edit_post(request):
    '''
    If the user edits a comment this calls the util to edit the comment

    :param request:
    :return:
    '''
    try:
        post_data = get_post_data(request)
        edit_post_info_task(post_data)
        return Response({"detail": "Post edited!"})
    except:
        return Response({"detail": "Post editing failed!"})

#TODO Only allow users to delete their comment, get flagging system working
@api_view(['POST'])
def delete_post(request):
    try:
        post_data = get_post_data(request)
        delete_post_and_comments.apply_async([post_data,])
        return Response({"detail": "Post deleted!"})
    except:
        return Response({"detail": "Post could not be deleted!"})


@api_view(['POST'])
def vote_post(request):
    try:
        post_data = get_post_data(request)
        create_post_vote(post_data)
        return Response({"detail": "Vote Created!"})
    except:
        return Response({"detail": "Vote could not be created!"})
