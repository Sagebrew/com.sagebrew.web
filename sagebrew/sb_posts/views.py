import pytz
import logging
from uuid import uuid1
from datetime import datetime
from urllib2 import HTTPError
from requests import ConnectionError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.response import Response

from api.utils import (get_post_data, post_to_garbage,
                       spawn_task)
from plebs.neo_models import Pleb
from .neo_models import SBPost
from .tasks import save_post_task, edit_post_info_task
from .utils import (get_pleb_posts, create_post_vote)
from .forms import (SavePostForm, EditPostForm, DeletePostForm, VotePostForm,
                    GetPostForm)



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
        post_data = get_post_data(request)
        if (type(post_data) != dict):
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
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create post"},
                        status=408)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_user_posts(request):
    '''
    If the user wants to create a post this calls the util to create the post

    :param request:
    :return:
    '''
    post_data = get_post_data(request)
    post_form = GetPostForm(post_data)
    if post_form.is_valid():
        citizen = Pleb.index.get(email=post_form.cleaned_data['email'])
        posts = get_pleb_posts(citizen, post_form.cleaned_data['range_end'],
                           post_form.cleaned_data['range_start'])
        return Response(posts, status=200)
    else:
        return Response(status=400)


# TODO Only allow users to edit their comment, unless they have admin status
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edit_post(request):
    '''
    If the user edits a post this calls the util to edit the post

    :param request:
    :return:
        Return Possibilities:
            {'detail': 'edit task spawned'}, status=200
                This will return most of the time, it means that the task has
                been spawned

            {'detail': 'form contains errors', 'errors': form.errors}
                This returns if .is_valid() fails, review django docs
                on form.is_valid() and the variables passed to this function
    '''
    try:
        post_data = get_post_data(request)
        if (type(post_data) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        try:
            post_data['last_edited_on'] = datetime.now(pytz.utc)
        except TypeError:
            post_data = post_data

        post_form = EditPostForm(post_data)
        if post_form.is_valid():
            spawn_task(task_func=edit_post_info_task,
                       task_param=post_form.cleaned_data)
            return Response({'detail': 'edit task spawned'}, status=200)
        else:
            return Response(
                {'detail': 'form contains errors', 'errors': post_form.errors},
                status=400)

    except (HTTPError, ConnectionError):
        return Response({"detail": "Failed Editing"}, status=408)


#TODO Only allow users to delete their comment, get flagging system working
#TODO look into POST to DELETE
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
        post_data = get_post_data(request)
        if (type(post_data) != dict):
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


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vote_post(request):
    '''
    Calls the util which determines what sort of vote will be created also
    determines if the user is allowed to vote

    :param request:
    :return:
    '''
    try:
        post_data = get_post_data(request)
        if (type(post_data) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        post_form = VotePostForm(post_data)
        if post_form.is_valid():
            create_post_vote(**post_form.cleaned_data)
            return Response({"detail": "Vote Created!"}, status=200)
        else:
            return Response({'detail': post_form.errors}, status=400)
    except Exception, e:
        return Response({"detail": "Vote could not be created!",
                         'exception': e})
