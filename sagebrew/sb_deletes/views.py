import logging
from json import dumps
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from neomodel import DoesNotExist

from .forms import DeleteObjectForm
from .tasks import delete_object_task
from plebs.neo_models import Pleb
from api.utils import spawn_task

logger = logging.getLogger('loggly_logs')


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def delete_object_view(request):
    try:
        delete_object_form = DeleteObjectForm(request.DATA)
        if delete_object_form.is_valid():
            try:
                current_pleb = Pleb.nodes.get(email=delete_object_form.
                                              cleaned_data['current_pleb'])
            except (Pleb.DoesNotExist, DoesNotExist):
                return Response({"detail": "pleb does not exist"}, status=400)
            choice_dict = dict(settings.KNOWN_TYPES)
            task_data = {
                "current_pleb": current_pleb,
                "object_type": choice_dict[
                    delete_object_form.cleaned_data['object_type']],
                "object_uuid": delete_object_form.cleaned_data['object_uuid']
            }
            spawn_task(task_func=delete_object_task, task_param=task_data)
            return Response(status=200)
    except Exception:
        logger.exception(dumps({"function": delete_object_view.__name__,
                                "exception": "Unhandled Exception"}))
        return Response(status=400)