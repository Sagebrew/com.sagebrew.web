import logging
from json import dumps
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist

from .forms import FlagObjectForm
from .tasks import flag_object_task
from plebs.neo_models import Pleb
from api.utils import get_object, spawn_task

logger = logging.getLogger("loggly_logs")

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def flag_object_view(request):
    try:
        flag_object_form = FlagObjectForm(request.DATA)
        if flag_object_form.is_valid():
            try:
                pleb = Pleb.nodes.get(email=flag_object_form.
                                      cleaned_data['current_pleb'])
            except (Pleb.DoesNotExist, DoesNotExist):
                return Response({"detail": "pleb does not exist"}, status=401)

            sb_object = get_object(flag_object_form.cleaned_data
                                   ['object_type'],
                                   flag_object_form.cleaned_data['object_uuid'])
            if not object:
                return Response({"detail": "object does not exist"}, status=400)
            task_data = {
                "current_pleb": pleb, "sb_object": sb_object,
                "flag_reason": flag_object_form.cleaned_data['flag_reason']
            }
            spawn_task(task_func=flag_object_task, task_param=task_data)

            return Response({"detail": "success"}, status=200)
        else:
            print flag_object_form.errors
            return Response({"detail": "invalid form"}, status=400)
    except Exception:
        logger.exception(dumps({"function": flag_object_view.__name__,
                                "exception": "UnhandledException: "}))
        return Response(status=400)


