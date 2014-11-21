from uuid import uuid1
from urllib2 import HTTPError
from requests import ConnectionError
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from neomodel import DoesNotExist

from sb_base.utils import defensive_exception
from plebs.neo_models import Pleb
from api.utils import spawn_task
from api.tasks import get_pleb_task
from .tasks import save_comment_on_object
from .forms import (SaveCommentForm)


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
            choice_dict = dict(settings.KNOWN_TYPES)
            task_data = {
                "object_uuid": comment_form.cleaned_data['object_uuid'],
                "object_type": choice_dict
                    [comment_form.cleaned_data['object_type']],
                "content": comment_form.cleaned_data['content'],
                'comment_uuid': str(uuid1())
            }
            pleb_task_data = {
                'email': request.user.email,
                'task_func': save_comment_on_object,
                'task_param': task_data
            }
            spawn_task(task_func=get_pleb_task, task_param=pleb_task_data)
            return Response({"detail": "Comment successfully created"},
                            status=200)
        else:
            return Response({'detail': "invalid form"}, status=400)
    except(HTTPError, ConnectionError):
        return Response({"detail": "Failed to create comment task"}, status=408)
    except Exception as e:
        return defensive_exception(save_comment_view.__name__, e,
                                   Response({"detail": "Internal Server Error"},
                                            status=500))
