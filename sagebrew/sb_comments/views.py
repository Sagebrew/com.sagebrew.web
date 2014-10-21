import pytz
import logging
from json import dumps
from urllib2 import HTTPError
from datetime import datetime
from requests import ConnectionError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from sb_posts.neo_models import SBPost
from api.utils import get_post_data, comment_to_garbage, spawn_task
from .tasks import (create_vote_comment, submit_comment_on_post,
                    edit_comment_task, flag_comment_task)
from .utils import (get_post_comments)
from .forms import (SaveCommentForm, EditCommentForm, DeleteCommentForm,
                    VoteCommentForm, FlagCommentForm)

logger = logging.getLogger('loggly_logs')

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_comment_view(request):
    '''
    Creates the comment, connects it to whatever parent it was posted on(posts,
    questions, answers)

    Transition from spawning tasks to calling utils to prevent race conditions.

        ex. User creates comment then deletes before the comment creation
        task is
        handled by a worker. This is more likely in a distributed worker queue
        when we have multiple celery workers on multiple servers.

    :param request:
    :return:
    '''
    try:
        comment_info = request.DATA
        if (type(comment_info) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        comment_form = SaveCommentForm(comment_info)
        if comment_form.is_valid():
            spawn_task(task_func=submit_comment_on_post,
                       task_param=comment_form.cleaned_data)
            return Response({"here": "Comment succesfully created"},
                            status=200)
        else:
            return Response({'detail': comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                        status=408)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def edit_comment(request):  # task
    '''
    Allow plebs to edit their comment

    :param request:
    :return:
    '''
    try:
        comment_info = request.DATA
        try:
            comment_info['last_edited_on'] = datetime.now(pytz.utc)
        except TypeError:
            comment_info = comment_info

        if (type(comment_info) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        comment_form = EditCommentForm(comment_info)
        if comment_form.is_valid():
            spawn_task(task_func=edit_comment_task,
                       task_param=comment_form.cleaned_data)
            return Response({"detail": "Comment succesfully edited"},
                            status=200)
        else:
            return Response({'detail': comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({'detail': 'Failed to edit comment'},
                        status=408)
        # do stuff with post_info


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_comment(request):  # task
    '''
    Allow plebs to delete their comment

    :param request:
    :return:
    '''
    try:
        comment_info = request.DATA
        if (type(comment_info) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        comment_form = DeleteCommentForm(comment_info)
        if comment_form.is_valid():
            comment_to_garbage(comment_form.cleaned_data['comment_uuid'])
            return Response({"detail": "Comment deleted"}, status=200)
        else:
            return Response({"detail": comment_form.errors}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to delete comment"})
        # do stuff with post_info


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def vote_comment(request):
    '''
    Allow plebs to up/down vote comments

    :param request:
    :return:
    '''
    try:
        comment_info = request.DATA

        if (type(comment_info) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)

        comment_form = VoteCommentForm(comment_info)

        if comment_form.is_valid():
            spawn_task(task_func=create_vote_comment,
                       task_param=comment_form.cleaned_data)
            return Response({"detail": "Vote created"}, status=200)
        else:
            return Response({'detail': comment_form.errors}, status=400)
    except Exception:
        logger.exception('UnhandledException: ')
        return Response(status=400)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def flag_comment(request):  # task
    '''
    Spawns the task to handle creation of the flag on a comment

    :param request:
    :return:
    '''
    comment_info = request.DATA

    if type(comment_info) != dict:
        return Response({'detail': 'Please Provide a Valid JSON Object'},
                        status=400)

    try:
        comment_form = FlagCommentForm(comment_info)
        if comment_form.is_valid():
            spawn_task(task_func=flag_comment_task, task_param=
                       comment_form.cleaned_data)
            return Response(status=200)
        else:
            return Response(status=400)
    except Exception:
        logger.exception(dumps({"function": flag_comment.__name__,
                                "exception": "UnhandledException: "}))


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def share_comment(request):  # task
    '''
    Allow plebs to share comments with other plebs

    :param request:
    :return:
    '''
    post_info = request.DATA
    if (post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
        # do stuff with post_info


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def reference_comment(request):  # task
    '''
    Allow users to reference comments in other comments/posts/questions/answers

    :param request:
    :return:
    '''
    post_info = request.DATA
    if (post_info["giraffe_contents"] == 3):
        return Response({"comment": "hello"}, status=200)
        # do stuff with post_info


# @permission_classes([IsAuthenticated, ])
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_comments(request):
    '''
    Use to return the most recent/top comments, used as a filter
    to show comments on profile page

    :param request:
    :return:
    '''
    my_post = SBPost.nodes.get(post_id=request.DATA['post_id'])
    comments = get_post_comments(my_post)
    return Response(comments, status=200)