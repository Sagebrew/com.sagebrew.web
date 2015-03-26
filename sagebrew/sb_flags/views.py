import pytz
import logging
from datetime import datetime
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .forms import FlagObjectForm
from .tasks import flag_object_task
from api.utils import spawn_task
from sb_docstore.utils import add_object_to_table

logger = logging.getLogger("loggly_logs")


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def flag_object_view(request):
    now = unicode(datetime.now(pytz.utc))
    try:
        flag_object_form = FlagObjectForm(request.DATA)
        valid_form = flag_object_form.is_valid()
    except AttributeError:
        return Response(status=400)
    if valid_form:
        choice_dict = dict(settings.KNOWN_TYPES)
        task_data = {
            "object_uuid": flag_object_form.cleaned_data['object_uuid'],
            "object_type": choice_dict[
                flag_object_form.cleaned_data['object_type']],
            "flag_reason": flag_object_form.cleaned_data['flag_reason'],
            'username': request.user.username,
        }
        spawned = spawn_task(task_func=flag_object_task, task_param=task_data)
        dynamo_data = {
            'parent_object': flag_object_form.cleaned_data['object_uuid'],
            'user': request.user.email,
            'flag_type': flag_object_form.cleaned_data['flag_reason'],
            'time': now
        }
        if isinstance(spawned, Exception):
            return Response({"detail": "server error"}, status=500)
        res = add_object_to_table(table_name="flags", object_data=dynamo_data)
        if isinstance(res, Exception):
            return Response({"detail": "server error"}, status=500)

        return Response({"detail": "success"}, status=200)
    else:
        return Response({"detail": "invalid form"}, status=400)


