import logging
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import VoteObjectForm
from .tasks import vote_object_task
from api.utils import spawn_task
from api.tasks import get_pleb_task
from sb_base.utils import defensive_exception

logger = logging.getLogger('loggly_logs')


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def vote_object_view(request):
    try:
        vote_object_form = VoteObjectForm(request.DATA)
        valid_form = vote_object_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_type": choice_dict[
                vote_object_form.cleaned_data['object_type']],
            "object_uuid": vote_object_form.cleaned_data['object_uuid'],
            "vote_type": vote_object_form.cleaned_data['vote_type']
        }
        pleb_data = {
            'email': request.user.email,
            'task_func': vote_object_task,
            'task_param': task_data
        }
        spawned = spawn_task(task_func=get_pleb_task, task_param=pleb_data)
        if isinstance(spawned, Exception) is True:
            return Response({"detail": "server error"}, status=500)
        return Response({"detail": "success"}, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)
