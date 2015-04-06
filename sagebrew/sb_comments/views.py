import pytz
from uuid import uuid1
from datetime import datetime

from django.conf import settings
from django.template.loader import render_to_string

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.utils import spawn_task, request_to_api

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
    comment_form = SaveCommentForm(request.DATA)

    if comment_form.is_valid() is True:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_uuid": comment_form.cleaned_data['object_uuid'],
            "object_type": choice_dict
                [comment_form.cleaned_data['object_type']],
            "content": comment_form.cleaned_data['content'],
            'comment_uuid': str(uuid1()),
            'username': request.user.username
        }
        owner_url = "%s?expand=true" % reverse(
            'user-detail', kwargs={'username': request.user.username},
            request=request)
        comment_owner = request_to_api(
            owner_url, username=request.user.username,
            req_method="GET")
        comment_owner = comment_owner.json()
        profile = comment_owner.pop("profile", None)
        comment_data = {
            "object_uuid": task_data['comment_uuid'],
            "content": comment_form.cleaned_data['content'],
            "vote_type": None,
            "upvotes": 0,
            "downvotes": 0,
            "vote_count": str(0),
            "created": datetime.now(pytz.utc),
            "last_edited_on": datetime.now(pytz.utc),
            "owner": comment_owner,
            "profile": profile,
            "parent_object": request.user.username
        }
        html = render_to_string("sb_comments.html", comment_data)
        spawned = spawn_task(task_func=save_comment_on_object,
                             task_param=task_data)
        if isinstance(spawned, Exception):
            return Response({"detail": "Failed to create comment task"},
                            status=500)
        return Response({
            "detail": "Comment successfully created", "html": html,
            "ids": [task_data['comment_uuid']]},
            status=200)
    else:
        return Response({'detail': "invalid form"}, status=400)
