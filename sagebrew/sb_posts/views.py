import pytz
import logging
from uuid import uuid1
from datetime import datetime
from urllib2 import HTTPError
from requests import ConnectionError
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from api.utils import (post_to_garbage, spawn_task)
from plebs.neo_models import Pleb
from .neo_models import SBPost
from .tasks import save_post_task
from .utils import (get_pleb_posts)
from .forms import (SavePostForm, DeletePostForm, GetPostForm)

logger = logging.getLogger('loggly_logs')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_post_view(request):
    '''
    Creates the post, connects it to the Pleb which posted it

    :param request:
    :return:
    '''
    try:
        post_data = request.DATA
        if type(post_data) != dict:
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        post_form = SavePostForm(post_data)
        if post_form.is_valid():
            #post_data['content'] = language_filter(post_data['content'])
            post_form.cleaned_data['post_uuid'] = str(uuid1())
            spawn_task(task_func=save_post_task,
                       task_param=post_form.cleaned_data)
            return Response(
                {"action": "filtered", "filtered_content": post_data},
                status=200)
        else:
            return Response(post_form.errors, status=400)
    except (HTTPError, ConnectionError):
        return Response({"detail": "Failed to create post"},
                        status=408)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_user_posts(request):
    '''
    This view gets all of the posts attached to a user's wall.

    :param request:
    :return:
    '''
    html_array = []
    post_data = request.DATA
    post_form = GetPostForm(post_data)
    if post_form.is_valid():
        citizen = Pleb.nodes.get(email=post_form.cleaned_data['email'])
        posts = get_pleb_posts(citizen, post_form.cleaned_data['range_end'],
                           post_form.cleaned_data['range_start'])
        for post in posts:
            post['current_user'] = post_form.cleaned_data['current_user']
            for comment in post['comments']:
                comment['current_user'] = post_form.cleaned_data['current_user']
            html_array.append(render_to_string('sb_post.html', post))
        return Response({'html': html_array}, status=200)
    else:
        return Response(status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_post(request):
    '''
    calls the util which attaches the post and all the comments attached to
    said
    post to the garbage can to be deleted when the garbage can task is run

    :param request:
    :return:
    '''
    try:
        post_data = request.DATA
        if type(post_data) != dict:
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        post_form = DeletePostForm(post_data)
        if post_form.is_valid():
            post_to_garbage(post_form.cleaned_data['post_uuid'])
            return Response({"detail": "Post scheduled to be deleted!"},
                            status=200)
        else:
            return Response({'detail': post_form.errors}, status=400)
    except SBPost.DoesNotExist:
        return Response({"detail": "Post could not be deleted!"}, status=400)