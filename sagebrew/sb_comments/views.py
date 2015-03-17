import pytz
from uuid import uuid1
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from api.utils import spawn_task
from api.tasks import get_pleb_task
from .tasks import save_comment_on_object
from .forms import (SaveCommentForm)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def save_comment_view(request):
    '''
    Creates the comment, connects it to whatever parent it was posted on(posts,
    questions, solutions)

    Transition from spawning tasks to calling utils to prevent race conditions.

        ex. User creates comment then deletes before the comment creation
        task is
        handled by a worker. This is more likely in a distributed worker queue
        when we have multiple celery workers on multiple servers.

    :param request:
    :return:
    '''
    if (type(request.DATA) != dict):
        return Response({"details": "Please Provide a JSON Object"},
                        status=400)
    try:
        request.DATA['current_pleb'] = request.user.email
        comment_form = SaveCommentForm(request.DATA)
        valid_form = comment_form.is_valid()
    except AttributeError:
        return Response({"details": "Invalid Form"}, status=400)
    if valid_form is True:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_uuid": comment_form.cleaned_data['object_uuid'],
            "object_type": choice_dict
                [comment_form.cleaned_data['object_type']],
            "content": comment_form.cleaned_data['content'],
            'comment_uuid': str(uuid1())
        }
        pleb_task_data = {
            'username': request.user.username,
            'task_func': save_comment_on_object,
            'task_param': task_data
        }
        comment_data = {
            "comments": [{
                "object_uuid": task_data['comment_uuid'],
                "content": comment_form.cleaned_data['content'],
                "up_vote_number": 0,
                "down_vote_number": 0,
                "vote_count": str(0),
                "datetime": datetime.now(pytz.utc),
                "comment_owner": "%s %s"%(request.user.first_name,
                                         request.user.last_name),
                "last_edited_on": datetime.now(pytz.utc)
            }],
            "parent_object": request.user.username
        }
        html = render_to_string("sb_comments.html", comment_data)
        spawned = spawn_task(task_func=get_pleb_task, task_param=pleb_task_data)
        if isinstance(spawned, Exception):
            return Response({"detail": "Failed to create comment task"},
                            status=500)
        return Response({"detail": "Comment successfully created",
                         "html": html},
                        status=200)
    else:
        return Response({'detail': "invalid form"}, status=400)
