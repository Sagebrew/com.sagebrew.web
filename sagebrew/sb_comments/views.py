import logging
from urllib2 import HTTPError
from requests import ConnectionError
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from neomodel import DoesNotExist

from plebs.neo_models import Pleb
from sb_posts.neo_models import SBPost
from api.utils import comment_to_garbage, spawn_task
from .tasks import save_comment_on_object
from .utils import (get_post_comments)
from .forms import (SaveCommentForm, DeleteCommentForm)

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
        if (type(request.DATA) != dict):
            return Response({"details": "Please Provide a JSON Object"},
                            status=400)
        comment_form = SaveCommentForm(request.DATA)
        if comment_form.is_valid():
            try:
                pleb = Pleb.nodes.get(email=comment_form.
                                      cleaned_data['current_pleb'])
            except (Pleb.DoesNotExist, DoesNotExist):
                return Response({'detail': 'pleb does not exist'}, status=400)
            choice_dict = dict(settings.KNOWN_TYPES)
            task_data = {
                "current_pleb": pleb,
                "object_uuid": comment_form.cleaned_data['object_uuid'],
                "object_type": choice_dict
                    [comment_form.cleaned_data['object_type']],
                "content": comment_form.cleaned_data['content']
            }
            spawn_task(task_func=save_comment_on_object,
                       task_param=task_data)
            return Response({"detail": "Comment succesfully created"},
                            status=200)
        else:
            return Response({'detail': "invalid form"}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"},
                        status=408)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def get_comments(request):
    '''
    Use to return the most recent/top comments, used as a filter
    to show comments on profile page

    :param request:
    :return:
    '''
    try:
        my_post = SBPost.nodes.get(sb_id=request.DATA['sb_id'])
    except (SBPost.DoesNotExist, DoesNotExist):
        return Response(status=400)
    comments = get_post_comments(my_post)
    return Response(comments, status=200)